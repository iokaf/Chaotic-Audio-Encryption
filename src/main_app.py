import threading
import random
# import sounddevice as sd
import pyaudio
import numpy as np

from scipy.io.wavfile import write as write_wav
from scipy.io import wavfile

import sys
from PyQt6.QtCore import QThread, pyqtSignal
from PyQt6.QtWidgets import (
    QMainWindow, QVBoxLayout, QPushButton, QWidget, QFileDialog, QInputDialog, 
    QGridLayout, QLabel, QDialog
)

class HelpDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Help")
        
        layout = QVBoxLayout()

        title = QLabel("Chaotic Audio Encryptor")
        font = title.font()
        font.setPointSize(20)
        font.setBold(True)
        title.setFont(font)
        layout.addWidget(title)

        developers = QLabel("Developer: Dr. Ioannis Kafetzis")
        layout.addWidget(developers)
        contact = QLabel("Contact: ioanniskaf@gmail.com")
        layout.addWidget(contact)
        


        encrypt_instructions = QLabel("Instructions")
        font = encrypt_instructions.font()
        font.setPointSize(20)
        font.setBold(True)
        encrypt_instructions.setFont(font)
        layout.addWidget(encrypt_instructions)

        

        general = QLabel("Please turn your keyboard in English. \n \n")
        layout.addWidget(general)

        encrypt_instructions = QLabel("Encryption")
        font = encrypt_instructions.font()
        font.setPointSize(15)
        font.setBold(True)
        encrypt_instructions.setFont(font)
        layout.addWidget(encrypt_instructions)


        encrypt_step_1 = QLabel("1. Select the directory and filename for the encrypted file.")
        layout.addWidget(encrypt_step_1)

        encrypt_step_2 = QLabel("2. Select encryption keys and add the keys.")
        layout.addWidget(encrypt_step_2)

        encrypt_step_3 = QLabel("3. Click the start button to start recording.")
        layout.addWidget(encrypt_step_3)

        encrypt_step_4 = QLabel("4. Click the stop button to stop recording.")
        layout.addWidget(encrypt_step_4)

        encrypt_step_5 = QLabel("5. The encrypted file will be saved in the selected directory. \n \n ")
        layout.addWidget(encrypt_step_5)


        decrypt_instructions = QLabel("Decryption")
        font = decrypt_instructions.font()
        font.setPointSize(15)
        font.setBold(True)
        decrypt_instructions.setFont(font)
        layout.addWidget(decrypt_instructions)

        decrypt_step_1 = QLabel("1. Select the encrypted file.")
        layout.addWidget(decrypt_step_1)

        decrypt_step_2 = QLabel("2. Select the decryption keys. They should be the same as the ones used for encryption.")
        layout.addWidget(decrypt_step_2)

        decrypt_step_3 = QLabel("3. Select the directory and filename to save  the decrypted file.")
        layout.addWidget(decrypt_step_3)

        decrypt_step_4 = QLabel("4. Click the decrypt button to decrypt the file.\n \n")
        layout.addWidget(decrypt_step_4)
        
        # Add a title label with information about hte software
        # Make the title bold and bigger

        title = QLabel("Chaotic Map and PRBG")
        font = title.font()
        font.setPointSize(20)
        font.setBold(True)
        title.setFont(font)

        layout.addWidget(title)

        map_used = QLabel("This application uses the chaotic map: x_n+1 = r * sin(pi * x_n) + r * (10^3 * x_n) % 1")
        layout.addWidget(map_used)

        prbg_used = QLabel("The pseudo random bit generator is: bit_n = 10^10 * x_n % 1 > 0.5 \n \n")
        layout.addWidget(prbg_used)

        title = QLabel("Citation")
        font = title.font()
        font.setPointSize(20)
        font.setBold(True)
        title.setFont(font)
        layout.addWidget(title)

        authors = QLabel("Kafetzis, I., Volos, C., Nistazakis, H. E., Goudos, S., & Bardis, N. G. (2023, June)")
        citation = QLabel("A Real-time Chaos-based Audio Encryption Scheme.")
        journal = QLabel("In 2023 7th International Conference on Advanced Information Systems and Engineering (ICAISE) (pp. 1-5). IEEE.")
        doi = QLabel("DOI: 10.1109/MOCAST57943.2023.10176599")

        layout.addWidget(authors)
        layout.addWidget(citation)
        layout.addWidget(journal)
        layout.addWidget(doi)




        


        self.setLayout(layout)

