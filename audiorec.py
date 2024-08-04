import serial
import threading
import tkinter as tk
from tkinter import messagebox
import wave
import os
from datetime import datetime

class AudioRecorder:
    def __init__(self, progress_tb):
        self.serial_port = None
        self.thread = None
        self.recording = False
        self.progress_tb = progress_tb
        self.file_path = None

    def start_recording(self, com_port, baud_rate, file_path):
        self.file_path = file_path
        try:
            self.serial_port = serial.Serial(com_port, baud_rate, timeout=1)
            self.recording = True
            self.thread = threading.Thread(target=self.record_data)
            self.thread.start()
        except serial.SerialException as e:
            messagebox.showerror("Error", f"Could not open serial port: {e}")

    def stop_recording(self):
        self.recording = False
        if self.thread:
            self.thread.join()
        if self.serial_port:
            self.serial_port.close()

    def record_data(self):
        # Ensure the directory exists
        if not os.path.exists(self.file_path):
            os.makedirs(self.file_path)

        # Generate a file name based on the current timestamp
        filename = os.path.join(self.file_path, datetime.now().strftime("%Y-%m-%d_%H-%M-%S") + ".wav")
        
        with wave.open(filename, 'w') as wf:
            wf.setnchannels(1)
            wf.setsampwidth(2)
            wf.setframerate(44100)
            
            while self.recording:
                try:
                    data = self.serial_port.readline().strip()
                    if data:
                        wf.writeframes(data)
                        self.progress_tb.insert(tk.END, data + "\n")
                        self.progress_tb.see(tk.END)
                except serial.SerialException as e:
                    self.progress_tb.insert(tk.END, f"Error: {e}\n")
                    self.progress_tb.see(tk.END)
                    break
                except Exception as e:
                    self.progress_tb.insert(tk.END, f"Unexpected error: {e}\n")
                    self.progress_tb.see(tk.END)
                    break
