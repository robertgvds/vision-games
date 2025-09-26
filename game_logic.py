import random
import math

def distancia(p1, p2):
    return math.sqrt((p1.x - p2.x)**2 + (p1.y - p2.y)**2)

def detectar_gesto(hand_landmarks):
    if not hand_landmarks: 
        return None 
    tips = [4, 8, 12, 16, 20] # Thumb, Index, Middle, Ring, Pinky 
    dedos = [] # Checa 4 dedos (ignorando polegar)
    
    for i in range(1, 5): 
        if hand_landmarks.landmark[tips[i]].y < hand_landmarks.landmark[tips[i]-2].y: 
            dedos.append(1) 
        else: 
            dedos.append(0) 
    
    total = sum(dedos) # Detecta Joinha: polegar levantado e outros dedos fechados
    if total == 0:
        polegar_tip = hand_landmarks.landmark[4]
        indicador_tip = hand_landmarks.landmark[8]
        if distancia(polegar_tip, indicador_tip) > 0.1: # ajuste a margem conforme necessário 
            return "Joinha" # Pedra/Tesoura/Papel
    
    if total == 0: 
        return "Pedra"
    elif total == 2 and dedos[0] == 1 and dedos[1] == 1:
        return "Tesoura"
    elif total >= 4: 
        return "Papel"
    
    return None

def decidir_vencedor(jogador, computador):
    if jogador == computador:
        return "Empate"
    elif (jogador == "Pedra" and computador == "Tesoura") or \
         (jogador == "Tesoura" and computador == "Papel") or \
         (jogador == "Papel" and computador == "Pedra"):
        return "Jogador"
    else:
        return "Computador"

class GameLogic:
    def __init__(self):
        self.choices = ["Pedra", "Papel", "Tesoura"]
        self.player_score = 0
        self.computer_score = 0
        self.max_rounds = 3 # A partida é uma melhor de 3

    def play_round(self, player_choice):
        # ... (seu código de play_round continua o mesmo) ...
        # ... (ele deve atualizar self.player_score ou self.computer_score) ...
        computer_choice = random.choice(self.choices)
        winner = "Empate"

        if player_choice == computer_choice:
            winner = "Empate"
        elif (player_choice == "Pedra" and computer_choice == "Tesoura") or \
             (player_choice == "Papel" and computer_choice == "Pedra") or \
             (player_choice == "Tesoura" and computer_choice == "Papel"):
            winner = "Você venceu"
            self.player_score += 1
        else:
            winner = "PC venceu"
            self.computer_score += 1
            
        return winner, computer_choice

    def reset_scores(self):
        """Reseta os placares para uma nova partida."""
        self.player_score = 0
        self.computer_score = 0

    # NOVO MÉTODO:
    def is_match_over(self):
        """
        Verifica se a partida (melhor de N) terminou.
        Retorna True se um jogador atingiu a pontuação necessária para vencer.
        """
        score_to_win = (self.max_rounds // 2) + 1
        
        if self.player_score >= score_to_win or self.computer_score >= score_to_win:
            return True
        
        return False

    # NOVO MÉTODO:
    def get_match_winner(self):
        """
        Retorna uma string declarando o vencedor da partida.
        Deve ser chamada apenas depois que is_match_over() retornar True.
        """
        if self.player_score > self.computer_score:
            return "🎉 Você venceu a partida!"
        elif self.computer_score > self.player_score:
            return "💻 O Computador venceu a partida!"
        else:
            # Este caso é raro em "melhor de N", mas é bom ter
            return "🤝 A partida terminou em empate!"
