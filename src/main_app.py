import threading
import random
import sounddevice as sd
import numpy as np

from scipy.io.wavfile import write as write_wav
from scipy.io import wavfile

import sys
from PyQt6.QtCore import QThread, pyqtSignal
from PyQt6.QtWidgets import QMainWindow, QVBoxLayout, QPushButton, QWidget, QFileDialog, QInputDialog, QGridLayout


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Chaotic Audio Encryptor")

        self.save_dir = "./"
        self.decrypt_dir = "./"
    
        self.encryption_x0 = 0.0
        self.encryption_r = 0.0
        self.decryption_x0 = 0.0
        self.decryption_r = 0.0

        # Create buttons
        self.start_button = QPushButton("Start")
        self.stop_button = QPushButton("Stop")
        self.select_save_dir = QPushButton("Select Save Directory")
        self.select_decryption_save_dir = QPushButton("Select Decryption Save Directory")
        self.get_encrypted_file = QPushButton("Select Encrypted File")
        self.encryption_keys = QPushButton("Select Encryption Keys")
        self.decrypt_keys = QPushButton("Select Decryption Keys")
        self.decrypt = QPushButton("Decrypt")


        # Connect buttons to methods
        self.start_button.clicked.connect(self.start_numbers)
        self.stop_button.clicked.connect(self.stop_numbers)
        self.select_save_dir.clicked.connect(self.select_save_directory)
        self.get_encrypted_file.clicked.connect(self.select_encrypted_file)
        self.encryption_keys.clicked.connect(self.select_encryption_keys)
        self.decrypt_keys.clicked.connect(self.select_decrypt_keys)
        self.select_decryption_save_dir.clicked.connect(self.select_decryption_save_directory)
        self.decrypt.clicked.connect(self.decrypt_file)
        

        self.stop_button.setEnabled(False)
        # Create layout and add buttons
        layout = QGridLayout()
        layout.addWidget(self.select_save_dir, 0,0)
        layout.addWidget(self.encryption_keys, 1,0)
        layout.addWidget(self.start_button, 2,0)
        layout.addWidget(self.stop_button, 3,0)
        layout.addWidget(self.get_encrypted_file, 0, 1)
        layout.addWidget(self.decrypt_keys, 1, 1)
        layout.addWidget(self.select_decryption_save_dir, 2, 1)
        layout.addWidget(self.decrypt, 3, 1)

        # Set layout as central widget
        widget = QWidget()
        widget.setLayout(layout)
        self.setCentralWidget(widget)
        self.stop_flag = False
        self.stop_button.clicked.connect(self.stop_numbers)

        self.thread = CompleteThread()

        self.recordings = []

    def start_numbers(self):
        self.start_button.setEnabled(False)
        self.stop_button.setEnabled(True)
        self.stop_flag = False
        self.thread.x0 = self.encryption_x0
        self.thread.r = self.encryption_r
        self.thread.start()

    def stop_numbers(self):
        self.start_button.setEnabled(True)
        self.stop_button.setEnabled(False)
        
        self.thread.stop_flag = True

        recording = np.concatenate(self.thread.results["recordings"])
        numbers = np.concatenate(self.thread.results["numbers"])
        encrypted = np.concatenate(self.thread.results["encrypted"])

        decrypted = np.bitwise_xor(encrypted, numbers[:len(encrypted)])
        # save recording as wav file
        write_wav(f"{self.save_dir}test.wav", 4_000, recording)
        write_wav(f"{self.save_dir}encrypted.wav", 4_000, encrypted)
        write_wav(f"{self.save_dir}decrypted.wav", 4_000, decrypted)
    
    def select_save_directory(self):
        self.save_dir = QFileDialog.getExistingDirectory(self, "Select Directory")
        if not self.save_dir.endswith("/"):
            self.save_dir += "/"

    def select_encrypted_file(self):
        self.encrypted_file = QFileDialog.getOpenFileName(self, "Select Encrypted File")[0]
        print(self.encrypted_file)

    def select_encryption_keys(self):
        # Create input dialogs
        self.encryption_x0, ok = QInputDialog.getDouble(self, "Encryption x0", "Enter x0")
        self.encryption_r, ok = QInputDialog.getDouble(self, "Encryption r", "Enter r")

    def select_decrypt_keys(self):
        # Create input dialogs
        self.decryption_x0, ok = QInputDialog.getDouble(self, "Decryption x0", "Enter x0")
        self.decryption_r, ok = QInputDialog.getDouble(self, "Decryption r", "Enter r")

    def decrypt_file(self):
        file_path = self.encrypted_file
        # Read encrypted file
        fs, encrypted = wavfile.read(file_path) # There is an issue with how this is read I think
        encrypted = np.expand_dims(encrypted, axis=1)
        print("Encrypted:", encrypted.shape, np.amin(encrypted), np.amax(encrypted), encrypted.dtype)
        # Create the trajectory
        values_dict = {
            "numbers": [],
        }

        self.thread.rng(
            values_dict, 16 * len(encrypted), self.decryption_x0, self.decryption_r
        )
        
        print(len(encrypted), len(values_dict["numbers"]), len(values_dict["numbers"][0]))
        # Stack lists from values
        key = np.concatenate(values_dict["numbers"])
        print(key.shape)
        # Decrypt the file
        decrypted = np.bitwise_xor(encrypted, key[:len(encrypted)])
        print("Decrypted:", decrypted.shape, np.amin(decrypted), np.amax(decrypted), decrypted.dtype)
        save_path = self.decrypt_dir + "_______decrypted.wav"
        write_wav(save_path, fs, decrypted)
    
    def select_decryption_save_directory(self):
        self.decrypt_dir = QFileDialog.getExistingDirectory(self, "Select Directory")
        if not self.decrypt_dir.endswith("/"):
            self.decrypt_dir += "/"



