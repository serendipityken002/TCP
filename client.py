import socket
import os
import struct
import time

def send_data(file_path, server, checkpoint=0):
    fp = open(file_path, 'rb')
    fp.seek(checkpoint)
    while True:
        data = fp.read(1024)
        if not data:
            break
        server.send(data)
    fp.close()

def send_file(server):
    while True:
        vedio_path = input("请输入视频路径：")
        if not os.path.exists(vedio_path):
            print("文件不存在")
            continue

        # 发送文件头部信息
        filename = os.path.basename(vedio_path)
        file_size = os.path.getsize(vedio_path)
        filehead = struct.pack('128sl', filename.encode('utf-8'), file_size)
        server.send(filehead)
        print('文件头部信息发送成功')
        
        # 发送文件内容
        send_data(vedio_path, server)
        print('文件内容发送成功')

def main():
    # 定义服务器IP和端口
    ip = '127.0.0.1'
    port = 8080
    server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

    try:
        server.connect((ip, port))
        print("连接成功")
    except Exception as e:
        print("连接失败", e)
        exit(1)
    send_file(server)

if __name__ == '__main__':
    main()