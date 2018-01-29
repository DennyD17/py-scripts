import socket
import pickle

znr = input('Enter znr number: ')
sock = socket.socket()
server = ('localhost', 10000)
sock.connect(server)
sock.sendto(znr.encode(), server)
for key, value in pickle.loads(sock.recv(10000)).items():
    print(str(key) + '..........' + str(value))
