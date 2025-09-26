import random
from PySide6.QtCore import QRectF, Qt 
from PySide6.QtGui import QPixmap, QPainter, QColor, QPen, QFont # Importa QFont

class Obstacle:
    def __init__(self, screen_width, screen_height, image_path=None):
        self.screen_width = screen_width
        self.screen_height = screen_height
        
        self.size = random.randint(80, 120) 
        self.x = random.randint(0, screen_width - self.size)
        self.y = -self.size
        self.speed = random.randint(5, 10) 

        self.image_path = image_path
        self.pixmap = None
        if self.image_path:
            try:
                self.pixmap = QPixmap(self.image_path).scaled(self.size, self.size)
            except Exception as e:
                print(f"Erro ao carregar imagem do obstáculo '{image_path}': {e}")
                self.pixmap = None

    def update(self):
        self.y += self.speed

    def get_rect(self):
        return QRectF(self.x, self.y, self.size, self.size)

    def draw(self, painter, color=None):
        if self.pixmap and not self.pixmap.isNull():
            painter.drawPixmap(int(self.x), int(self.y), self.pixmap)
        else:
            painter.setBrush(QColor(color if color else "#C0392B"))
            painter.setPen(Qt.NoPen)
            painter.drawRect(int(self.x), int(self.y), self.size, self.size)

class Collectible(Obstacle): # Herda de Obstacle para reusar a lógica de movimento e desenho
    def __init__(self, screen_width, screen_height, image_path="assets/face-game/astronauta.png"):
        super().__init__(screen_width, screen_height, image_path)
        self.size = random.randint(80, 120) 
        self.pixmap = QPixmap(self.image_path).scaled(self.size, self.size)
        self.speed = random.randint(6, 11) 

    def draw(self, painter):
        if self.pixmap and not self.pixmap.isNull():
            painter.drawPixmap(int(self.x), int(self.y), self.pixmap)
        else:
            painter.setBrush(QColor("#FFD700")) 
            painter.setPen(Qt.NoPen)
            painter.drawEllipse(int(self.x), int(self.y), self.size, self.size)

class Player:
    def __init__(self, player_id, screen_width, screen_height, colors, image_path=None):
        self.player_id = player_id 
        self.screen_width = screen_width
        self.screen_height = screen_height
        self.colors = colors
        
        self.size = 120 
        
        if self.player_id == 1:
            self.x = (screen_width / 4) - (self.size / 2)
        else: # player_id == 2
            self.x = (3 * screen_width / 4) - (self.size / 2)
        
        self.y = screen_height - self.size - 20
        self.speed = 10 
        
        self.is_jumping = False 
        self.jump_height = 80 
        self.current_jump_offset = 0 
        self.jump_speed = 8 
        self.invincible = False
        self.invincibility_duration = 1.5

        self.is_out = False 

        self.image_path = image_path
        self.pixmap = None
        if self.image_path:
            try:
                self.pixmap = QPixmap(self.image_path).scaled(self.size, self.size, Qt.KeepAspectRatio, Qt.SmoothTransformation)
            except Exception as e:
                print(f"Erro ao carregar imagem do jogador '{image_path}': {e}")
                self.pixmap = None

    def update_position(self, target_x):
        if not self.is_out: 
            self.x = max(0, min(target_x - self.size / 2, self.screen_width - self.size))

    def update_jump(self):
        if not self.is_out: 
            if self.is_jumping:
                if self.current_jump_offset < self.jump_height:
                    self.current_jump_offset += self.jump_speed
                else:
                    self.is_jumping = False
            else:
                if self.current_jump_offset > 0:
                    self.current_jump_offset -= self.jump_speed
                else:
                    self.current_jump_offset = 0

    def activate_shield(self):
        if not self.is_out: 
            self.invincible = True

    def get_rect(self):
        if self.is_out: 
            return QRectF(-1000, -1000, 1, 1) # Retorna um retângulo fora da tela, quase invisível
        return QRectF(self.x, self.y - self.current_jump_offset, self.size, self.size)

    def draw(self, painter):
        player_y_pos = self.y - self.current_jump_offset

        if self.is_out: # Desenha o jogador de forma diferente se estiver fora
            painter.setOpacity(0.4) # Transparente
            painter.setBrush(QColor(self.colors["text_dark"])) # Cinza escuro
            painter.setPen(Qt.NoPen)
            painter.drawEllipse(int(self.x), int(player_y_pos), self.size, self.size)
            painter.setOpacity(1.0) # Restaura opacidade
            
            # CORREÇÃO: Cria um objeto QFont e passa para setFont
            font = QFont("Arial", 20, QFont.Bold)
            painter.setFont(font)
            painter.setPen(QColor(self.colors["accent_red"]))
            # Ajusta a posição para o texto ficar mais centralizado no jogador
            painter.drawText(int(self.x), int(player_y_pos), self.size, self.size, Qt.AlignCenter, "FORA")
            return # Não desenha o pixmap ou escudo normal

        if self.pixmap and not self.pixmap.isNull():
            painter.drawPixmap(int(self.x), int(player_y_pos), self.pixmap)
        else:
            painter.setBrush(QColor(self.colors["primary"] if self.player_id == 1 else self.colors["accent_green"])) 
            painter.setPen(Qt.NoPen)
            painter.drawEllipse(int(self.x), int(player_y_pos), self.size, self.size)
        
        if self.invincible:
            painter.setBrush(QColor(255, 255, 0, 100)) 
            painter.setPen(QPen(QColor(self.colors["text_light"]), 3)) 
            painter.drawEllipse(int(self.x - 10), int(player_y_pos - 10), self.size + 20, self.size + 20)