import threading
import socket
import redis

hoteBDD = input()
motDePasseBDD = input()

# authentification
def auth(user,motDePasse):
    database = redis.Redis(connection_pool=redis.ConnectionPool(host=hoteBDD, port=6379, db=0,password=motDePasseBDD))
    identifiants = database.hgetall("comptes")
    
    return user in identifiants and identifiants[user] == motDePasse

class ClientThread(threading.Thread):

    def __init__(self, clientSocket, ip, port,stop_event):
        threading.Thread.__init__(self)
        self.ip = ip
        self.port = port
        self.clientsocket = clientSocket
        self.stop_event = stop_event
        print("[+] Nouveau thread pour %s %s" % (self.ip, self.port, ))

    def run(self):
        # 'commandes' est une liste avec :
        #   index 0 comme utilisateur
        #   index 1 comme mot de passe hashé
        #   et les commandes
        requete = self.clientsocket.recv(255).split(b":")
        
        # authentification
        if auth(requete[0],requete[1]):
            # exécution des commandes
            for cmd in requete[2:]:
                match cmd:
                    # 'stop' commande pour arrêter le serveur
                    case b"stop":
                        self.stop_event.set()



def listen_thread(stop_event):
    # pour écouter les connexions entrantes
    serveur = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    
    # timeout de 2 secondes
    serveur.settimeout(2)
    serveur.bind(('', 15555))
    serveur.listen()

    while not stop_event.is_set():
        try:
            (clientSocket, (ip, port)) = serveur.accept()
            newthread = ClientThread(clientSocket, ip, port,stop_event)
            newthread.start()
        except socket.timeout:
            continue


def process_thread(stop_event):
    print("process")

stop_event = threading.Event()

# Create and start the two threads
listen_thread = threading.Thread(target=listen_thread,args=(stop_event,))
listen_thread.start()

process_thread = threading.Thread(target=process_thread,args=(stop_event,))
process_thread.start()
