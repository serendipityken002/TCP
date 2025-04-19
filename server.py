import socket
import os
import threading
import struct

def handle_client(conn):
    while True:
        # 接收文件头
        filehead = conn.recv(128 + 4)
        filename, filesize = struct.unpack('128sl', filehead)
        filename = filename.decode('utf-8')
        print(f'文件名：{filename}，文件大小：{filesize}')

        # 判断是否需要断点续传
        filepath = f'download/{filename}'.strip('\x00')  
        checkoutpoint = 0
        if os.path.exists(filepath):
            checkoutpoint = os.path.getsize(filepath)
        conn.send(str(checkoutpoint).encode('utf-8'))
        print(f"已接收 {checkoutpoint} 字节，等待继续接收")

        # 接收文件内容  
        with open(filepath, 'ab') as fp:
            received_size = checkoutpoint
            while received_size < filesize:
                data = conn.recv(1024)
                if not data:
                    break
                fp.write(data)
                received_size += len(data)
                progress = 100 * received_size / filesize
                print(f'\r文件接收中{progress:.2f}%', end='', flush=True)
            
        print()  # 换行，避免后续输出覆盖进度条
        if received_size == filesize:
            print(f'文件{filename}接收完成')
        else:
            print(f'文件{filename}接收失败，可能数据丢失')

def main():
    ip = '127.0.0.1'
    port = 8080
    server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server.bind((ip, port))
    server.listen(3)
    print(f"INFO:服务端已启动 {ip}:{port}")
    if not os.path.exists('download'):
        os.makedirs('download')

    while True:
        try:
            # 等待连接
            conn, addr = server.accept()
            print(f"客户端已连接: {addr}")
            threading.Thread(target=handle_client, args=(conn,)).start()
        except socket.error as e:
            print(f"ERROR: {e}")
            continue

if __name__ == '__main__':
    main()