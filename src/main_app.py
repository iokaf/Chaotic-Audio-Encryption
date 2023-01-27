import threading
import random
import sounddevice as sd
import numpy as np

from scipy.io.wavfile import write as write_wav

import sys
from PyQt6.QtCore import QThread, pyqtSignal
from PyQt6.QtWidgets import QApplication, QMainWindow, QVBoxLayout, QPushButton, QWidget


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("PyQt Example")

        # Create buttons
        self.start_button = QPushButton("Start")
        self.stop_button = QPushButton("Stop")

        # Connect buttons to methods
        self.start_button.clicked.connect(self.start_numbers)
        self.stop_button.clicked.connect(self.stop_numbers)

        self.stop_button.setEnabled(False)
        # Create layout and add buttons
        layout = QVBoxLayout()
        layout.addWidget(self.start_button)
        layout.addWidget(self.stop_button)

        # Set layout as central widget
        widget = QWidget()
        widget.setLayout(layout)
        self.setCentralWidget(widget)
        self.stop_flag = False
        self.stop_button.clicked.connect(self.stop_numbers)

        self.recordings = []

    def start_numbers(self):
        self.start_button.setEnabled(False)
        self.stop_button.setEnabled(True)
        self.stop_flag = False
        self.thread = CompleteThread()
        self.thread.start()


    def stop_numbers(self):
        self.start_button.setEnabled(True)
        self.stop_button.setEnabled(False)
        
        self.thread.stop_flag = True

        recording = np.concatenate(self.thread.results["recordings"])
        numbers = np.concatenate(self.thread.results["numbers"])
        encrypted = np.concatenate(self.thread.results["encrypted"])

        print(recording.shape, numbers.shape, encrypted.shape)

        decrypted = np.bitwise_xor(encrypted, numbers[:len(encrypted)])
        # save recording as wav file
        write_wav('test.wav', 4_000, recording)
        write_wav('encrypted.wav', 4_000, encrypted)
        write_wav('decrypted.wav', 4_000, decrypted)


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
        bits = self.random_bits(trajectory)
        ints = self.random_bits_to_int(bits)
        values_dict["numbers"].append(np.expand_dims(np.array(ints, dtype=np.int16).transpose(), 1))

    def run(self):
        while not self.stop_flag:
            rec_thread = threading.Thread(target=self.record)  # , args=(self.results)) #
            rng_thread = threading.Thread(target=self.rng, args=(self.results, 16 * self.rec_time, random.random(), random.random()))

            rec_thread.start()
            rng_thread.start()
            
            rec_thread.join()
            rng_thread.join()

            self.results["encrypted"].append(np.bitwise_xor(self.results["numbers"][-1], self.results["recordings"][-1]))



if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec())