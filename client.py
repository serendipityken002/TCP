import socket
import os
# 创建socket服务

ip = '127.0.0.1'
port = 8080

# 创建socket对象
server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

try:
    server.connect((ip, port))
    print("连接成功")
except Exception as e:
    print("连接失败", e)
    exit(1)

# 发送数据
while True:
    # 发送数据
    vedio_path = input("请输入视频路径：")

