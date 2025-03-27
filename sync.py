import json

import paramiko
import requests
import scp
import sys

args = sys.argv

## args
# 0: Host
# 1: ローカルファイルパス


# サーバへのログイン情報
host = "192.168.161.18"
user = "yonedayuto"
key = "/home/yonedayuto/.ssh/id_rsa"
local_path = "/home/yonedayuto/serial_data.csv"
remote_path = "/home/yonedayuto/serial_data.csv"

if len(args) > 1:
    host = args[1]
if len(args) == 3:
    local_path = args[2]

data = []
write_data = []

# ローカルファイルを開いて内容を読み取る
with open(local_path) as f:
    for line in f.read().splitlines():
        split_line = line.split(",")
        if len(split_line) > 1:
            data.append(split_line[1])
print(data)

# サーバ接続
with paramiko.SSHClient() as sshc:
    sshc.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    sshc.connect(hostname=host, port=22, username=user, key_filename=key)

    # リモートファイルを開いて内容を読み取る
    sftp = sshc.open_sftp()
    with sftp.open(remote_path, mode='r') as remote_file:
        contents = remote_file.read().decode('utf-8')  # または .readlines()

    # 後処理
    sftp.close()
    sshc.close()

    print("ファイルの中身:")
    for content in contents.splitlines():
        split_content = content.split(",")
        if len(split_content) > 1:
            is_exists = False
            for d in data:
                if d == split_content[1]:
                    is_exists = True
                    break
            if not is_exists:
                write_data.append(content)

    # リモートファイルに書き込む
    print("write_data", write_data)
    with open(local_path, mode='a') as f:
        f.write("\n".join(write_data))
    data = []
    with open(local_path, mode='r') as f:
        json_data = {"data": f.read().splitlines(), "version": "v0.0.1"}
    print(json_data)
    try:
        response = requests.post(
            "http://192.168.190.180/data",
            data=json_data,
            headers={"Content-Type": "application/json"},
            timeout=(3.0, 5.0)
        )
        print("Success: post data")
    except:
        print("Error: post data error")
