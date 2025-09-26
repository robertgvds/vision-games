# ninja_game.py

import sys
import random
from PySide6.QtWidgets import QApplication, QWidget, QLabel, QPushButton, QVBoxLayout, QHBoxLayout, QStackedWidget
from PySide6.QtCore import Qt, QTimer, QPoint, Signal
from PySide6.QtGui import QPixmap, QPainter, QPen, QFont, QImage, QColor

# Certifique-se de que os arquivos camera.py e game_objects.py estão na mesma pasta
from camera import Camera
from game_objects import FallingObject

# --- TELA 2: O JOGO EM SI ---
class GameWidget(QWidget):
    game_finished = Signal(int)

    DIFFICULTY_STAGES = [
        {'duration': 15, 'spawn_rate': 1200, 'min_vy': -11, 'max_vy': -8, 'bomb_chance': 0.10},
        {'duration': 15, 'spawn_rate': 900, 'min_vy': -13, 'max_vy': -10, 'bomb_chance': 0.15},
        {'duration': 30, 'spawn_rate': 700, 'min_vy': -15, 'max_vy': -12, 'bomb_chance': 0.20},
        {'duration': 40, 'spawn_rate': 500, 'min_vy': -17, 'max_vy': -14, 'bomb_chance': 0.25},
        {'duration': 999, 'spawn_rate': 400, 'min_vy': -19, 'max_vy': -16, 'bomb_chance': 0.30}
    ]

    def __init__(self, colors):
        super().__init__()
        self.colors = colors
        self.camera = Camera()
        self.camera_pixmap = QPixmap()
        
        self.game_objects = []
        self.trail_points_hand1 = []
        self.trail_points_hand2 = []
        
        self.score = 0
        self.lives = 3
        self.game_over = False
        self.game_time_elapsed = 0
        self.current_stage = 0

        self.fruit_images = ["assets/ninja-game/apple.png", "assets/ninja-game/banana.png", "assets/ninja-game/uva.png", "assets/ninja-game/melancia.png"]
        self.bomb_image = "assets/ninja-game/bomb.png"
        
        self.game_timer = QTimer(self)
        self.game_timer.timeout.connect(self.update_game_state)
        self.spawn_timer = QTimer(self)
        self.spawn_timer.timeout.connect(self.spawn_object)
        self.difficulty_timer = QTimer(self)
        self.difficulty_timer.timeout.connect(self._update_difficulty)

    def start_game(self):
        self.score = 0
        self.lives = 3
        self.game_over = False
        self.game_objects.clear()
        self.trail_points_hand1.clear()
        self.trail_points_hand2.clear()
        self.game_time_elapsed = 0
        self.current_stage = 0
        initial_settings = self.DIFFICULTY_STAGES[0]
        self.spawn_timer.start(initial_settings['spawn_rate'])
        self.game_timer.start(16)
        self.difficulty_timer.start(1000)

    def end_game(self):
        self.game_over = True
        self.game_timer.stop()
        self.spawn_timer.stop()
        self.difficulty_timer.stop()
        self.game_finished.emit(self.score)

    def _update_difficulty(self):
        self.game_time_elapsed += 1
        if self.current_stage < len(self.DIFFICULTY_STAGES) - 1:
            stage_end_time = sum(s['duration'] for s in self.DIFFICULTY_STAGES[:self.current_stage + 1])
            if self.game_time_elapsed >= stage_end_time:
                self.current_stage += 1
                new_settings = self.DIFFICULTY_STAGES[self.current_stage]
                self.spawn_timer.setInterval(new_settings['spawn_rate'])

    def spawn_object(self):
        if self.game_over: return
        settings = self.DIFFICULTY_STAGES[self.current_stage]
        if random.random() < settings['bomb_chance']:
            obj = FallingObject(self.bomb_image, settings, is_bomb=True)
        else:
            image_path = random.choice(self.fruit_images)
            obj = FallingObject(image_path, settings)
        if not obj.pixmap.isNull():
            self.game_objects.append(obj)

    def update_game_state(self):
        if self.game_over: return
        rgb_frame, results = self.camera.get_frame()
        if rgb_frame is None: return

        self.camera_pixmap = self._convert_frame_to_pixmap(rgb_frame)
        active_hands_cursors = []
        if results and results.multi_hand_landmarks:
            for hand_landmarks in results.multi_hand_landmarks:
                pt = hand_landmarks.landmark[8]
                cursor_pos = QPoint(int(pt.x * self.width()), int(pt.y * self.height()))
                active_hands_cursors.append(cursor_pos)

        if len(active_hands_cursors) > 0:
            self.trail_points_hand1.append(active_hands_cursors[0])
            if len(self.trail_points_hand1) > 15: self.trail_points_hand1.pop(0)
        else: self.trail_points_hand1.clear()
        
        if len(active_hands_cursors) > 1:
            self.trail_points_hand2.append(active_hands_cursors[1])
            if len(self.trail_points_hand2) > 15: self.trail_points_hand2.pop(0)
        else: self.trail_points_hand2.clear()

        for obj in list(self.game_objects):
            obj.update()
            if obj.y > self.height() and obj.vy > 0:
                if not obj.is_bomb and not obj.sliced:
                    self.lives -= 1
                    if self.lives <= 0: self.end_game()
                self.game_objects.remove(obj)
                continue
            for cursor in active_hands_cursors:
                if obj.get_rect().contains(cursor) and not obj.sliced:
                    obj.sliced = True
                    if obj.is_bomb: self.end_game()
                    else: self.score += 1
                    break 
        self.update()

    def paintEvent(self, event):
        painter = QPainter(self)
        if not self.camera_pixmap.isNull(): painter.drawPixmap(self.rect(), self.camera_pixmap)
        
        for obj in self.game_objects:
            if not obj.sliced: obj.draw(painter)

        if len(self.trail_points_hand1) > 1:
            pen = QPen(QColor(self.colors["primary"]), 5, Qt.SolidLine)
            painter.setPen(pen)
            painter.drawPolyline(self.trail_points_hand1)
        
        if len(self.trail_points_hand2) > 1:
            pen = QPen(QColor(self.colors["accent_red"]), 5, Qt.SolidLine)
            painter.setPen(pen)
            painter.drawPolyline(self.trail_points_hand2)

        painter.setFont(QFont("Arial", 24, QFont.Bold))
        painter.setPen(QColor(self.colors["text_light"])) # Texto branco para contraste com a câmera
        painter.drawText(20, 40, f"Score: {self.score}")
        painter.drawText(self.width() - 150, 40, f"Vidas: {self.lives}")
        
        if self.game_over:
            painter.setFont(QFont("Arial", 50, QFont.Bold))
            painter.setPen(QColor(self.colors["accent_red"]))
            painter.drawText(self.rect(), Qt.AlignCenter, "GAME OVER")
        
        painter.end()

    def _convert_frame_to_pixmap(self, frame):
        h, w, ch = frame.shape
        qt_image = QImage(frame.data, w, h, ch * w, QImage.Format_RGB888)
        return QPixmap.fromImage(qt_image)

