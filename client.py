import time, socket


class ClientError(Exception):
    def __init__(self, text):
        self.text = text


class Client:
    def __init__(self, host, port, timeout = None):
        try:
            self.connection = socket.create_connection((host, port), timeout)
        except socket.error:
            raise ClientError('creating connection failed')
    
    def close(self):
        try: self.connection.close()
        except socket.error:
            raise ClientError('closing connection failed')

    def put(self, name, value, timestamp = None):
        try:
            self.connection.sendall(f'put {name} {value} {timestamp or int(time.time())}\n'.encode()) 
            answer = self.connection.recv(1024).decode()
            if answer == ('error\nwrong command\n\n'):
                raise ClientError('wrong commant')         
        except socket.timeout:
            raise ClientError('time is out')
        except socket.error:
            raise ClientError('socket error')

    def get(self, name):
        try:
            self.connection.sendall(f'get {name}\n'.encode())
            data = (self.connection.recv(1024)).decode()
            data = data.split('\n')
            dict = {}
            try:
                for key, value, time in [data[i].split(' ') for i in range(1, len(data)-2)]:
                    if key in dict.keys():
                        dict[key].append((int(time), float(value)))
                    else: dict[key] = [(int(time), float(value)),]
                for key in dict:
                    dict[key].sort(key = lambda x: x[0])
                return dict
            except Exception:
                raise ClientError('wrong answer')
        except socket.timeout:
            raise ClientError('time is out')
        except socket.error:
            raise ClientError('socket error')