import os
import threading
from pathlib import Path
from time import sleep

import serial

from patlite import Patlite

dev_path = "/dev"
dev_lists = []
max_length = 10
save_name = "./serial_data"
data_type = "int"
pattlites = [{"ip": "192.168.10.1", "port": 10000}]


def save_data(path, str_data):
    if Path(path).is_file():
        with open(path, "r") as f:
            for line in f.readlines():
                match data_type:
                    case "int":
                        if int(str_data) == int(line):
                            print(f"Data already exists: {int(str_data)}")
                            return
                    case "str":
                        if str_data in line:
                            print(f"Data already exists: {str_data}")
                            return
    with open(path, "a") as f:
        f.write(f"{str(str_data)}\n")


def convert_to_str(binary_data):
    str_data = binary_data.decode("utf-8")
    split_str_data = str_data.split("\r")
    if len(split_str_data) > 0:
        return split_str_data[0]
    return str_data


def save_per_serial(serial_port, str_data):
    path = f"{serial_port.split("/")[2]}.txt"
    save_data(path, str_data)


def save_per_all(str_data):
    path = f"{save_name}.txt"
    save_data(path, str_data)


def search_patlite(serial_port):
    for patlite in pattlites:
        if patlite["serial"] == serial_port:
            return patlite
    return None


class SerialReaderThreading(threading.Thread):
    def __init__(self, thread_name, serial_port):
        self.thread_name = str(thread_name)
        self.serial_port = serial_port
        threading.Thread.__init__(self)

    def __str__(self):
        return self.thread_name

    def run(self):
        while True:
            readSerial = serial.Serial(self.serial_port, 9600, timeout=1)
            c = readSerial.read(max_length)
            print(f"Read Serial({self.serial_port}): {c}")
            if len(c) > 0:
                patlite_info = search_patlite(self.serial_port)
                print(patlite_info)
                pat = None
                if patlite_info:
                    pat = Patlite(patlite_info["ip"], patlite_info["port"])
                while True:
                    try:
                        if pat:
                            pat.green_light()
                            pat.buzzer(pattern=4)
                        str_data = convert_to_str(c)
                        save_per_serial(serial_port=self.serial_port, str_data=str_data)
                        save_per_all(str_data=str_data)
                        sleep(1)
                        if pat:
                            pat.all_reset()
                        break
                    except Exception as e:
                        if pat:
                            pat.red_light()
                            pat.buzzer(pattern=1)
                        print(f"Error: {e}")
            # # readSerial.close()


# Get usb serial devices in the /dev directory
for f in os.listdir(dev_path):
    if "tty.usbserial" in f:
        dev_lists.append(f)
print(dev_lists)

for dev_list in dev_lists:
    for idx, obj in enumerate(pattlites):
        pattlites[idx]["serial"] = f"{dev_path}/{dev_list}"
    t = SerialReaderThreading(dev_list, f"{dev_path}/{dev_list}")
    t.start()
    # t.join()