# --- JANELA PRINCIPAL: Gerenciador das Telas ---
class MainWindow(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Fruit Ninja")
        self.setGeometry(100, 100, 800, 600)
        self.setFixedSize(800, 600)

        # --- Paleta de Cores: Manhã Suave (Ultra Pastel) ---
        self.colors = {
            "bg_dark": "#F0F4F7",      # Um branco com um toque de azul gelo
            "bg_medium": "#CAD3DB",    # Um cinza-azulado pastel claro
            "primary": "#A5C4D4",      # Azul pastel
            "accent_green": "#8EB897", # Verde sálvia
            "accent_red": "#E09E8F",   # Coral suave
            "text_dark": "#333C4A",     # Cinza-chumbo suave
            "text_light": "#F7F7F7",    # Branco para texto sobre a câmera
            "text_gold": "#E5C07B"       # Dourado suave
        }
        self.setStyleSheet(f"background-color: {self.colors['bg_dark']}; color: {self.colors['text_dark']};")

        self.highscore = self._load_highscore()
        self.stack = QStackedWidget()
        
        self.home_screen = self._create_home_screen()
        self.game_widget = GameWidget(self.colors) # Passa as cores para a tela do jogo
        self.game_over_screen = self._create_game_over_screen()
        
        self.stack.addWidget(self.home_screen)
        self.stack.addWidget(self.game_widget)
        self.stack.addWidget(self.game_over_screen)
        
        self.game_widget.game_finished.connect(self.show_game_over_screen)

        layout = QVBoxLayout()
        layout.setContentsMargins(0,0,0,0)
        layout.addWidget(self.stack)
        self.setLayout(layout)

    def _load_highscore(self):
        try:
            with open("highscore.txt", "r") as f: return int(f.read())
        except (FileNotFoundError, ValueError): return 0

    def _save_highscore(self):
        with open("highscore.txt", "w") as f: f.write(str(self.highscore))

    def _create_home_screen(self):
        widget = QWidget()
        layout = QVBoxLayout(widget, alignment=Qt.AlignCenter, spacing=20)
        
        title = QLabel("Fruit Ninja", alignment=Qt.AlignCenter)
        title.setFont(QFont("Arial", 50, QFont.Bold))

        image_label = QLabel(alignment=Qt.AlignCenter)
        try:
            pixmap = QPixmap("assets/ninja-game/fruitninja.png")
            image_label.setPixmap(pixmap.scaled(300, 300, Qt.KeepAspectRatio, Qt.SmoothTransformation))
        except Exception as e:
            image_label.setText("Imagem não encontrada")
        
        self.highscore_label = QLabel(f"RECORDE: {self.highscore}", alignment=Qt.AlignCenter)
        self.highscore_label.setFont(QFont("Arial", 20))
        
        start_btn = QPushButton("▶ Iniciar Jogo")
        start_btn.setFixedSize(250, 70)
        start_btn.setFont(QFont("Arial", 22))
        start_btn.setStyleSheet(f"background-color: {self.colors['accent_green']}; border-radius: 15px; color: {self.colors['text_light']};")
        start_btn.clicked.connect(self.start_game)
        
        layout.addWidget(title)
        layout.addWidget(image_label)
        layout.addWidget(self.highscore_label)
        layout.addWidget(start_btn, alignment=Qt.AlignCenter)
        return widget
        
    def _create_game_over_screen(self):
        widget = QWidget()
        widget.setStyleSheet(f"background-color: {self.colors['bg_medium']};")
        layout = QVBoxLayout(widget, alignment=Qt.AlignCenter, spacing=25)
        
        title = QLabel("Fim de Jogo", alignment=Qt.AlignCenter)
        title.setFont(QFont("Arial", 50, QFont.Bold))
        
        self.final_score_label = QLabel("Sua pontuação: 0", alignment=Qt.AlignCenter)
        self.final_score_label.setFont(QFont("Arial", 22))
        
        btn_layout = QHBoxLayout()
        restart_btn = QPushButton("Jogar Novamente")
        home_btn = QPushButton("Voltar ao Início")
        
        for btn, color, action in [
            (restart_btn, self.colors['primary'], self.start_game),
            (home_btn, self.colors['accent_red'], self.show_home_screen)
        ]:
            btn.setFixedSize(220, 60)
            btn.setFont(QFont("Arial", 18))
            btn.setStyleSheet(f"background-color: {color}; border-radius: 15px; color: {self.colors['text_light']};")
            btn.clicked.connect(action)
            btn_layout.addWidget(btn)
            
        layout.addWidget(title)
        layout.addWidget(self.final_score_label)
        layout.addLayout(btn_layout)
        return widget

    def start_game(self):
        self.stack.setCurrentWidget(self.game_widget)
        self.game_widget.start_game()

    def show_home_screen(self):
        self.highscore_label.setText(f"RECORDE: {self.highscore}")
        self.final_score_label.setStyleSheet(f"color: {self.colors['text_dark']};") # Reseta cor do score
        self.stack.setCurrentWidget(self.home_screen)

    def show_game_over_screen(self, final_score):
        self.final_score_label.setText(f"Sua pontuação: {final_score}")
        if final_score > self.highscore:
            self.highscore = final_score
            self._save_highscore()
            self.final_score_label.setText(f"NOVO RECORDE: {final_score}!")
            self.final_score_label.setStyleSheet(f"color: {self.colors['text_gold']};")
        
        self.stack.setCurrentWidget(self.game_over_screen)

    def closeEvent(self, event):
        self.game_widget.camera.release()
        event.accept()

# --- Bloco para executar o jogo ---
if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec())