# ==============================================================================
# 4. OBJETO VISUAL (NOTA)
# ==============================================================================
import pygame

from Config import Config


# ==============================================================================
# 4. OBJETO VISUAL HORIZONTAL
# ==============================================================================
class VisualNote:
    def __init__(self, corda, casa, tempo_alvo, duracao):
        self.corda = corda
        self.casa = casa
        self.tempo_alvo = tempo_alvo
        self.duracao = duracao

        # Posição Y é FIXA agora (na linha da corda)
        self.y = Config.get_string_y(corda)

        self.cor = Config.get_string_color(corda)
        self.tocada = False

    def draw(self, surface, current_time):
        # A nota se move no Eixo X (Horizontal)
        # Ela deve chegar em HIT_X quando current_time == tempo_alvo
        # X = Target + (Distancia_Tempo * Velocidade)
        time_diff = self.tempo_alvo - current_time
        x = Config.HIT_X + (time_diff * Config.SCROLL_SPEED)

        # Só desenha se estiver visível
        if -50 < x < Config.WIDTH + 50:
            radius = 16

            # Desenha a bolinha
            pygame.draw.circle(surface, self.cor, (int(x), int(self.y)), radius)
            pygame.draw.circle(surface, Config.BLACK, (int(x), int(self.y)), radius, 2)  # Borda

            # Texto da casa (número)
            font = pygame.font.SysFont("Arial", 18, bold=True)
            text = font.render(str(self.casa), True, Config.BLACK)
            rect = text.get_rect(center=(int(x), int(self.y)))
            surface.blit(text, rect)

            # Rastro (Sustain) desenhado para a DIREITA (de onde veio a nota)
            if self.duracao > 0.5:
                sustain_width = (self.duracao * Config.SCROLL_SPEED) * 0.8
                # Retângulo começa na nota e vai para a direita
                rect_sustain = pygame.Rect(x + 10, self.y - 5, sustain_width, 10)
                # Só desenha se não já passou da tela esquerda
                if rect_sustain.right > 0:
                    pygame.draw.rect(surface, self.cor, rect_sustain)

            # Feedback Visual (Flash) quando passa pela linha
            if not self.tocada and current_time >= self.tempo_alvo:
                self.tocada = True
                pygame.draw.circle(surface, Config.WHITE, (int(Config.HIT_X), int(self.y)), 25, 3)