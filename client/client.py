# coding: utf-8

import socket

hote = "localhost"
port = 15555

client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
client.connect((hote, port))
print("Connection on {}".format(port))

client.send(str.encode("admin:test:stop"))

print("Close")
client.close()