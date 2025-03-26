import paramiko
import scp
import sys

args = sys.argv

## args
# 0: Host
# 1: ローカルファイルパス


# サーバへのログイン情報
host = "192.168.161.18"
user = "yonedayuto"
key = "/Users/y-yoneda/.ssh/all-hands"
local_path = "/Users/y-yoneda/github/eventer-client/serial_data.csv"
remote_path = "/opt/eventer-client/serial_data.csv"
print(len(args))
if len(args) > 1:
    host = args[0]
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

    # SCPによるコピー処理
    # with scp.SCPClient(sshc.get_transport()) as scpc:
    #     scpc.get(remote_path=target_path, local_path=out_path)
    # リモートファイルを開いて内容を読み取る
    sftp = sshc.open_sftp()
    with sftp.open(remote_path, mode='r') as remote_file:
        contents = remote_file.read().decode('utf-8')  # または .readlines()

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
    print(write_data)
    with open(local_path, mode='a') as f:
        f.write("\n".join(write_data))

    # 後処理
    sftp.close()
    sshc.close()
