import serial
import time

class GateController:
    def __init__(self, com_port):
        self.serial_port = serial.Serial(com_port, 9600, timeout=1)
        self.docheckstatus = True
        self.dispstatus = False
        self.door_status = 0  # door is closed

    def open_gate(self):
        if self.serial_port:
            self.serial_port.write(b'~O\n')
            self.door_status = 1
            print('Open the gate.')
            if self.docheckstatus:
                self.check_controller_status()

    def close_gate(self):
        if self.serial_port:
            self.serial_port.write(b'~C\n')
            self.door_status = 0
            print('Close the gate.')
            if self.docheckstatus:
                self.check_controller_status()

    def check_version(self):
        if self.serial_port:
            self.serial_port.write(b'~H\n')
            if self.docheckstatus:
                self.check_controller_status()

    def set_manual_mode(self):
        if self.serial_port:
            self.serial_port.write(b'~M\n')
            if self.docheckstatus:
                self.check_controller_status()

    def set_comm_mode(self):
        if self.serial_port:
            self.serial_port.write(b'~S\n')
            if self.docheckstatus:
                self.check_controller_status()

    def delete(self):
        if self.serial_port:
            self.serial_port.close()

    def check_controller_status(self):
        start_time = time.time()
        max_wait_time = 0.5
        status = []

        while self.serial_port.in_waiting <= 1:
            if time.time() - start_time >= max_wait_time:
                break

        while self.serial_port.in_waiting > 1:
            s = self.serial_port.readline().strip().decode('utf-8')
            if s:
                if self.dispstatus:
                    print(s)
                else:
                    status.append(s)

        return status
