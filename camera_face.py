import cv2
import mediapipe as mp

class FaceCamera:
    def __init__(self):
        self.cap = cv2.VideoCapture(0)
        if not self.cap.isOpened():
            print("Erro: Não foi possível abrir a câmera.")
            exit()

        self.mp_face_mesh = mp.solutions.face_mesh
        self.face_mesh = self.mp_face_mesh.FaceMesh(
            static_image_mode=False,
            max_num_faces=2, # AGORA SUPORTA ATÉ 2 FACES
            refine_landmarks=True,
            min_detection_confidence=0.5,
            min_tracking_confidence=0.5
        )

    def get_frame(self):
        ret, frame = self.cap.read()
        if not ret: return None, None

        frame = cv2.flip(frame, 1)

        rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        
        results = self.face_mesh.process(rgb_frame)

        return rgb_frame, results

    def release(self):
        if self.cap.isOpened():
            self.cap.release()
        self.face_mesh.close()