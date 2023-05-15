import socket
import threading
import time
import queue
import pickle

class Multi_Server:
    def __init__(self):
        self.host_ip = socket.gethostbyname(socket.gethostname())
        self.port = 12000
        self.msg_queue = queue.Queue()
        self.socket_array = []
        self.server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)       # 방금 사용하고 close한 port를 즉시 다시 사용할 수 있다.
        self.server_socket.bind((self.host_ip, self.port))
        self.server_socket.listen(6)
        self.is_password = False
        self.password = ""
        self.random_request = False
    
    
    def single_send(self, index, msg):
        self.socket_array[index].send(pickle.dumps(msg))
    
    
    def multi_send(self):
        while True:
            if self.msg_queue.empty() == True:
                time.sleep(0.2)
            else:
                M = self.msg_queue.get()
                
                for i in range(len(self.socket_array)):
                    self.socket_array[i].send(pickle.dumps(M))
    
    
    def receive(self, client_socket):
        while True:
            msg = pickle.loads(client_socket.recv(4096))
            
            if isinstance(msg,dict):
                self.msg_queue.put(msg)
            else:
                if msg == "deleted":
                    break
                elif msg[0:6] == "random":
                    if self.random_request == False:
                        self.random_request = True
                        
                        num = int(msg[15:])
                else:
                    self.msg_queue.put(msg)
    
    def handle_client(self):
        while True:
            connect_socket, addr = self.server_socket.accept()
            if self.is_password == True:
                connect_socket.send(pickle.dumps("password"))
                thread = threading.Thread(target=self.password_receive, args=(connect_socket, addr,))
                thread.daemon = True
                thread.start()
            else:
                self.authenticated_client(connect_socket, addr)
            
    def password_receive(self, connect_socket, addr):
        msg = pickle.loads(connect_socket.recv(1024))
        
        if msg == self.password:
            self.authenticated_client(connect_socket, addr)
        else:
            connect_socket.send(pickle.dumps("wrong"))
    
    def authenticated_client(self, connect_socket, addr):
        print(f"{addr} 연결됨")
        connect_socket.send(pickle.dumps("authenticated"))
        
        self.socket_array.append(connect_socket)
            
        thread_receive = threading.Thread(target=self.receive, args=(connect_socket,))
        thread_receive.daemon = True
        thread_receive.start()
            
    def server_start(self):
        thread_handle_client = threading.Thread(target=self.handle_client)
        thread_handle_client.daemon = True
        thread_handle_client.start()
                    
        thread_send = threading.Thread(target=self.multi_send)
        thread_send.daemon = True
        thread_send.start()
