import sys
import random
import math 
from PySide6.QtWidgets import QApplication, QWidget, QLabel, QPushButton, QVBoxLayout, QHBoxLayout, QStackedWidget
from PySide6.QtCore import Qt, QTimer, QPoint, Signal, QRectF # Removida a importação de Signal, não será usada
from PySide6.QtGui import QPixmap, QPainter, QPen, QFont, QImage, QColor

import mediapipe as mp 

from camera_face import FaceCamera
from game_objects_face import Obstacle, Player, Collectible 

mp_drawing = mp.solutions.drawing_utils
mp_drawing_styles = mp.solutions.drawing_styles

class FaceGameWidget(QWidget):
    # REMOVIDO: game_finished = Signal(dict) -- Não usaremos mais este sinal

    def __init__(self, colors, parent=None): # Adicionado parent para boas práticas
        super().__init__(parent)
        self.colors = colors
        self.camera = FaceCamera()
        self.camera_pixmap = QPixmap()
        
        self.players = {} 
        self.num_players_current_game = 0 

        self.obstacles = []
        self.collectibles = [] 
        
        self.scores = {}
        self.lives = {}
        
        self.game_over = False
        self.game_paused_by_face_count = False 
        self.warning_message = "" 

        self.game_timer = QTimer(self)
        self.game_timer.timeout.connect(self.update_game_state)
        
        self.spawn_timer = QTimer(self)
        self.spawn_timer.timeout.connect(self.spawn_game_object) 
        
        self.shield_timers = {
            1: QTimer(self),
            2: QTimer(self)
        }
        self.shield_timers[1].setSingleShot(True)
        self.shield_timers[1].timeout.connect(lambda: self._deactivate_shield(1))
        self.shield_timers[2].setSingleShot(True)
        self.shield_timers[2].timeout.connect(lambda: self._deactivate_shield(2))

        self.current_spawn_rate = 800 
        self.min_obstacle_speed = 5   
        self.max_obstacle_speed = 10  

        self.MOUTH_OPEN_THRESHOLD = 0.04 
        
        self.obstacle_specs = [
            ("assets/face-game/rock.png", 10),      
            ("assets/face-game/meteor.png", 8),     
            ("assets/face-game/pedra.png", 7),      
            ("assets/face-game/pedra2.png", 7),     
            ("assets/face-game/pedra3.png", 6),     
            ("assets/face-game/pedra4.png", 6),     
            ("assets/face-game/alien.png", 3),      
            ("assets/face-game/sofa.png", 1),       
            ("assets/face-game/bota.png", 1),       
        ]

        self.collectible_specs = [
            ("assets/face-game/astronauta.png", 5), 
        ]
        self.collectible_spawn_chance = 0.2 

        # NOVO: Callback para notificar a MainWindow sobre o fim do jogo
        self.game_finished_callback = None 

    def set_game_finished_callback(self, callback):
        self.game_finished_callback = callback

    def start_game(self, num_players):
        print(f"DEBUG: Iniciando jogo para {num_players} jogadores.")
        self.num_players_current_game = num_players
        self.scores = {1: 0}
        self.lives = {1: 3}
        self.players = {1: Player(1, self.width(), self.height(), self.colors, image_path="assets/face-game/player.png")}

        if num_players == 2:
            self.scores[2] = 0
            self.lives[2] = 3
            self.players[2] = Player(2, self.width(), self.height(), self.colors, image_path="assets/face-game/player.png")

        self.game_over = False
        self.obstacles.clear()
        self.collectibles.clear() 
        
        for player_id in self.players:
            self.players[player_id].invincible = False
            self.players[player_id].is_out = False 
            if player_id in self.shield_timers:
                 self.shield_timers[player_id].stop() 

        self.warning_message = "" 
        self.game_paused_by_face_count = False 

        self.current_spawn_rate = 800 
        self.min_obstacle_speed = 5   
        self.max_obstacle_speed = 10  
        self.game_timer.start(16)
        print(f"DEBUG: Pontuações iniciais: {self.scores}")


    def end_game(self):
        print("DEBUG: end_game chamado.")
        self.game_over = True
        self.game_timer.stop()
        self.spawn_timer.stop()
        for timer in self.shield_timers.values(): timer.stop()
        
        final_scores_to_send = dict(self.scores) # Captura os scores finais
        print(f"DEBUG: Pontuações finais ANTES de chamar callback: {final_scores_to_send}")
        
        # CHAMA O CALLBACK DIRETAMENTE
        if self.game_finished_callback:
            self.game_finished_callback(final_scores_to_send)
        else:
            print("WARNING: game_finished_callback não foi definido na FaceGameWidget.")
        # REMOVIDO: self.game_finished.emit(final_scores_to_emit)
        print("DEBUG: Callback game_finished_callback (ou aviso) processado.") # Confirma que o callback foi tentado

    def spawn_game_object(self):
        if self.game_over or self.game_paused_by_face_count: return 

        if random.random() < self.collectible_spawn_chance and self.collectible_specs:
            images_paths = [spec[0] for spec in self.collectible_specs]
            weights = [spec[1] for spec in self.collectible_specs]
            selected_image_path = random.choices(images_paths, weights=weights, k=1)[0]
            collectible = Collectible(self.width(), self.height(), image_path=selected_image_path)
            collectible.speed = random.randint(self.min_obstacle_speed + 1, self.max_obstacle_speed + 2) 
            self.collectibles.append(collectible)
        else:
            if not self.obstacle_specs: return 
            images_paths = [spec[0] for spec in self.obstacle_specs]
            weights = [spec[1] for spec in self.obstacle_specs]
            selected_image_path = random.choices(images_paths, weights=weights, k=1)[0]
            obstacle = Obstacle(self.width(), self.height(), image_path=selected_image_path)
            obstacle.speed = random.randint(self.min_obstacle_speed, self.max_obstacle_speed)
            self.obstacles.append(obstacle)

    def _calculate_mouth_distance(self, landmarks):
        lip_upper = landmarks.landmark[13]
        lip_lower = landmarks.landmark[14]
        
        distance = math.sqrt((lip_upper.x - lip_lower.x)**2 + (lip_upper.y - lip_lower.y)**2 + (lip_upper.z - lip_lower.z)**2)
        return distance

    def _activate_shield(self, player_id): 
        if player_id in self.players and not self.players[player_id].is_out: 
            self.players[player_id].activate_shield()
            if player_id in self.shield_timers:
                self.shield_timers[player_id].start(int(self.players[player_id].invincibility_duration * 1000))

    def _deactivate_shield(self, player_id): 
        if player_id in self.players: 
            self.players[player_id].invincible = False

    def update_game_state(self):
        if self.game_over: return

        rgb_frame, results = self.camera.get_frame()
        if rgb_frame is None: return

        white_drawing_spec_contour = mp_drawing.DrawingSpec(color=(255, 255, 255), thickness=1, circle_radius=1)
        white_drawing_spec_tesselation = mp_drawing.DrawingSpec(color=(220, 220, 220), thickness=1, circle_radius=1)
        white_drawing_spec_iris = mp_drawing.DrawingSpec(color=(255, 255, 255), thickness=1, circle_radius=1)


        if results.multi_face_landmarks:
            for face_landmarks in results.multi_face_landmarks:
                mp_drawing.draw_landmarks(
                    image=rgb_frame,
                    landmark_list=face_landmarks,
                    connections=self.camera.mp_face_mesh.FACEMESH_TESSELATION, 
                    landmark_drawing_spec=None, 
                    connection_drawing_spec=white_drawing_spec_tesselation 
                )
                mp_drawing.draw_landmarks(
                    image=rgb_frame,
                    landmark_list=face_landmarks,
                    connections=self.camera.mp_face_mesh.FACEMESH_CONTOURS, 
                    landmark_drawing_spec=None, 
                    connection_drawing_spec=white_drawing_spec_contour 
                )
                mp_drawing.draw_landmarks(
                    image=rgb_frame,
                    landmark_list=face_landmarks,
                    connections=self.camera.mp_face_mesh.FACEMESH_IRISES, 
                    landmark_drawing_spec=None, 
                    connection_drawing_spec=white_drawing_spec_iris 
                )


        self.camera_pixmap = self._convert_frame_to_pixmap(rgb_frame)

        num_faces_detected = 0
        if results.multi_face_landmarks:
            num_faces_detected = len(results.multi_face_landmarks)

        required_faces = self.num_players_current_game

        if num_faces_detected == required_faces: 
            self.game_paused_by_face_count = False 
            if not self.spawn_timer.isActive(): 
                self.spawn_timer.start(self.current_spawn_rate)

            sorted_faces = sorted(results.multi_face_landmarks, key=lambda f: f.landmark[1].x)

            for i in range(required_faces):
                player_id = i + 1 
                if player_id in self.players and not self.players[player_id].is_out:
                    landmarks = sorted_faces[i] 
                    nose_tip = landmarks.landmark[1]
                    target_x_player = int(nose_tip.x * self.width())
                    self.players[player_id].update_position(target_x_player)
                    
                    mouth_distance = self._calculate_mouth_distance(landmarks)
                    if mouth_distance > self.MOUTH_OPEN_THRESHOLD:
                        self._activate_shield(player_id)
            
            self.warning_message = "" 
        else: 
            self.game_paused_by_face_count = True 
            self.spawn_timer.stop() 
            self.obstacles.clear() 
            self.collectibles.clear() 

            self.warning_message = f"Mínimo de {required_faces} rosto(s) na câmera para jogar!"
            
        for player_id in self.players:
            self.players[player_id].update_jump()
        
        if not self.game_paused_by_face_count:
            
            for obstacle in list(self.obstacles):
                obstacle.update()
                if obstacle.y > self.height():
                    self.obstacles.remove(obstacle)
                else:
                    for player_id in list(self.players.keys()): 
                        player = self.players[player_id]
                        if player.is_out: continue 

                        if player.get_rect().intersects(obstacle.get_rect()):
                            if player.invincible:
                                self.obstacles.remove(obstacle)
                                self.scores[player_id] = max(0, self.scores[player_id] - 5) 
                                print(f"DEBUG: P{player_id} Score (colisão com escudo): {self.scores[player_id]}")
                                break 
                            else:
                                self.lives[player_id] -= 1
                                if self.lives[player_id] <= 0:
                                    player.is_out = True 
                                    player.invincible = False 
                                    if player_id in self.shield_timers:
                                        self.shield_timers[player_id].stop() 
                                    
                                self.obstacles.remove(obstacle)
                                print(f"DEBUG: P{player_id} Vida perdida. Vidas restantes: {self.lives[player_id]}. Pontuações atuais: {self.scores}")
                                break 
            
            if all(player.is_out for player in self.players.values()):
                self.end_game()

            for collectible in list(self.collectibles):
                collectible.update()
                if collectible.y > self.height():
                    self.collectibles.remove(collectible)
                else:
                    for player_id in list(self.players.keys()):
                        player = self.players[player_id]
                        if player.is_out: continue 

                        if player.get_rect().intersects(collectible.get_rect()):
                            self.collectibles.remove(collectible)
                            self.scores[player_id] += 10 
                            print(f"DEBUG: P{player_id} Coletou! Score: {self.scores[player_id]}")
                            break 

            total_score = sum(self.scores.values())
            if total_score > 0 and total_score % 40 == 0 and self.spawn_timer.interval() > 200: 
                new_interval = self.spawn_timer.interval() - 50
                self.spawn_timer.setInterval(new_interval)

                self.min_obstacle_speed = min(self.min_obstacle_speed + 1, 15) 
                self.max_obstacle_speed = min(self.max_obstacle_speed + 2, 25) 
                active_players = [pid for pid, p in self.players.items() if not p.is_out]
                if active_players:
                    chosen_player = random.choice(active_players)
                    self.scores[chosen_player] += 1 
                    print(f"DEBUG: P{chosen_player} Ponto extra por dificuldade! Score: {self.scores[chosen_player]}")
                
        self.update() 

    def paintEvent(self, event):
        painter = QPainter(self)
        if not self.camera_pixmap.isNull(): painter.drawPixmap(self.rect(), self.camera_pixmap)
        
        for player_id in self.players:
            self.players[player_id].draw(painter) 
            
        if not self.game_paused_by_face_count:
            for obstacle in self.obstacles:
                obstacle.draw(painter, color=self.colors["accent_red"])
            for collectible in self.collectibles:
                collectible.draw(painter) 

        painter.setFont(QFont("Arial", 24, QFont.Bold))
        painter.setPen(QColor(self.colors["text_light"]))

        if 1 in self.players:
            painter.drawText(20, 40, f"P1 Score: {self.scores.get(1, 0)}")
            painter.drawText(20, 70, f"P1 Vidas: {self.lives.get(1, 0) if self.lives.get(1,0) > 0 else 'FORA'}")
        
        if 2 in self.players: 
            painter.drawText(self.width() - 200, 40, f"P2 Score: {self.scores.get(2, 0)}")
            painter.drawText(self.width() - 200, 70, f"P2 Vidas: {self.lives.get(2, 0) if self.lives.get(2,0) > 0 else 'FORA'}")
        
        if self.warning_message: 
            painter.setFont(QFont("Arial", 28, QFont.Bold)) 
            painter.setPen(QColor(self.colors["accent_red"])) 
            painter.drawText(self.rect(), Qt.AlignCenter, self.warning_message)
            
        if self.game_over:
            painter.setFont(QFont("Arial", 50, QFont.Bold))
            painter.setPen(QColor(self.colors["accent_red"]))
            painter.drawText(self.rect(), Qt.AlignCenter, "GAME OVER")
            
            print(f"DEBUG: Pontuações no paintEvent (Game Over): {self.scores}")
            
            final_scores_text = ""
            if self.num_players_current_game == 1:
                final_scores_text = f"Pontuação Final: {self.scores.get(1, 0)}"
            else: # 2 jogadores
                final_scores_text = f"Pontuações Finais: P1: {self.scores.get(1, 0)} | P2: {self.scores.get(2, 0)}"

            painter.setFont(QFont("Arial", 30))
            painter.drawText(self.rect().adjusted(0, 80, 0, 0), Qt.AlignCenter, final_scores_text)

        painter.end() 

    def _convert_frame_to_pixmap(self, frame):
        h, w, ch = frame.shape
        qt_image = QImage(frame.data, w, h, ch * w, QImage.Format_RGB888)
        return QPixmap.fromImage(qt_image)

