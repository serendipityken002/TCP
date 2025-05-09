import socket
import os
import struct
import time
import hashlib
import yaml

with open('config.yaml', 'r') as f:
    config = yaml.safe_load(f)

def calculate_md5(file_path):
    """计算文件的 MD5 值"""
    md5 = hashlib.md5()
    with open(file_path, 'rb') as f:
        while chunk := f.read(1024):
            md5.update(chunk)
    return md5.hexdigest()

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
        
        # 发送文件md5码
        file_md5 = calculate_md5(vedio_path)
        server.send(file_md5.encode('utf-8'))

        # 获取断点位置
        checkpoint = int(server.recv(128).decode('utf-8'))
        print(f'服务器已接收 {checkpoint} 字节，继续传输')

        # 发送文件内容
        send_data(vedio_path, server, checkpoint)
        print('文件内容发送成功')

        # 接收服务器回应，校验文件完整性
        op = server.recv(128).decode('utf-8')
        if op == 'true':
            print('经md5核验文件准确无误')
        else:
            print('经md5核验文件有误，建议重新发送')

def online_transfer(server):
    vedio_path = input("请输入视频路径：")
    if not os.path.exists(vedio_path):
        print("文件不存在")
        return
    send_data(vedio_path, server)
    print('文件发送成功')

def main():
    # 定义服务器IP和端口
    ip = config['server']['ip']
    port = config['server']['port']
    server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

    try:
        server.connect((ip, port))
        print("连接成功")
    except Exception as e:
        print("连接失败", e)
        exit(1)
    if config['play']:
        # 在线播放
        online_transfer(server)
    else:
        # 断点续传
        send_file(server)

if __name__ == '__main__':
    main()