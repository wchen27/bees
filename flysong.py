import serial
import threading
import tkinter as tk
from tkinter import messagebox
import pyaudio
import wave
import os
from datetime import datetime
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import numpy as np

class FlySongApp:
    def __init__(self, progress_tb, fig_canvas):
        self.serial_port = None
        self.thread = None
        self.recording = False
        self.audio_stream = None
        self.p = None
        self.frames = []
        self.progress_tb = progress_tb
        self.fig_canvas = fig_canvas
        self.line = None

    def initialize_plot(self):
        self.fig, self.ax = plt.subplots()
        self.ax.set_ylim(-32768, 32767)
        self.ax.set_xlim(0, 1024)
        self.line, = self.ax.plot(np.random.rand(1024))

        self.fig_canvas.figure = self.fig
        self.fig_canvas.draw()

    def start_recording(self, com_port, baud_rate, save_location):
        self.save_location = save_location
        try:
            self.serial_port = serial.Serial(com_port, baud_rate, timeout=1)
            self.recording = True
            self.thread = threading.Thread(target=self.record_data)
            self.thread.start()

            # Initialize PyAudio
            self.p = pyaudio.PyAudio()
            self.audio_stream = self.p.open(format=pyaudio.paInt16,
                                            channels=1,
                                            rate=44100,
                                            input=True,
                                            frames_per_buffer=1024,
                                            stream_callback=self.audio_callback)
        except serial.SerialException as e:
            messagebox.showerror("Error", f"Could not open serial port: {e}")

    def stop_recording(self):
        self.recording = False
        if self.thread:
            self.thread.join()
        if self.serial_port:
            self.serial_port.close()
        if self.audio_stream:
            self.audio_stream.stop_stream()
            self.audio_stream.close()
        if self.p:
            self.p.terminate()

        self.save_audio()

    def record_data(self):
        while self.recording:
            try:
                data = self.serial_port.readline().decode('utf-8').strip()
                if data:
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

    def audio_callback(self, in_data, frame_count, time_info, status):
        self.frames.append(in_data)
        audio_data = np.frombuffer(in_data, dtype=np.int16)
        self.line.set_ydata(audio_data)
        self.fig_canvas.draw()
        return (in_data, pyaudio.paContinue)

    def save_audio(self):
        if not os.path.exists(self.save_location):
            os.makedirs(self.save_location)
        filename = os.path.join(self.save_location, datetime.now().strftime("%Y-%m-%d_%H-%M-%S") + ".wav")
        wf = wave.open(filename, 'wb')
        wf.setnchannels(1)
        wf.setsampwidth(self.p.get_sample_size(pyaudio.paInt16))
        wf.setframerate(44100)
        wf.writeframes(b''.join(self.frames))
        wf.close()
