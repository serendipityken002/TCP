import socket
import os
# 创建socket服务

ip = '127.0.0.1'
port = 8080

# 创建socket对象
server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
# 绑定ip和端口
server.bind((ip, port))

# 监听连接
server.listen(2)
print(f"INFO:服务端已启动 {ip}:{port}")
while True:
    try:
        # 等待连接
        conn, addr = server.accept()
        print(f"Connected by {addr}")
    except socket.error as e:
        print(f"ERROR: {e}")
        continue
    if not os.path.exists('download'):
        os.makedirs('download')
    time.sleep(10)
    conn.close()