class MainWindow(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Esquiva Facial Multiplayer")
        self.setGeometry(100, 100, 1400, 900)
        self.setFixedSize(1400, 900)

        self.colors = {
            "bg_dark": "#F0F4F7",      
            "bg_medium": "#CAD3DB",    
            "primary": "#A5C4D4",      
            "accent_green": "#8EB897", 
            "accent_red": "#FF3333",   
            "text_dark": "#333C4A",     
            "text_light": "#F7F7F7",    
            "text_gold": "#E5C07B"       
        }
        self.setStyleSheet(f"background-color: {self.colors['bg_dark']}; color: {self.colors['text_dark']};")

        self.highscore = self._load_highscore() 

        self.stack = QStackedWidget()
        self.home_screen = self._create_home_screen()
        # Garante que game_widget é criado apenas uma vez
        self.game_widget = FaceGameWidget(self.colors) 
        self.game_over_screen = self._create_game_over_screen()
        
        self.stack.addWidget(self.home_screen)
        self.stack.addWidget(self.game_widget)
        self.stack.addWidget(self.game_over_screen)
        
        # Conecta o callback APENAS UMA VEZ
        self.game_widget.set_game_finished_callback(self.show_game_over_screen)


        layout = QVBoxLayout()
        layout.setContentsMargins(0,0,0,0)
        layout.addWidget(self.stack)
        self.setLayout(layout)

    def _load_highscore(self):
        try:
            with open("highscore_face.txt", "r") as f:
                return int(f.read())
        except (FileNotFoundError, ValueError): return 0

    def _save_highscore(self):
        with open("highscore_face.txt", "w") as f: f.write(str(self.highscore))

    def _create_home_screen(self):
        widget = QWidget()
        layout = QVBoxLayout(widget, alignment=Qt.AlignCenter, spacing=20)
        
        title = QLabel("Esquiva Facial", alignment=Qt.AlignCenter) 
        title.setFont(QFont("Arial", 50, QFont.Bold))

        image_path = "assets/face-game/face_avatar.png"
        image_label = QLabel(alignment=Qt.AlignCenter)
        try:
            pixmap = QPixmap(image_path)
            image_label.setPixmap(pixmap.scaled(200, 200, Qt.KeepAspectRatio, Qt.SmoothTransformation))
        except Exception as e:
            image_label.setText(f"Imagem do jogo não encontrada: {image_path}")
        
        self.highscore_label = QLabel(f"RECORDE (Individual): {self.highscore}", alignment=Qt.AlignCenter) 
        self.highscore_label.setFont(QFont("Arial", 20))
        
        start_1p_btn = QPushButton("▶ Iniciar Jogo (1 Jogador)")
        start_1p_btn.setFixedSize(400, 70)
        start_1p_btn.setFont(QFont("Arial", 20))
        start_1p_btn.setStyleSheet(f"background-color: {self.colors['accent_green']}; border-radius: 15px; color: {self.colors['text_light']};")
        start_1p_btn.clicked.connect(lambda: self.start_game_mode(1)) 
        
        start_2p_btn = QPushButton("▶ Iniciar Jogo (2 Jogadores)")
        start_2p_btn.setFixedSize(400, 70)
        start_2p_btn.setFont(QFont("Arial", 20))
        start_2p_btn.setStyleSheet(f"background-color: {self.colors['primary']}; border-radius: 15px; color: {self.colors['text_light']};")
        start_2p_btn.clicked.connect(lambda: self.start_game_mode(2)) 
        
        layout.addWidget(title)
        layout.addWidget(image_label)
        layout.addWidget(self.highscore_label)
        layout.addWidget(start_1p_btn, alignment=Qt.AlignCenter)
        layout.addWidget(start_2p_btn, alignment=Qt.AlignCenter)
        return widget
        
    def _create_game_over_screen(self):
        widget = QWidget()
        widget.setStyleSheet(f"background-color: {self.colors['bg_medium']};")
        layout = QVBoxLayout(widget, alignment=Qt.AlignCenter, spacing=25)
        
        title = QLabel("Fim de Jogo", alignment=Qt.AlignCenter)
        title.setFont(QFont("Arial", 50, QFont.Bold))
        
        self.final_scores_label = QLabel("Pontuações Finais: P1: 0 | P2: 0", alignment=Qt.AlignCenter)
        self.final_scores_label.setFont(QFont("Arial", 22))
        
        self.new_highscore_label = QLabel("", alignment=Qt.AlignCenter) 
        self.new_highscore_label.setFont(QFont("Arial", 25, QFont.Bold))
        self.new_highscore_label.setStyleSheet(f"color: {self.colors['text_gold']};")

        btn_layout = QHBoxLayout()
        self.restart_btn = QPushButton("Jogar Novamente")
        self.restart_btn.setFixedSize(220, 60)
        self.restart_btn.setFont(QFont("Arial", 18))
        self.restart_btn.setStyleSheet(f"background-color: {self.colors['primary']}; border-radius: 15px; color: {self.colors['text_light']};")
        
        home_btn = QPushButton("Voltar ao Início")
        home_btn.setFixedSize(220, 60)
        home_btn.setFont(QFont("Arial", 18))
        home_btn.setStyleSheet(f"background-color: {self.colors['accent_red']}; border-radius: 15px; color: {self.colors['text_light']};")
        home_btn.clicked.connect(self.show_home_screen)
            
        btn_layout.addWidget(self.restart_btn)
        btn_layout.addWidget(home_btn)
            
        layout.addWidget(title)
        layout.addWidget(self.final_scores_label)
        layout.addWidget(self.new_highscore_label) 
        layout.addLayout(btn_layout) 
        return widget

    def start_game_mode(self, num_players):
        self.stack.setCurrentWidget(self.game_widget)
        self.game_widget.start_game(num_players)

    def show_home_screen(self):
        self.highscore_label.setText(f"RECORDE (Individual): {self.highscore}")
        self.new_highscore_label.setText("") 
        self.stack.setCurrentWidget(self.home_screen)

    def show_game_over_screen(self, final_scores):
        print(f"DEBUG: show_game_over_screen recebendo scores via CALLBACK: {final_scores}")
        
        p1_score = final_scores.get(1, 0) 
        p2_score = final_scores.get(2, 0)
        
        score_text = ""
        # Verifica se o jogo foi para 1 ou 2 jogadores para formatar a mensagem
        if self.game_widget.num_players_current_game == 1:
            score_text = f"Pontuação Final: {p1_score}"
        else: # 2 jogadores
            score_text = f"Pontuações Finais: P1: {p1_score} | P2: {p2_score}"

        self.final_scores_label.setText(score_text)
        
        new_record_achieved = False
        for score in final_scores.values():
            if score > self.highscore:
                self.highscore = score
                new_record_achieved = True
        
        if new_record_achieved:
            self._save_highscore()
            self.new_highscore_label.setText(f"NOVO RECORDE INDIVIDUAL: {self.highscore}!")
        else:
            self.new_highscore_label.setText("") 

        # A desconexão e reconexão do botão de restart deve estar correta agora.
        try:
            self.restart_btn.clicked.disconnect()
        except TypeError: 
            pass # Ignora se não houver conexão para desconectar
        self.restart_btn.clicked.connect(lambda: self.start_game_mode(self.game_widget.num_players_current_game))

        self.stack.setCurrentWidget(self.game_over_screen)

    def closeEvent(self, event):
        self.game_widget.camera.release()
        event.accept()

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec())