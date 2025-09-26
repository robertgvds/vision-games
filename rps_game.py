import sys

from PySide6.QtWidgets import (QApplication, QWidget, QLabel, QPushButton, QVBoxLayout, QHBoxLayout, QFrame, QStackedWidget)
from PySide6.QtCore import Qt, QTimer
from PySide6.QtGui import (QImage, QPixmap, QFont, QColor, QPainter, QPainterPath, QBrush)

from camera import Camera, mp_hands, mp_drawing
from game_logic import GameLogic, detectar_gesto

class RPSGame(QWidget):
    def __init__(self):
        super().__init__()
        
        # --- Configurações Iniciais ---
        self.setWindowTitle("Pedra, Papel ou Tesoura com Visão Computacional")
        self.setGeometry(100, 100, 800, 750)
        self.setMinimumSize(600, 700)

        self.camera = Camera()
        self.logic = GameLogic()

        # --- Paleta de Cores e Fontes ---
        self.colors = {
            "bg_dark": "#F0F4F7",
            "bg_medium": "#CAD3DB",

            "primary": "#A5C4D4",      
            "accent_green": "#8EB897", 
            "accent_red": "#E09E8F",   
            
            "text_dark": "#4A3833",
            
            "text_gold": "#E5C07B"
        }

        self.setStyleSheet(f"background-color: {self.colors['bg_dark']}; color: {self.colors['text_dark']};")
        self.font_title = QFont("Segoe UI", 32, QFont.Bold)
        self.font_large = QFont("Segoe UI", 24, QFont.Bold)
        self.font_medium = QFont("Segoe UI", 18)
        self.font_small = QFont("Segoe UI", 14)

        # --- Estados do Jogo ---
        self.is_game_running = False
        self.is_waiting_for_thumb = False
        self.countdown_value = 0
        self.player_move = None

        # --- Estrutura da UI ---
        self.stack = QStackedWidget(self)
        self.main_layout = QVBoxLayout(self)
        self.main_layout.addWidget(self.stack)

        self._create_screens()

        # --- Timers ---
        self.camera_timer = QTimer(self)
        self.camera_timer.timeout.connect(self._update_camera_feed)
        self.camera_timer.start(30)

        self.countdown_timer = QTimer(self)
        self.countdown_timer.timeout.connect(self._update_countdown)

    def _create_screens(self):
        home_screen = self._create_home_screen()
        game_screen = self._create_game_screen()

        self.stack.addWidget(home_screen)
        self.stack.addWidget(game_screen)

    def _create_home_screen(self):
        widget = QWidget()
        layout = QVBoxLayout(widget, alignment=Qt.AlignCenter, spacing=30)
        title = QLabel("Pedra, Papel & Tesoura", alignment=Qt.AlignCenter)
        title.setFont(self.font_title)

        image_path = "assets/rps-hand/image.png"
        image_label = QLabel(alignment=Qt.AlignCenter)
        try:
            pixmap = QPixmap(image_path)
            image_label.setPixmap(pixmap.scaled(400, 400, Qt.KeepAspectRatio, Qt.SmoothTransformation))
        except Exception as e:
            print(f"Erro ao carregar a imagem da tela inicial: {e}")
            image_label.setText("Erro ao carregar imagem")

        start_btn = QPushButton("▶ Iniciar Jogo")
        start_btn.setFont(self.font_large)
        start_btn.setMinimumHeight(80)
        start_btn.setStyleSheet(f"""
            QPushButton {{ background-color: {self.colors['accent_green']}; border-radius: 20px; padding: 15px 30px; }}
            QPushButton:hover {{ background-color: #5cb85c; }}
        """)
        start_btn.clicked.connect(self._start_game)

        layout.addStretch()
        layout.addWidget(title)
        layout.addWidget(image_label)
        layout.addWidget(start_btn, alignment=Qt.AlignCenter)
        layout.addStretch()
        
        return widget

    def _create_game_screen(self):
        widget = QWidget()
        main_layout = QVBoxLayout(widget, spacing=15)
        top_layout = QHBoxLayout()
        
        self.status_label = QLabel("Faça 👍 para começar!", alignment=Qt.AlignCenter)
        self.status_label.setFont(self.font_large)
        
        score_frame = QFrame()
        score_frame.setStyleSheet(f"background-color: {self.colors['bg_medium']}; border-radius: 20px;")
        score_layout = QHBoxLayout(score_frame)
        self.score_label = QLabel("Jogador 0 x 0 PC", alignment=Qt.AlignCenter)
        self.score_label.setFont(self.font_medium)
        score_layout.addWidget(self.score_label)
        
        top_layout.addWidget(self.status_label, 1)
        top_layout.addWidget(score_frame)
        
        self.camera_label = QLabel(alignment=Qt.AlignCenter)
        self.camera_label.setStyleSheet("border: 3px solid #333C4A; border-radius: 20px; background-color: black;")
        
        info_layout = QHBoxLayout(spacing=20)
        signal_frame, self.signal_value_label = self._create_info_box("Sinal Detectado", "---")
        computer_frame, self.computer_choice_value_label = self._create_info_box("Escolha do PC", "❓")
        
        info_layout.addWidget(signal_frame)
        info_layout.addWidget(computer_frame)
        
        self.actions_widget = QWidget()
        actions_layout = QHBoxLayout(self.actions_widget, alignment=Qt.AlignCenter, spacing=20)
        self.restart_btn = QPushButton("Reiniciar Partida")
        self.home_btn = QPushButton("Voltar ao Início")
        for btn, color, action in [
            (self.restart_btn, self.colors['accent_red'], self._reset_game),
            (self.home_btn, self.colors['primary'], self._go_to_home)
        ]:
            btn.setFont(self.font_medium)
            btn.setStyleSheet(f"background-color: {color}; border-radius: 20px; padding: 10px;")
            btn.clicked.connect(action)
            actions_layout.addWidget(btn)
        
        self.actions_widget.hide()
        
        main_layout.addLayout(top_layout, stretch=0)
        main_layout.addWidget(self.camera_label, stretch=1)
        main_layout.addLayout(info_layout, stretch=0)
        main_layout.addWidget(self.actions_widget, stretch=0)
        
        return widget

    def _create_info_box(self, title_text, initial_value):
        frame = QFrame()
        frame.setStyleSheet(f"background-color: {self.colors['bg_medium']}; border-radius: 20px;")
        layout = QVBoxLayout(frame, alignment=Qt.AlignCenter)
        title = QLabel(title_text)
        title.setFont(self.font_small)
        
        value_label = QLabel(initial_value)
        value_label.setFont(self.font_large)
        
        layout.addWidget(title)
        layout.addWidget(value_label)
        
        return frame, value_label

    def _start_game(self):
        self.logic.reset_scores()
        self._update_score_display()
        
        self.stack.setCurrentIndex(1)
        self.is_game_running = True
        
        self._start_new_round()

    def _go_to_home(self):
        self.is_game_running = False
        self.stack.setCurrentIndex(0)

    def _start_new_round(self):
        if self.logic.is_match_over():
            self._end_match()
            return
        
        self.status_label.setText("Faça 👍 para a próxima rodada!")
        self.computer_choice_value_label.setText("❓")
        
        self.actions_widget.hide()
        self.is_waiting_for_thumb = True

    def _create_rounded_pixmap(self, source_pixmap, radius):        
        rounded = QPixmap(source_pixmap.size())
        rounded.fill(Qt.transparent)

        painter = QPainter(rounded)
        painter.setRenderHint(QPainter.Antialiasing) 
        painter.setPen(Qt.NoPen)

        texture_brush = QBrush(source_pixmap)
        painter.setBrush(texture_brush)

        path = QPainterPath()
        path.addRoundedRect(rounded.rect(), radius, radius)

        painter.drawPath(path)
        painter.end()

        return rounded

    def _update_camera_feed(self):
        rgb_frame, results = self.camera.get_frame()
        
        if not self.is_game_running or rgb_frame is None:
            if self.is_game_running:
                self.camera_label.setText("Falha na Câmera")
            return

        detected_gesture = "---"
        if results and results.multi_hand_landmarks:
            for hand_landmarks in results.multi_hand_landmarks:
                mp_drawing.draw_landmarks(rgb_frame, hand_landmarks, mp_hands.HAND_CONNECTIONS)
                gesture = detectar_gesto(hand_landmarks)
                if gesture:
                    detected_gesture = gesture
                    if self.is_waiting_for_thumb and gesture == "Joinha":
                        self.is_waiting_for_thumb = False
                        self._start_countdown()
        if detected_gesture == "Joinha":
            detected_gesture = "👍 Joinha"
        
        self.signal_value_label.setText(detected_gesture)
        pixmap = self._convert_frame_to_pixmap(rgb_frame)
        
        if self.countdown_value > 0:
            painter = QPainter(pixmap)
            painter.setFont(QFont("Arial", 150, QFont.Bold))
            painter.setPen(QColor(255, 255, 0, 200))
            painter.drawText(pixmap.rect(), Qt.AlignCenter, str(self.countdown_value))
            painter.end()
        
        scaled_pixmap = pixmap.scaled(self.camera_label.size(), Qt.IgnoreAspectRatio, Qt.SmoothTransformation)

        rounded_scaled_pixmap = self._create_rounded_pixmap(scaled_pixmap, 27)

        self.camera_label.setPixmap(rounded_scaled_pixmap)

    def _start_countdown(self):
        self.countdown_value = 3
        self.status_label.setText("Prepare-se...")
        self.countdown_timer.start(1000)

        
    def _update_countdown(self):
        if self.countdown_value > 0:
            self.status_label.setText(f"{self.countdown_value}...")
        self.countdown_value -= 1
        
        if self.countdown_value < 0:
            self.countdown_timer.stop()
            self.countdown_value = 0
            self.status_label.setText("JOGUE!")
            QTimer.singleShot(500, self._process_player_move)

    def _process_player_move(self):
        _frame, results = self.camera.get_frame()
        
        self.player_move = "---"
        if results and results.multi_hand_landmarks:
            self.player_move = detectar_gesto(results.multi_hand_landmarks[0])
        
        if self.player_move in ["---", "Joinha", None]:
            self.status_label.setText("Jogada inválida! Tente de novo.")
            QTimer.singleShot(2000, self._start_new_round)
            return
        
        winner, computer_move = self.logic.play_round(self.player_move)
        
        self._update_score_display()
        self.computer_choice_value_label.setText(computer_move)
        result_text = f"{winner}!"
        self.status_label.setText(result_text)
        
        QTimer.singleShot(3000, self._start_new_round)

    def _end_match(self):
        winner_text = self.logic.get_match_winner()
        self.status_label.setText(f"{winner_text}")
        self.actions_widget.show()

    def _reset_game(self):
        self.logic.reset_scores()
        self._update_score_display()
        self._start_new_round()

    def _update_score_display(self):
        self.score_label.setText(f"Jogador {self.logic.player_score} x {self.logic.computer_score} PC")

    def _convert_frame_to_pixmap(self, frame):
        h, w, ch = frame.shape
        bytes_per_line = ch * w
        qt_image = QImage(frame.data, w, h, bytes_per_line, QImage.Format_RGB888)
        
        return QPixmap.fromImage(qt_image)

    def closeEvent(self, event):
        self.camera.release()
        event.accept()

# --- Executar ---
if __name__ == "__main__":
    app = QApplication(sys.argv)
    game = RPSGame()
    game.show()
    sys.exit(app.exec())