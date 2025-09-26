import cv2
import mediapipe as mp

# Inicializa os objetos do MediaPipe fora da classe para serem usados globalmente
mp_hands = mp.solutions.hands
mp_drawing = mp.solutions.drawing_utils

class Camera:
    def __init__(self):
        """
        Inicializa a captura de vídeo e o modelo de detecção de mãos do MediaPipe.
        """
        # Inicia a captura de vídeo da webcam padrão (índice 0)
        self.cap = cv2.VideoCapture(0)
        if not self.cap.isOpened():
            raise IOError("Não foi possível abrir a webcam.")

        # Configura o detector de mãos do MediaPipe
        self.hands = mp_hands.Hands(
            max_num_hands=2,
            min_detection_confidence=0.7,
            min_tracking_confidence=0.5
        )

    def get_frame(self):
        """
        Lê um frame da câmera, processa-o com o MediaPipe e o retorna.
        """
        success, frame = self.cap.read()
        if not success:
            return None, None

        # 1. Inverte a imagem (efeito espelho) e converte a cor de BGR para RGB
        frame = cv2.flip(frame, 1)
        rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)

        # 2. Processa o frame com o MediaPipe para encontrar mãos
        results = self.hands.process(rgb_frame)

        # Retorna o frame em RGB (para o PySide6) e os resultados da detecção
        return rgb_frame, results

    def release(self):
        """
        Libera os recursos da câmera e fecha as janelas ao final.
        """
        self.cap.release()
        self.hands.close()