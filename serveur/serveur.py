import threading
import socket
import redis
import pickle

# demande l'adresse IP de la base de donnée
hoteBDD = input("IP hôte de la base de donnée ? ")

# vérifie la connexion à la base de donnée
if not redis.StrictRedis(host=hoteBDD, port=6379).ping():
    print("Echec de la tentative de connexion à la base de donnée.")
    exit(1)

# connexion à la base de donnée
DATABASE = redis.Redis(connection_pool=redis.ConnectionPool(host=hoteBDD, port=6379, db=1,))

def auth(user, motDePasse):
    """Authentification du client."""

    admins = pickle.loads(DATABASE.get('admins'))

    comptes = pickle.loads(DATABASE.get('comptes'))

    return (user in admins and admins[user] == motDePasse) or (user in comptes and comptes[user] == motDePasse)

def read(nomUtilisateur,motDePasse):
    """Récupère tous les utilisateurs pour les renvoyer au client."""
    resultat = ""

    # Vérifie si l'utilisateur est un administrateur
    if isAdmin(nomUtilisateur,motDePasse):
        resultat = "Administrateurs : \n"
        for admin in pickle.loads(DATABASE.get('admins')):
            resultat += f"\t{admin}\n"

    # Ajoute les utilisateurs
    resultat += "Utilisateurs : \n"
    for compte in pickle.loads(DATABASE.get('comptes')):
        resultat += f"\t{compte}\n"

    return resultat

def create(currentUser,motDePasse,newUser,newUserPassword):
    """Créer un utilisateur dans la base de donnée"""

    # vérifie si l'utilisateur est un admin
    if not isAdmin(currentUser,motDePasse) :
        return "Vous n'êtes pas administrateur."
    comptes = pickle.loads(DATABASE.get('comptes'))
    # vérifie si l'utilisateur existe déja
    if newUser in comptes:
        return f"Le compte {newUser} existe déjà.\n"
    else:
        comptes[newUser] = newUserPassword
        DATABASE.set('comptes',pickle.dumps(comptes))
    return read(currentUser,motDePasse)

def supprimer(currentUser,motDePasse,newUser):
    """Supprime un utilisateur dans la base de donnée"""

    # vérifie si l'utilisateur est un admin
    if not isAdmin(currentUser,motDePasse) :
        return "Vous n'êtes pas administrateur."
    
    comptes = pickle.loads(DATABASE.get('comptes'))
    # vérifie si l'utilisateur existe
    if newUser not in comptes:
        return f"Le compte '{newUser}' n'existe pas.\n"
    else:
        del(comptes[newUser])
        DATABASE.set('comptes',pickle.dumps(comptes))
    return read(currentUser,motDePasse)

def modifier(currentUser,motDePasse,newUserPassword):
    """Modifie le mot de passe de currentUser"""
    comptes = pickle.loads(DATABASE.get('comptes'))
    if isAdmin(currentUser,motDePasse) :
        comptes = pickle.loads(DATABASE.get('admins'))
        # remplace le mot de passe
        comptes[currentUser] = newUserPassword
        DATABASE.set('admins',pickle.dumps(comptes))
    elif currentUser in comptes: # vérifie si l'utilisateur existe dans les utilisateurs 'normaux'
        # remplace le mot de passe
        comptes[currentUser] = newUserPassword
        DATABASE.set('comptes',pickle.dumps(comptes))
    else:
        return "Erreur : modification mot de passe"
    return "Mot de passe modifié."

def modUser(currentUser,motDePasse,newUser,newUserPassword):
    """Modifie le mot de passe de newUser"""
    # vérifie si l'utilisateur est un admin
    if not isAdmin(currentUser,motDePasse) :
        return "Vous n'êtes pas administrateur."
    comptes = pickle.loads(DATABASE.get('comptes'))
    # vérifie si l'utilisateur existe
    if newUser not in comptes:
        return f"Le compte '{newUser}' n'existe pas.\n"
    # modifie le mot de passe
    comptes[newUser] = newUserPassword
    DATABASE.set('comptes',pickle.dumps(comptes))
    return f"Mot de passe de {newUser} modifié."

def isAdmin(user,motDePasse):
    if type(user) is bytes:
        user = user.decode('utf-8')
    if type(motDePasse) is bytes:
        motDePasse = motDePasse.decode('utf-8')

    admins = pickle.loads(DATABASE.get('admins'))
    return user in admins and admins[user] == motDePasse

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
        self.nomUtilisateur = requete[0].decode('utf-8')
        # l'index 1 correspond au mot de passe du client
        self.motDePasse = requete[1].decode('utf-8')
        # le client doit être authentifié que le serveur utilise ces commandes
        if auth(self.nomUtilisateur, self.motDePasse):
            cmd = requete[2]
            match cmd:
                # pour arrêter le serveur
                case b's':
                    if isAdmin(self.nomUtilisateur,self.motDePasse):
                        self.stop_event.set()
                    else:
                        self.clientsocket.send(str.encode("Vous n'étes pas administrateur."))
                # Lire
                case b'r':
                    self.clientsocket.send(str.encode(read(self.nomUtilisateur,self.motDePasse)))
                # Créer
                case b'c':
                    newUser = requete[3].decode('utf-8')
                    newUserPassword = requete[4].decode('utf-8')
                    self.clientsocket.send(str.encode(create(self.nomUtilisateur,self.motDePasse,newUser,newUserPassword)))
                # Supprimer
                case b'd':
                    newUser = requete[3].decode('utf-8')
                    self.clientsocket.send(str.encode(supprimer(self.nomUtilisateur,self.motDePasse,newUser)))
                # Modifier son mot de passe
                case b'p':
                    newUserPassword = requete[3].decode('utf-8')
                    self.clientsocket.send(str.encode(modifier(self.nomUtilisateur,self.motDePasse,newUserPassword)))
                # Modifier le mot de passe d'un utilisateur
                case b'm':
                    newUser = requete[3].decode('utf-8')
                    newUserPassword = requete[4].decode('utf-8')
                    self.clientsocket.send(str.encode(modUser(self.nomUtilisateur,self.motDePasse,newUser,newUserPassword)))
        else:
            self.clientsocket.send(str.encode("L'authentification a échoué."))

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