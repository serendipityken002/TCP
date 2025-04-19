import socket
import os
import threading
import struct
import hashlib

def calculate_md5(file_path):
    """计算文件的 MD5 值"""
    md5 = hashlib.md5()
    with open(file_path, 'rb') as f:
        while chunk := f.read(1024):
            md5.update(chunk)
    return md5.hexdigest()

def handle_client(conn):
    try:
        while True:
            # 接收文件头
            filehead = conn.recv(128 + 4)
            filename, filesize = struct.unpack('128sl', filehead)
            filename = filename.decode('utf-8')
            print(f'文件名：{filename}，文件大小：{filesize}')

            # 接收文件md5码
            client_md5 = conn.recv(128).decode('utf-8')

            # 判断是否需要断点续传
            filepath = f'download/{filename}'.strip('\x00')  
            checkoutpoint = 0
            if os.path.exists(filepath):
                checkoutpoint = os.path.getsize(filepath)
            conn.send(str(checkoutpoint).encode('utf-8'))
            print(f"已接收 {checkoutpoint} 字节，等待继续接收")

            # 检查文件是否损坏
            if checkoutpoint == filesize:
                print('文件已存在，跳过接收')
                server_md5 = calculate_md5(filepath)
                if server_md5 == client_md5:
                    conn.send('true'.encode('utf-8'))
                    print('文件md5码校验成功')
                else:
                    conn.send('false'.encode('utf-8'))
                    print('error:文件md5码校验失败!')
                continue
            elif checkoutpoint > filesize:
                print('error:文件已损坏，重新接收')
                os.remove(filepath)
                conn.send('false'.encode('utf-8'))
                continue

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
            server_md5 = calculate_md5(filepath)
            if server_md5 == client_md5:
                conn.send('true'.encode('utf-8'))
                print('文件md5码校验成功')
            else:
                conn.send('false'.encode('utf-8'))
                print('error:文件md5码校验失败!')

    except Exception as e:
        print(f"客户端连接异常断开{e}")
    finally:
        conn.close()
        print("连接已关闭")

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