import cv2
import mediapipe as mp
import time

class HandController:
    """
    Contrôle Tetris via le bout de l'index avec MediaPipe.
    Commandes : "LEFT", "RIGHT", "ROTATE", "NONE", "QUIT".
    """

    def __init__(self, max_num_hands=1, detection_confidence=0.7, tracking_confidence=0.7):
        self.command = "NONE"
        self.cap = cv2.VideoCapture(0)
        
        # --- CONFIGURATION DES LATENCES ---
        self.move_cooldown = 0.15    # 150ms pour gauche/droite (rapide)
        self.rotate_cooldown = 0.6   # 600ms pour tourner (plus lent pour éviter le spam)
        self.last_time = 0
        # ----------------------------------

        self.mp_hands = mp.solutions.hands
        self.hands = self.mp_hands.Hands(
            max_num_hands=max_num_hands,
            min_detection_confidence=detection_confidence,
            min_tracking_confidence=tracking_confidence
        )
        self.mp_draw = mp.solutions.drawing_utils

    def read_frame(self):
        if not self.cap.isOpened():
            self.command = "NONE"
            return self.command

        ret, frame = self.cap.read()
        if not ret:
            self.command = "NONE"
            return self.command

        frame = cv2.flip(frame, 1)
        h, w, _ = frame.shape
        rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        results = self.hands.process(rgb)

        self.command = "NONE"
        current_time = time.time()

        if results.multi_hand_landmarks:
            hand_landmarks = results.multi_hand_landmarks[0]
            self.mp_draw.draw_landmarks(frame, hand_landmarks, self.mp_hands.HAND_CONNECTIONS)

            index_tip = hand_landmarks.landmark[self.mp_hands.HandLandmark.INDEX_FINGER_TIP]
            x_tip = int(index_tip.x * w)
            y_tip = int(index_tip.y * h)

            # --- LOGIQUE DE DÉTECTION AVEC LATENCES SÉPARÉES ---
            
            # 1. On identifie la zone visée par le doigt
            intended_command = "NONE"
            if y_tip < h * 0.35:
                intended_command = "ROTATE"
            elif x_tip < w * 0.45:
                intended_command = "LEFT"
            elif x_tip > w * 0.55:
                intended_command = "RIGHT"

            # 2. On applique le cooldown approprié selon l'action
            time_since_last = current_time - self.last_time
            
            if intended_command == "ROTATE":
                # Vérifie si on a attendu assez longtemps pour tourner (0.6s)
                if time_since_last > self.rotate_cooldown:
                    self.command = "ROTATE"
                    self.last_time = current_time
            
            elif intended_command in ["LEFT", "RIGHT"]:
                # Vérifie si on a attendu assez longtemps pour bouger (0.15s)
                if time_since_last > self.move_cooldown:
                    self.command = intended_command
                    self.last_time = current_time
            
            # Pour le visuel (cercle bleu)
            cv2.circle(frame, (x_tip, y_tip), 10, (255, 0, 0), cv2.FILLED)

        print(f"Commande : {self.command}") # Debug utile
        
        # Affichage des zones pour t'aider à calibrer
        cv2.line(frame, (0, int(h * 0.35)), (w, int(h * 0.35)), (0, 255, 0), 2) # Ligne Rotation
        cv2.imshow("Hand Control", frame)
        
        if cv2.waitKey(1) & 0xFF == ord('q'):
            self.command = "QUIT"

        return self.command

    def release(self):
        self.cap.release()
        cv2.destroyAllWindows()
