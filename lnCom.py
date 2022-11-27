
import serial
import threading
from time import sleep


class LoconetUart:
    def __init__(self, port, baud):
        self.received_packet = list()
        self.wait = False
        self.busy = False

        self.ln_uart = serial.Serial()
        self.ln_uart.port = port
        self.ln_uart.baudrate = baud
        self.ln_uart.bytesize = serial.EIGHTBITS
        self.ln_uart.parity = serial.NONE
        self.ln_uart.stopbits = serial.STOPBITS_ONE
        self.ln_uart.timeout = 0.1

        self.alive = threading.Event()
        self.thread = threading.Thread(target=self.receive_process, daemon=True)

    def start(self):
        try:
            self.ln_uart.open()
        except serial.SerialException:
            return False
        else:
            self.alive.set()
            self.thread.start()
        return True

    def stop(self, timeout=3):
        self.alive.clear()
        self.thread.join(timeout)
        self.ln_uart.close()

    def receive_process(self):
        while self.alive.isSet():
            sleep(0.05)
            if not self.wait:
                if self.ln_uart.in_waiting > 1:
                    self.busy = True
                    # print("available:", byte)
                    byte_message = self.ln_uart.read(2)
                    # print("2 byte:", byte_message)
                    message_size = self.get_ln_msg_size(byte_message)
                    # print("message size:", message_size)
                    if message_size > 2:
                        byte_message += self.ln_uart.read(message_size - 2)
                    self.received_packet.append(byte_message)
                    self.busy = False

    def receive_ln_packet(self):
        self.wait = True
        sleep(0.01)
        while self.busy:
            pass
        packet = self.received_packet[0]
        self.received_packet = self.received_packet[1:]
        self.wait = False
        return packet

    def send_ln_packet(self, packet, length):
        while self.busy:
            pass
        self.busy = True
        flag = True
        try:
            for i in range(length):
                self.ln_uart.write(chr(packet[i]))
        except:
            flag = False
        self.busy = False
        return flag

    def available(self):
        return len(self.received_packet)

    @staticmethod
    def get_ln_msg_size(ln_msg):
        return ln_msg[1] if ln_msg[0] & 0x60 == 0x60 else ((ln_msg[0] & 0x60) >> 4) + 2
