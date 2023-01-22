import threading
import socket

SERVEUR_THREADS = []


def auth(user,pw):
    return user == "user" and pw == "mdp"

class ClientThread(threading.Thread):

    def __init__(self, clientSocket, ip, port,stop_event):
        threading.Thread.__init__(self)
        self.ip = ip
        self.port = port
        self.clientsocket = clientSocket
        self.stop_event = stop_event
        print("[+] Nouveau thread pour %s %s" % (self.ip, self.port, ))

    def run(self):

        commandes = self.clientsocket.recv(255).decode("utf-8").split(":")

        # si l'utilisateur s'est identifié
        if auth(commandes[0],commandes[1]):
            for cmd in commandes[2:]:
                print(cmd)
                match cmd:
                    case "stop":
                        self.stop_event.set()



def listen_thread(stop_event):
    # Set up the server to listen for incoming connections
    serveur = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    
    # set un timeout de 2 secondes
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
