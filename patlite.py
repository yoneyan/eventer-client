import socket

base_patlite_data = b'\x58\x58\x53\x00\x00\x06'


class Patlite:
    def __init__(self, ip, port):
        self.ip = ip
        self.port = port

    def send(self, command):
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        s.connect((self.ip, self.port))

        print("Connected!!!!!")

        data = base_patlite_data + command
        # まとめて送信
        s.sendall(data)
        # receive = s.recv(4096).decode()
        # print(receive + "\n")
        # while True:
        #     print("<メッセージを入力してください>")
        #     message = input('>>>')
        #     if not message:
        #         s.send("quit".encode("utf-8"))
        #         break
        #     receive = s.recv(4096).decode()
        #     print(receive + "\n")

        s.close()
        print("END")

    def red_light(self):
        self.send(b'\x01\x09\x09\x09\x09\x09')

    def warning_light(self):
        self.send(b'\x09\x01\x09\x09\x09\x09')

    def green_light(self):
        self.send(b'\x09\x09\x01\x09\x09\x09')

    def buzzer(self, pattern=1):
        match pattern:
            case 1:
                self.send(b'\x09\x09\x09\x09\x09\x01')
            case 2:
                self.send(b'\x09\x09\x09\x09\x09\x02')
            case 3:
                self.send(b'\x09\x09\x09\x09\x09\x03')
            case 4:
                self.send(b'\x09\x09\x09\x09\x09\x04')

    def all_reset(self):
        self.send(b'\x00\x00\x00\x00\x00\x00')


# p = Patlite("192.168.10.1", 10000)
#
# p.warning_light()
# p.buzzer(pattern=4)
