import json
import os
import sys
import threading
from datetime import datetime
from pathlib import Path
from time import sleep

import serial
import re

from patlite import Patlite

## args
# 0: 機器名
# 1: configファイルパス
args = sys.argv

device_name = "wheel"
dev_path = "/dev"
dev_lists = []
max_length = 10
save_name = "./serial_data"
data_type = "int"
patlites = [
    {"id": 1, "ip": "192.168.10.1", "port": 10000},
    {"id": 2, "ip": "192.168.10.2", "port": 10000},
    {"id": 3, "ip": "192.168.10.3", "port": 10000},
    {"id": 4, "ip": "192.168.10.4", "port": 10000},
    {"id": 5, "ip": "192.168.10.5", "port": 10000},
]
serial_targets = ["tty.usbserial", "ttySerial", "ttyACM"]
local_servers = []
remote_servers = []

if len(args) > 1:
    device_name = args[0]

if len(args) > 2:
    device_name = args[1]
    with open('config.json', 'r') as f:
        data = json.load(f)
        patlites = data['patlites']
        serial_targets = data["serial_targets"]


def extract_number(text):
    return int(''.join(filter(str.isdigit, text)))


def save_data(path, str_data):
    if Path(path).is_file():
        with open(path, "r") as f:
            for lines in f.read().splitlines():
                match data_type:
                    case "int":
                        if int(str_data) == int(lines[1]):
                            print(f"Data already exists: {int(str_data)}")
                            return
                    case "str":
                        if str_data in lines[1]:
                            print(f"Data already exists: {str_data}")
                            return
    with open(path, "a") as f:
        dt_now = datetime.now()
        f.write(f"{dt_now.strftime('%Y%m%d%H%M%S')},{str(str_data)},{device_name}\n")


def convert_to_str(binary_data):
    str_data = binary_data.decode("utf-8")
    split_str_data = str_data.split("\r")
    if len(split_str_data) > 0:
        return split_str_data[0]
    return str_data


def save_per_serial(serial_port, str_data):
    serial_port_name = serial_port.split("/")[2]
    path = f"{serial_port_name}.csv"
    save_data(path, str_data)


def save_per_all(str_data):
    path = f"{save_name}.csv"
    save_data(path, str_data)


def search_patlite(serial_port):
    for patlite in patlites:
        if patlite["serial"] == serial_port:
            return patlite
    return None


def search_patlite_by_id(id):
    for idx, obj in enumerate(patlites):
        if obj["id"] == int(id):
            return {"index": idx, "patlite": obj}
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
            if len(c) > 0:
                patlite_info = search_patlite(self.serial_port)
                pat = None
                if patlite_info:
                    pat = Patlite(patlite_info["ip"], patlite_info["port"])
                while True:
                    try:
                        str_data = convert_to_str(c)
                        match str_data:
                            case "test":
                                print("test mode")
                                print(f"test> {self.serial_port}")
                                if pat:
                                    pat.green_light()
                                    pat.warning_light()
                                    pat.red_light()
                                    pat.buzzer()
                                    sleep(2)
                                    pat.all_reset()
                                    break
                            case a if re.search("setup\d+", a) is not None:
                                print("setup mode")
                                # patlite関数の配列番号
                                sp = search_patlite_by_id(extract_number(str_data))
                                print(sp)
                                if sp:
                                    idx = sp['index']
                                    patlites[idx]["serial"] = f"{self.serial_port}"
                                    print(
                                        f"Setup Success> Patlite: [{patlites[idx]['id']}]{patlites[idx]['ip']}:{patlites[idx]['port']} -> Serial: {self.serial_port}")
                                break
                            case "debug":
                                print("debug mode")
                                print(f"debug> {self.serial_port}")
                                for obj in patlites:
                                    print(f"debug> Patlite: [{obj['id']}]{obj['ip']}:{obj['port']} -> Serial: {obj['serial']}")
                                break
                            case _:
                                print(f"input> {self.serial_port}: {str_data}")
                                print(patlite_info["ip"], patlite_info["port"])
                                if pat:
                                    pat.green_light()
                                    pat.buzzer(pattern=4)
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
                        break
            # # readSerial.close()


# Get usb serial devices in the /dev directory
for f in os.listdir(dev_path):
    for text in serial_targets:
        if text in f:
            dev_lists.append(f)

for idx, obj in enumerate(patlites):
    dev_list = dev_lists.pop()
    patlites[idx]["serial"] = f"{dev_path}/{dev_list}"
    print(f"Patlite: [{obj['id']}]{obj['ip']}:{obj['port']} -> Serial: {dev_list}")
    t = SerialReaderThreading(dev_list, f"{dev_path}/{dev_list}")
    t.start()
