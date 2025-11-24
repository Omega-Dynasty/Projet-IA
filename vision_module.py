import cv2
import mediapipe as mp

class HandController:
    """
    Contrôle Tetris via la détection d’un doigt grâce à MediaPipe.
    Renvoie des commandes : "LEFT", "RIGHT", "ROTATE", "NONE", ou "QUIT".
    """
    def __init__(self, max_num_hands=1, detection_confidence=0.7, tracking_confidence=0.7):
        self.command = "NONE"
        self.cap = cv2.VideoCapture(0)

        self.mp_hands = mp.solutions.hands
        self.hands = self.mp_hands.Hands(
            max_num_hands=max_num_hands,
            min_detection_confidence=detection_confidence,
            min_tracking_confidence=tracking_confidence
        )
        self.mp_draw = mp.solutions.drawing_utils

    def read_frame(self):
        """
        Lit la caméra, détecte les landmarks de la main, et met à jour self.command.
        """
        if not self.cap.isOpened():
            print("Erreur : caméra inaccessible")
            self.command = "NONE"
            return self.command

        ret, frame = self.cap.read()
        if not ret:
            self.command = "NONE"
            return self.command

        frame = cv2.flip(frame, 1)
        h, w, _ = frame.shape

        # Convertir en RGB pour MediaPipe
        rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        results = self.hands.process(rgb)

        self.command = "NONE"

        if results.multi_hand_landmarks:
            # On ne prend qu’une main (max_num_hands=1)
            hand_landmarks = results.multi_hand_landmarks[0]
            # Dessiner les landmarks pour debug
            self.mp_draw.draw_landmarks(frame, hand_landmarks, self.mp_hands.HAND_CONNECTIONS)

            # Récupérer le landmark du bout de l'index (INDEX_FINGER_TIP)
            # MediaPipe : INDEX_FINGER_TIP correspond à l'index 8
            index_tip = hand_landmarks.landmark[self.mp_hands.HandLandmark.INDEX_FINGER_TIP]
            x_tip = int(index_tip.x * w)
            y_tip = int(index_tip.y * h)

            # Définir des zones de la caméra (gauche, droite, haut)
            if y_tip < h * 0.25:
                self.command = "ROTATE"
            elif x_tip < w * 0.33:
                self.command = "LEFT"
            elif x_tip > w * 0.66:
                self.command = "RIGHT"
            else:
                self.command = "NONE"

            # Affichage du point pour debug
            cv2.circle(frame, (x_tip, y_tip), 10, (255, 0, 0), cv2.FILLED)

        cv2.imshow("Hand Control", frame)
        if cv2.waitKey(1) & 0xFF == ord('q'):
            self.command = "QUIT"

        return self.command

    def release(self):
        self.cap.release()
        cv2.destroyAllWindows()