class MainWindow(QMainWindow):
    def __init__(self, freq=4_000):
        super().__init__()
        self.setWindowTitle("Chaotic Audio Encryptor")

        self.freq = freq

        self.save_dir = "./"
        self.decrypt_dir = "./"
    
        self.encryption_x0 = 0.0
        self.encryption_r = 0.0
        self.decryption_x0 = 0.0
        self.decryption_r = 0.0
        self.encrypt_filename = "encrypted.wav"
        self.decrypt_filename = "decrypted.wav"

        # Create buttons
        self.start_button = QPushButton("Start")
        self.stop_button = QPushButton("Stop")
        self.select_save_dir = QPushButton("Select Save Directory")
        self.select_decryption_save_dir = QPushButton("Select Decryption Save Directory")
        self.get_encrypted_file = QPushButton("Select Encrypted File")
        self.encryption_keys = QPushButton("Select Encryption Keys")
        self.decrypt_keys = QPushButton("Select Decryption Keys")
        self.decrypt = QPushButton("Decrypt")
        self.help = QPushButton("Help")
        

        # Connect buttons to methods
        self.start_button.clicked.connect(self.start_recording)
        self.stop_button.clicked.connect(self.stop_recording)
        self.select_save_dir.clicked.connect(self.select_save_directory)
        self.get_encrypted_file.clicked.connect(self.select_encrypted_file)
        self.encryption_keys.clicked.connect(self.select_encryption_keys)
        self.decrypt_keys.clicked.connect(self.select_decrypt_keys)
        self.select_decryption_save_dir.clicked.connect(self.select_decryption_save_directory)
        self.decrypt.clicked.connect(self.decrypt_file)
        self.help.clicked.connect(self.show_help)

        self.stop_button.setEnabled(False)
        # Create layout and add buttons
        layout = QGridLayout()
        layout.addWidget(self.select_save_dir, 1,0)
        layout.addWidget(self.encryption_keys, 2,0)
        layout.addWidget(self.start_button, 3,0)
        layout.addWidget(self.stop_button, 4,0)
        layout.addWidget(self.get_encrypted_file, 1, 1)
        layout.addWidget(self.decrypt_keys, 2, 1)
        layout.addWidget(self.select_decryption_save_dir, 3, 1)
        layout.addWidget(self.decrypt, 4, 1)

        # Set layout as central widget
        widget = QWidget()
        widget.setLayout(layout)
        self.setCentralWidget(widget)
        self.stop_flag = False
        # Add the help button
        layout.addWidget(self.help, 5, 0, 1, 2)

        # On the top add a title widget with the name "Chaotic Audio Encryptor"
        # Make the font size bigger and bold
        title = QLabel("Chaotic Audio Encryptor")
        font = title.font()
        font.setPointSize(20)

        font.setBold(True)
        title.setFont(font)
        layout.addWidget(title, 0, 0, 1, 2)



        self.thread = CompleteThread(fs=self.freq)

        self.recordings = []

    def show_help(self):
        """Shows a help dialog"""
        help_dialog = HelpDialog(self)
        help_dialog.exec()




    def start_recording(self):
        """Initiates the recording thread and disables the start button"""
        self.start_button.setEnabled(False)
        self.stop_button.setEnabled(True)
        # Reset the dictionary
        self.thread.results = {
            "recordings": [],
            "numbers": [],
            "encrypted": [],
        }
        
        self.stop_flag = False
        self.thread.x0 = self.encryption_x0
        self.thread.r = self.encryption_r
        self.thread.start()

    def stop_recording(self):
        """Stops the recording thread and enables the start button"""
        self.start_button.setEnabled(True)
        self.stop_button.setEnabled(False)
        
        self.thread.stop_flag = True

        recording = np.concatenate(self.thread.results["recordings"])
        numbers = np.concatenate(self.thread.results["numbers"])
        encrypted = np.concatenate(self.thread.results["encrypted"])

        decrypted = np.bitwise_xor(encrypted, numbers[:len(encrypted)])

        # For debugging, allows to save the original recording
        # write_wav(f"{self.save_dir}test.wav", self.freq, recording)

        # Save the encrypted file
        write_wav(f"{self.save_dir}{self.encrypt_filename}", self.freq, encrypted)

    def select_save_directory(self):
        """Opens a dialog to select the save directory and select filename"""
        self.save_dir = QFileDialog.getExistingDirectory(self, "Select Directory")
        self.encrypt_filename = QInputDialog.getText(self, "Encryption Filename", "Enter filename")[0]

        if not self.save_dir.endswith("/"):
            self.save_dir += "/"

        if self.encrypt_filename == "":
            self.encrypt_filename = "encrypted.wav"

        if not self.encrypt_filename.endswith(".wav"):
            self.encrypt_filename += ".wav"


    def select_encrypted_file(self):
        """Opens a dialog to select the encrypted file"""
        self.encrypted_file = QFileDialog.getOpenFileName(self, "Select Encrypted File")[0]
        

    def select_encryption_keys(self):
        """Opens a dialog to select the encryption keys"""
        # Create input dialogs
        self.encryption_x0, ok = QInputDialog.getDouble(self, "Encryption x0", "Enter x0", decimals=16)
        self.encryption_r, ok = QInputDialog.getDouble(self, "Encryption r", "Enter r", decimals=16)

    def select_decrypt_keys(self):
        """Opens a dialog to select the decryption keys"""
        # Create input dialogs
        self.decryption_x0, ok = QInputDialog.getDouble(self, "Decryption x0", "Enter x0", decimals=16)
        self.decryption_r, ok = QInputDialog.getDouble(self, "Decryption r", "Enter r", decimals=16)

    def decrypt_file(self):
        """Decrypts the file"""
        file_path = self.encrypted_file
        # Read encrypted file
        fs, encrypted = wavfile.read(file_path) # There is an issue with how this is read I think

        # Create the trajectory
        values_dict = {
            "numbers": [],
        }

        self.thread.rng(
            values_dict, 16 * len(encrypted), self.decryption_x0, self.decryption_r
        )

        # Stack lists from values
        key = np.concatenate(values_dict["numbers"])
        # Decrypt the file

        decrypted = np.bitwise_xor(encrypted, key[:len(encrypted)])
        save_path = self.decrypt_dir + self.decrypt_filename
        write_wav(save_path, fs, decrypted)
    
    def select_decryption_save_directory(self):
        """Opens a dialog to select the save directory and select filename"""
        self.decrypt_dir = QFileDialog.getExistingDirectory(self, "Select Directory")
        self.decrypt_filename = QInputDialog.getText(self, "Decryption Filename", "Enter filename")[0]

        if self.decrypt_filename == "":
            self.decrypt_filename = "decrypted.wav"

        if not self.decrypt_filename.endswith(".wav"):
            self.decrypt_filename += ".wav"

        if not self.decrypt_dir.endswith("/"):
            self.decrypt_dir += "/"



