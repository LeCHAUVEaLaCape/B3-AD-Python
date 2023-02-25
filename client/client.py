import socket
from tkinter import *

port = 15555

window = Tk()
window.geometry('500x500+500+500')
window.title("Client")

frame_main = Frame(window)
frame_main.pack()

# IP de l'hôte
label_userName = Label(frame_main, text="Adresse IP de l'hôte : ").pack()
ip = Entry(frame_main)
ip.insert(0, "127.0.0.1")
ip.pack()

label_userName = Label(frame_main, text="Nom d'Utilisateur : ").pack()
nomUtilisateur = Entry(frame_main)
nomUtilisateur.pack()

label_password = Label(frame_main, text="Mot de Passe : ").pack()
motDePasse = Entry(frame_main, show="*")
motDePasse.pack()

def commandeHandler(utilisateur,motPasse,stop=False,read=False,creer=False,supp=False,modifier=False,mod=False):
    if type(utilisateur) is not Entry or type(motPasse) is not Entry:
        texte_sortie.insert('end', 'Erreur\n') 
        pass
    client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    client.settimeout(2)
    try:
        client.connect((ip.get(), port))
        texte_sortie.delete(1.0, END)

        if stop:
            client.send(str.encode(utilisateur.get() + ":" + motPasse.get() + ":s"))
        elif read:
            client.send(str.encode(utilisateur.get() + ":" + motPasse.get() + ":r"))
        elif creer:
            client.send(str.encode(utilisateur.get() + ":" + motPasse.get() + ":c:" + nouvel_Utilisateur.get() + ":" + nouveau_motDePasse.get()))
        elif supp:
            client.send(str.encode(utilisateur.get() + ":" + motPasse.get() + ":d:" + nouvel_Utilisateur.get()))
        elif modifier:
            client.send(str.encode(utilisateur.get() + ":" + motPasse.get() + ":p:" + nouveau_motDePasse.get()))
        elif mod:
            client.send(str.encode(utilisateur.get() + ":" + motPasse.get() + ":m:" + nouvel_Utilisateur.get() + ":" + nouveau_motDePasse.get()))
        texte_sortie.insert('end',client.recv(255))
    except (OSError,ConnectionAbortedError,ConnectionError,ConnectionRefusedError,ConnectionResetError,TimeoutError,socket.timeout)as erreur:
        texte_sortie.insert('end', 'Erreur: ' + str(erreur) + '\n') 
        pass
    client.close()


btn_stop = Button(frame_main, text="Arrêter le serveur",command=lambda: commandeHandler(nomUtilisateur,motDePasse,stop=True)).pack(fill=X, padx=5, pady=5)
btn_lire = Button(frame_main, text="Afficher les comptes",command=lambda: commandeHandler(nomUtilisateur,motDePasse,read=True)).pack(fill=X, padx=5, pady=5)

# creer
label_newUser = Label(frame_main, text="Nom d'utilisateur à Créer/Supprimer : ").pack()
nouvel_Utilisateur = Entry(frame_main)
nouvel_Utilisateur.pack()

label_password_newUser = Label(frame_main, text="Nouveau/Modifier Mot de passe : ").pack()
nouveau_motDePasse = Entry(frame_main, show="*")
nouveau_motDePasse.pack()

btn_creer = Button(frame_main, text="Créer un nouvel utilisateur", command=lambda: commandeHandler(nomUtilisateur,motDePasse,creer=True)).pack(fill=X, padx=5, pady=5)
btn_supprimer = Button(frame_main, text="Supprimer un utilisateur", command=lambda: commandeHandler(nomUtilisateur,motDePasse,supp=True)).pack(fill=X, padx=5, pady=5)
btn_modifier = Button(frame_main, text="Modifier son mot de passe", command=lambda: commandeHandler(nomUtilisateur,motDePasse,modifier=True)).pack(fill=X, padx=5, pady=5)
btn_mod = Button(frame_main, text="Modifier le mot de passe d'un utilisateur", command=lambda: commandeHandler(nomUtilisateur,motDePasse,mod=True)).pack(fill=X, padx=5, pady=5)

# Ajout du champ texte pour afficher des trucs
texte_sortie = Text(frame_main)
texte_sortie.pack()

mainloop()