class CompleteThread(QThread):
    def __init__(self, duration=0.5, fs=4_000):
        super().__init__()
        self.stop_flag = False
        self.all_recordings = []
        self.results = {
            "recordings": [],
            "numbers": [],
            "encrypted": []
        }
        self.duration = duration
        self.fs = fs
        self.rec_time = int(duration * fs)

    def record(self, values_dict=None):
        if values_dict is None:
            values_dict = self.results
        rec = sd.rec(self.rec_time, samplerate=self.fs, channels=1, blocking=True)
        values_dict["recordings"].append((32767 * rec).astype(np.int16))

    
    def map_fun(self, x, r): 
        return r * np.sin(np.pi * x) + r * np.remainder(10 ** 3 * x, 1)

    def trajectory(self, x, r, num_points):
        points = [x]
        for _ in range(num_points):
            x = self.map_fun(x, r)
            points.append(x)
        return points[1:]

    def prbg(self, x):
        return int(np.mod(10 ** 10 * x, 1) > 0.5)

    def random_bits(self, trajectory):
        return list(map(self.prbg, trajectory))

    def random_bits_to_int(self, bits):
        bit_pieces = [bits[i:i+16] for i in range(0, len(bits), 16)]
        ints = [int("".join(map(str, bit_piece)), 2) - 2**15 for bit_piece in bit_pieces]
        return ints


    def rng(self, values_dict, num_points, x0, r):
        trajectory = self.trajectory(x0, r, num_points)
        self.x0 = trajectory[-1] # So we continue encrypting from here
        bits = self.random_bits(trajectory)
        ints = self.random_bits_to_int(bits)
        values_dict["numbers"].append(np.expand_dims(np.array(ints, dtype=np.int16).transpose(), 1))

    def run(self):
        while not self.stop_flag:
            rec_thread = threading.Thread(target=self.record)  # , args=(self.results)) #
            rng_thread = threading.Thread(target=self.rng, args=(self.results, 16 * self.rec_time, self.x0, self.r))

            rec_thread.start()
            rng_thread.start()
            
            rec_thread.join()
            rng_thread.join()

            self.results["encrypted"].append(np.bitwise_xor(self.results["numbers"][-1], self.results["recordings"][-1]))
