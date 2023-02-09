import threading
import socket
import redis
import time
from getpass4 import getpass

CLIENT_THREADS = []

def auth(user, motDePasse):
    """Authentification"""
    database = redis.Redis(connection_pool=redis.ConnectionPool(host=hoteBDD, port=6379, db=0, password=motDePasseBDD))
    identifiants = database.hgetall("comptes")

    return user in identifiants and identifiants[user] == motDePasse

def read(nomUtilisateur):
    database = redis.Redis(connection_pool=redis.ConnectionPool(host=hoteBDD, port=6379, db=0, password=motDePasseBDD))
    # récupére seulement les noms d'utilisateur
    admins = database.hkeys("admins")
    comptes = database.hkeys("comptes")
    # resultat qui sera retourné
    resultat = ""
    if nomUtilisateur in admins:
        resultat = b'\n'.join(admins)
    resultat += b'\n'.join(admins)
    return resultat

def creer(currentUser,args):
    database = redis.Redis(connection_pool=redis.ConnectionPool(host=hoteBDD, port=6379, db=0, password=motDePasseBDD))
    admins = database.hkeys("admins")
    comptes = database.hkeys("comptes")
    # vérifie si l'utilisateur qui à utilisé cette commande est un admin
    if currentUser not in admins :
        return "Vous n'êtes pas administrateur."
    # résultat qui sera retourné
    resultat = ""
    # ajoute chaque utilisateur de args dans l'annuaire
    for user in args:
        if user in comptes:
            resultat += f"{user} existe déjà.\n"
        else:
            resultat += ""

class ClientThread(threading.Thread):

    def __init__(self, clientSocket, ip, port, stop_event):
        threading.Thread.__init__(self)
        self.ip = ip
        self.port = port
        self.clientsocket = clientSocket
        self.stop_event = stop_event
        print("[+] Nouveau thread pour %s %s" % (self.ip, self.port, ))

    def run(self):
        # 'commandes' est une liste avec :
        #   index 0 -> utilisateur
        #   index 1 -> mot de passe hashé
        #   et les commandes
        requete = self.clientsocket.recv(255).split(b":")
        self.nomUtilisateur = requete[0]
        self.motDePasse = requete[1]
        # authentification
        if auth(self.nomUtilisateur, self.motDePasse):
            # exécution des commandes
            for cmdArgs in requete[2:]:
                args = cmdArgs.split(b',')[1:]
                cmd = cmdArgs.split(b',')[0]

                match cmd:
                    # pour arrêter le serveur
                    case b's':
                        self.stop_event.set()
                    # pour modifier
                    case b'm':
                        print("pas fini")
                    # pour lire l'annuaire
                    case b'r':
                        self.clientsocket.send(read(self.nomUtilisateur))
                    # pour créer
                    case b'c':
                        print(args)
                        self.clientsocket.send(creer(self.nomUtilisateur,args))
                        

def listen_thread(stop_event):
    """écoute les connexions entrantes"""
    # pour écouter les connexions entrantes
    serveur = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

    # timeout de 2 secondes
    serveur.settimeout(2)
    serveur.bind(('', 15555))
    serveur.listen()

    while not stop_event.is_set():
        print(len(CLIENT_THREADS))
        try:
            (clientSocket, (ip, port)) = serveur.accept()
            newthread = ClientThread(clientSocket, ip, port, stop_event)
            newthread.start()
        except socket.timeout:
            continue


hoteBDD = input("IP hôte de la Base de donnée ? ")
motDePasseBDD = getpass("mot de passe de la base de donnée : ")

# vérifie la connexion à la base de donnée
redis.StrictRedis(
        host=hoteBDD,
        port=6379,
        password=motDePasseBDD).ping()
        
# 'stop_event' est la pour arrêter le serveur
stop_event = threading.Event()

# Créer et démarre les 2 processus
listen_thread = threading.Thread(target=listen_thread, args=(stop_event,))
listen_thread.start()
