import socket
import threading


class ClientThread(threading.Thread):

    def __init__(self, ip, port, clientSocket,serveur_stop):
        if serveur_stop[0]: pass
        threading.Thread.__init__(self)
        self.ip = ip
        self.port = port
        self.clientsocket = clientSocket
        self.serveur_stop = serveur_stop
        # Affiche ça apres
        print("[+] Nouveau thread pour %s %s" % (self.ip, self.port, ))

    def run(self):

        commande_byte = self.clientsocket.recv(255)
        match commande_byte:
            case b'stop':
                self.serveur_stop[0] = True

# TODO faire un thread par utilisateur dans un tableau
# TODO fix le serveur stop : ne s'arrete pas directement car il attend 
# TODO fix le port 
SERVEUR_STOP = [False]

serveur = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
serveur.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
serveur.bind(('', 15555))

while True:
    if SERVEUR_STOP[0]: break
    serveur.listen(5)

    (clientSocket, (ip, port)) = serveur.accept()
    newthread = ClientThread(ip, port, clientSocket,SERVEUR_STOP)
    newthread.start()
    
serveur.close()
