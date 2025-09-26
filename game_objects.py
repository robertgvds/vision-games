from PySide6.QtGui import QPixmap
from PySide6.QtCore import QRect
import random

class FallingObject:
    def __init__(self, image_path, settings, size=(80, 80), is_bomb=False): # Adicionado 'settings'
        self.pixmap = QPixmap(image_path).scaled(size[0], size[1])
        self.size = size
        self.is_bomb = is_bomb
        self.sliced = False
        
        self.x = random.randint(100, 700)
        self.y = 600

        # --- MUDANÇA AQUI ---
        # A velocidade agora é definida pelas configurações do estágio atual do jogo
        self.vx = random.uniform(-1.5, 1.5)
        self.vy = random.uniform(settings['min_vy'], settings['max_vy'])

    def update(self):
        """Atualiza a posição do objeto, aplicando gravidade."""
        if not self.sliced:
            self.x += self.vx
            self.y += self.vy
            self.vy += 0.15 # Efeito de gravidade

    def get_rect(self):
        """Retorna a área de colisão do objeto."""
        return QRect(int(self.x), int(self.y), self.size[0], self.size[1])

    def draw(self, painter):
        """Desenha o objeto na tela."""
        painter.drawPixmap(int(self.x), int(self.y), self.pixmap)