from vision_module import HandController
from Tetris import main as tetris_main

# Crée le contrôleur main
controller = HandController(cooldown=0)  # cooldown 0 pour test

# Lance le jeu Tetris avec le controller
tetris_main(controller)

# Libération caméra à la fin
controller.release()
