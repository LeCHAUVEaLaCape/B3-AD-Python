import threading
import socket
import redis
import getpass

# demande l'adresse IP de la base de donnée
hoteBDD = input("IP hôte de la base de donnée ? ")
# demande le mot de passe de la base de donnée
motDePasseBDD = getpass.getpass("mot de passe de la base de donnée : ")

# vérifie la connexion à la base de donnée
if not redis.StrictRedis(host=hoteBDD, port=6379, password=motDePasseBDD).ping():
    print("Echec de la tentative de connexion à la base de donnée.")
    exit(1)

# connexion à la base de donnée
DATABASE = redis.Redis(connection_pool=redis.ConnectionPool(host=hoteBDD, port=6379, db=0, password=motDePasseBDD))

def auth(user, motDePasse):
    """Authentification du client."""
    identifiants = DATABASE.hgetall("comptes,admins")

    return user in identifiants and identifiants[user] == motDePasse

def read(nomUtilisateur):
    """Récupère tous les utilisateurs pour les renvoyer au client."""

    # Récupère seulement les noms d'utilisateur
    admins = DATABASE.hkeys("admins")
    comptes = DATABASE.hkeys("comptes")

    # Vérifie si l'utilisateur est un admin
    if nomUtilisateur in admins:
        resultat = b'\n'.join(admins)
    else:
        resultat = b'\n'.join(comptes)

    return resultat

def create(currentUser,args):
    """Créer un ou des utilisateurs dans la base de donnée"""
    admins = DATABASE.hkeys("admins")
    comptes = DATABASE.hkeys("comptes")
    # vérifie si l'utilisateur est un admin
    if currentUser not in admins :
        return "Vous n'êtes pas administrateur."
    # résultat qui sera retourné
    resultat = ""
    # ajoute chaque utilisateur de args dans l'annuaire
    for user in args:
        # vérifie si l'utilisateur existe déja
        if user in comptes:
            resultat += f"{user} existe déjà.\n"
        else:
            # récupére les comptes déjà existant
            comptesExistant = DATABASE.hgetall('comptes')
            # ajoute le nouveau compte avec un mot de passe par défaut
            comptesExistant[user] = "test"
            # ajoute le nouveau dictionnaire de compte à la base de donnée
            DATABASE.hmset("comptes",comptesExistant)
    return resultat

class ClientThread(threading.Thread):

    def __init__(self, clientSocket, ip, port, stop_event):
        threading.Thread.__init__(self)
        self.ip = ip
        self.port = port
        self.clientsocket = clientSocket
        self.stop_event = stop_event
        print("[+] Nouveau thread pour %s %s" % (self.ip, self.port, ))

    def run(self):
        # récupére le message du client
        requete = self.clientsocket.recv(255).split(b":")
        # l'index 0 correspond au nom d'utilisateur du client
        self.nomUtilisateur = requete[0]
        # l'index 1 correspond au mot de passe du client
        self.motDePasse = requete[1]
        # le client doit être authentifié que le serveur utilise ces commandes
        if auth(self.nomUtilisateur, self.motDePasse):
            # exécution des commandes
            for cmdArgs in requete[2:]:
                # sépare la commande et ses arguments
                cmd = cmdArgs.split(b',')[0]
                args = cmdArgs.split(b',')[1:]

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
                        self.clientsocket.send(create(self.nomUtilisateur,args))
                        

def main():
    # 'stop_event' est la pour arrêter le serveur
    stop_event = threading.Event()
    
    # pour écouter les connexions entrantes
    serveur = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

    # timeout de 2 secondes
    serveur.settimeout(2)
    serveur.bind(('', 15555))
    serveur.listen()

    while not stop_event.is_set():
        try:
            (clientSocket, (ip, port)) = serveur.accept()
            newthread = ClientThread(clientSocket, ip, port, stop_event)
            newthread.start()
        except socket.timeout:
            continue

if __name__ == '__main__':
    main()