import socket, asyncio, re


store = {}

def put(msg):
    _, key, value, time = msg[0:-1].split(' ')
    time_val = store.setdefault(key, {})
    time_val[time] = float(value)
    return 'ok\n\n'

def get(msg):
    _, key = msg[0:-1].split(' ')
    answer = []
    if key =='*':
        for key in store:
            answer += [f'{key} {value} {time}\n' for time, value in store.get(key, {}).items()]
    else: 
        answer = [f'{key} {value} {time}\n' for time, value in store.get(key, {}).items()]
    return 'ok\n'+ ''.join(answer) + '\n'

msg_patterns = [
    ('put \S+ [0-9]+(\.[0-9]+)? [0-9]+\n', put), 
    ('get \S+\n', get)
]

def analyzer(msg):
    for pattern, function in msg_patterns:
        if re.match(pattern, msg):
            return function(msg)
    return 'error\nwrong command\n\n'


class ClientServerProtocol(asyncio.Protocol):
    def connection_made(self, transport):
        self.transport = transport

    def data_received(self, data):
        msg = data.decode()
        self.transport.write(analyzer(msg).encode())


def run_server(host, port):
    loop = asyncio.get_event_loop()
    coro = loop.create_server(ClientServerProtocol,host, port)
    server = loop.run_until_complete(coro)

    try: loop.run_forever()
    except KeyboardInterrupt: pass

    server.close()
    loop.run_until_complete(server.wait_closed())
    loop.close()