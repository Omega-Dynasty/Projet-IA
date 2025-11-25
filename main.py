from threading import Thread
from vision_module import HandController
controller = HandController()

from Tetris import main #Mettre Tetris pour toutes les pièces et Tetris_bis pour seulement 1*1 et 1*2 ( pour présentation)

controller = HandController()

# Lancer la lecture caméra dans un thread séparé
def update_controller():
    while True:
        cmd = controller.read_frame()
        if cmd == "QUIT":
            break

thread = Thread(target=update_controller)
thread.daemon = True
thread.start()

# Lancer le jeu Tetris
main(controller)