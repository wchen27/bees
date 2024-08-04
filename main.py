import tkinter as tk
from tkinter import ttk, messagebox, filedialog
from subprocess import Popen
import serial.tools.list_ports
from flysong import FlySongApp
import os
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import matplotlib.pyplot as plt

class App:
    def __init__(self, root):
        self.root = root
        self.root.title("Gate Controller and Audio Recorder Configuration")

        # Get the current directory of main.py
        current_dir = os.path.dirname(os.path.abspath(__file__))

        # Available COM ports
        self.available_ports = self.get_com_ports()

        # COM Port configuration for Gate Controller
        self.com_port_label = ttk.Label(root, text="Gate Controller COM Port:")
        self.com_port_label.grid(row=0, column=0, padx=10, pady=10)
        self.com_port_combobox = ttk.Combobox(root, values=self.available_ports)
        self.com_port_combobox.grid(row=0, column=1, padx=10, pady=10)

        # Camera source configuration
        self.camera_source_label = ttk.Label(root, text="Camera Source:")
        self.camera_source_label.grid(row=1, column=0, padx=10, pady=10)
        self.camera_source_entry = ttk.Entry(root)
        self.camera_source_entry.grid(row=1, column=1, padx=10, pady=10)

        # COM Port configuration for Audio Recorder
        self.recorder_com_port_label = ttk.Label(root, text="Audio Recorder COM Port:")
        self.recorder_com_port_label.grid(row=2, column=0, padx=10, pady=10)
        self.recorder_com_port_combobox = ttk.Combobox(root, values=self.available_ports)
        self.recorder_com_port_combobox.grid(row=2, column=1, padx=10, pady=10)

        # Baud rate configuration for Audio Recorder
        self.baud_rate_label = ttk.Label(root, text="Baud Rate:")
        self.baud_rate_label.grid(row=3, column=0, padx=10, pady=10)
        self.baud_rate_entry = ttk.Entry(root)
        self.baud_rate_entry.grid(row=3, column=1, padx=10, pady=10)
        self.baud_rate_entry.insert(0, "9600")

        # Save location configuration for Audio Recorder
        self.save_location_label = ttk.Label(root, text="Save Location:")
        self.save_location_label.grid(row=4, column=0, padx=10, pady=10)
        self.save_location_entry = ttk.Entry(root)
        self.save_location_entry.grid(row=4, column=1, padx=10, pady=10)
        self.save_location_entry.insert(0, current_dir)
        self.browse_button = ttk.Button(root, text="Browse", command=self.browse_directory)
        self.browse_button.grid(row=4, column=2, padx=10, pady=10)

        # Start and Stop buttons for Audio Recorder
        self.start_recorder_button = ttk.Button(root, text="Start Recording", command=self.start_recording)
        self.start_recorder_button.grid(row=5, column=0, padx=10, pady=10)
        self.stop_recorder_button = ttk.Button(root, text="Stop Recording", command=self.stop_recording, state=tk.DISABLED)
        self.stop_recorder_button.grid(row=5, column=1, padx=10, pady=10)

        # Start Gate Controller button
        self.start_gate_controller_button = ttk.Button(root, text="Start Gate Controller", command=self.start_detection)
        self.start_gate_controller_button.grid(row=6, column=0, columnspan=2, padx=10, pady=10)

        # Start both button
        self.start_both_button = ttk.Button(root, text="Start Both", command=self.start_both)
        self.start_both_button.grid(row=7, column=0, columnspan=2, padx=10, pady=10)

        # Textbox for displaying progress
        self.progress_tb = tk.Text(root, height=10, width=50)
        self.progress_tb.grid(row=8, column=0, columnspan=2, padx=10, pady=10)

        # Matplotlib Figure for real-time plotting
        self.fig_canvas = FigureCanvasTkAgg(plt.figure(), master=root)
        self.fig_canvas.get_tk_widget().grid(row=9, column=0, columnspan=3, padx=10, pady=10)

        self.flysong_app = FlySongApp(self.progress_tb, self.fig_canvas)
        self.flysong_app.initialize_plot()

    def get_com_ports(self):
        ports = serial.tools.list_ports.comports()
        return [port.device for port in ports]

    def browse_directory(self):
        directory = filedialog.askdirectory()
        if directory:
            self.save_location_entry.delete(0, tk.END)
            self.save_location_entry.insert(0, directory)

    def start_detection(self):
        com_port = self.com_port_combobox.get()
        camera_source = self.camera_source_entry.get()

        if not com_port:
            messagebox.showerror("Error", "Please select the COM Port for the Gate Controller.")
            return

        if not camera_source.isdigit():
            messagebox.showerror("Error", "Please enter a valid camera source (integer).")
            return

        camera_source = int(camera_source)

        # Run the detect_apriltags.py script with the provided configurations
        Popen(['python', 'detect_apriltags.py', '--camera_source', str(camera_source), '--com_port', com_port])

    def start_recording(self):
        com_port = self.recorder_com_port_combobox.get()
        baud_rate = self.baud_rate_entry.get()
        save_location = self.save_location_entry.get()

        if not com_port:
            messagebox.showerror("Error", "Please select the COM Port for the Audio Recorder.")
            return

        if not baud_rate.isdigit():
            messagebox.showerror("Error", "Please enter a valid baud rate (integer).")
            return

        if not save_location:
            messagebox.showerror("Error", "Please select a save location.")
            return

        baud_rate = int(baud_rate)
        self.flysong_app.start_recording(com_port, baud_rate, save_location)
        self.start_recorder_button.config(state=tk.DISABLED)
        self.stop_recorder_button.config(state=tk.NORMAL)

    def stop_recording(self):
        self.flysong_app.stop_recording()
        self.start_recorder_button.config(state=tk.NORMAL)
        self.stop_recorder_button.config(state=tk.DISABLED)

    def start_both(self):
        self.start_detection()
        self.start_recording()

if __name__ == "__main__":
    root = tk.Tk()
    app = App(root)
    root.mainloop()
