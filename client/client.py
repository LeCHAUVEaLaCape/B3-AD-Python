# coding: utf-8

import socket

hote = "localhost"
port = 15555

client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
client.connect((hote, port))
print("Connection on {}".format(port))
# commandes :
#   - 's' (stop) pour arrêter le serveur
#   - 'm' (modifier) pour modifier quelque chose(p,u)
client.send(str.encode("admin:test:c,"))
print(client.recv(255))
print("Close")
client.close()