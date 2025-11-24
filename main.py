from threading import Thread
from vision_module import HandController
controller = HandController()

from Tetris import main

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