class CompleteThread(QThread):
    def __init__(self, fs, duration=0.5):
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

        # Initialize pyaudio object 
        self.p = pyaudio.PyAudio()
        self.stream = None


    def record(self, values_dict=None):
        """Records a single chunk of audio and appends it to the results dictionary"""
        if values_dict is None:
            values_dict = self.results
        
        rec = self.stream.read(self.rec_time)
        rec = np.frombuffer(rec, dtype=np.int16)

        values_dict["recordings"].append(rec) 

    
    def map_fun(self, x, r): 
        """The chaotic map iteration."""
        return r * np.sin(np.pi * x) + r * np.remainder(10 ** 3 * x, 1)

    def trajectory(self, x, r, num_points):
        """Creates a trajectory of points from the chaotic map.
        
        Args:
            x (float): The initial value.
            r (float): The parameter of the chaotic map.
            num_points (int): The number of points to generate.
        
        Returns:
            list: The list of points.
        """
        points = [x]
        for _ in range(num_points):
            x = self.map_fun(x, r)
            points.append(x)
        return points[1:]

    def prbg(self, x):
        """Generates a pseudo random bit from a float.
        
        Args:
            x (float): The float to generate the bit from.

        Returns:
            int: The bit.
        """
        return int(np.mod(10 ** 10 * x, 1) > 0.5)

    def random_bits(self, trajectory):
        """Generates a list of random bits from a trajectory.

        Args:
            trajectory (list): The trajectory to generate the bits from.

        Returns:
            list: The list of bits.
        """
        return list(map(self.prbg, trajectory))

    def random_bits_to_int(self, bits):
        """Converts a list of bits to a list of ints.
        Args:
            bits (list): The list of bits.

        Returns:
            list: The list of ints.
        """
        bit_pieces = [bits[i:i+16] for i in range(0, len(bits), 16)]
        ints = [int("".join(map(str, bit_piece)), 2) - 2**15 for bit_piece in bit_pieces]
        return ints


    def rng(self, values_dict, num_points, x0, r):
        """Generates a list of random numbers from a trajectory.

        Args:
            values_dict (dict): The dictionary to append the numbers to.
            num_points (int): The number of points to generate.
            x0 (float): The initial value.
            r (float): The parameter of the chaotic map.
        """
        trajectory = self.trajectory(x0, r, num_points)
        self.x0 = trajectory[-1] # So we continue encrypting from here
        bits = self.random_bits(trajectory)
        ints = self.random_bits_to_int(bits)
        values_dict["numbers"].append(np.array(ints, dtype=np.int16))

    def run(self):
        """Runs the thread
        
        Description:
            This thread records audio and generates random numbers at the same time.
            It then encrypts the audio and appends it to the results dictionary.
        """

        if self.stream is None:
            self.stream = self.p.open(
                format=pyaudio.paInt16,
                channels=1,
                rate=self.fs,
                input=True,
            )
        while not self.stop_flag:
            rec_thread = threading.Thread(target=self.record) 
            rng_thread = threading.Thread(target=self.rng, args=(self.results, 16 * self.rec_time, self.x0, self.r))

            rec_thread.start()
            rng_thread.start()
            
            rec_thread.join()
            rng_thread.join()

            self.results["encrypted"].append(np.bitwise_xor(self.results["numbers"][-1], self.results["recordings"][-1]))
        else:
            self.stream.stop_stream()
            self.stream.close()
            