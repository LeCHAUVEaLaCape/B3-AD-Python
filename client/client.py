import socket
from tkinter import *

hote = "127.0.0.1"
port = 15555

def commandeHandler(utilisateur,motPasse,stop,read):
    if type(utilisateur) is not Entry or type(motPasse) is not Entry:
        texte_sortie.insert('end', 'Erreur\n') 
        pass
    client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    client.settimeout(2)
    try:
        client.connect((hote, port))
        texte_sortie.delete(1.0, END)
        if stop:
            client.send(str.encode(utilisateur.get() + ":" + motPasse.get() + ":s"))
            texte_sortie.insert('end',client.recv(255))
        elif read:
            client.send(str.encode(utilisateur.get() + ":" + motPasse.get() + ":r"))
            texte_sortie.insert('end',client.recv(255))
    except (ConnectionAbortedError,ConnectionError,ConnectionRefusedError,ConnectionResetError,TimeoutError,socket.timeout)as erreur:
        texte_sortie.insert('end', 'Erreur: ' + str(erreur) + '\n') 
        pass
    client.close()

window = Tk()
window.geometry('500x500+500+500')
window.title("Client")

frame_main = Frame(window)
frame_main.pack()

label_userName = Label(frame_main, text="Nom d'Utilisateur : ").pack()
nomUtilisateur = Entry(frame_main)
nomUtilisateur.pack()

label_password = Label(frame_main, text="Mot de Passe : ").pack()
motDePasse = Entry(frame_main, show="*")
motDePasse.pack()


btn_stop = Button(frame_main, text="Arrêter",command=lambda: commandeHandler(nomUtilisateur,motDePasse,stop=True,read=False)).pack(fill=X, padx=5, pady=5)
btn_lire = Button(frame_main, text="Lire",command=lambda: commandeHandler(nomUtilisateur,motDePasse,read=True,stop=False)).pack(fill=X, padx=5, pady=5)
#btn_modif = Button(frame_main, text="Modifier", command=lambda: commandeHandler(nomUtilisateur,motDePasse,)).pack(fill=X, padx=5, pady=5)

# Ajout du champ texte pour afficher les erreurs 
texte_sortie = Text(frame_main) 
texte_sortie.pack()

mainloop()
