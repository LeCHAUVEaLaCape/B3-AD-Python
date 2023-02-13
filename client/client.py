import socket
from tkinter import *

hote = "localhost"
port = 15555

def commandeHandler(nomUtilisateur,motDePasse,stop):
    client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    client.connect((hote, port))
    print("Connection on {}".format(port))
    if stop:
        client.send(str.encode("admin:" + nomUtilisateur.get() + ":" + motDePasse.get() + ":stop"))
    client.close()

window = Tk()
window.title("Client")

frame_main = Frame(window)
frame_main.pack()

label_userName = Label(frame_main, text="Nom d'Utilisateur : ").pack()
nomUtilisateur = Entry(frame_main).pack()
label_password = Label(frame_main, text="Mot de Passe : ").pack()
motDePasse = Entry(frame_main).pack()

btn_stop = Button(frame_main, text="Arrêter",command=lambda: commandeHandler(nomUtilisateur,motDePasse,stop=True)).pack(fill=X, padx=5, pady=5)
btn_modif = Button(frame_main, text="Modifier", command=lambda: commandeHandler(nomUtilisateur,motDePasse,)).pack(fill=X, padx=5, pady=5)

mainloop()
