# ==============================================================================
# 4. OBJETO VISUAL (NOTA)
# ==============================================================================
import pygame

from Config import Config


class VisualNote:
    def __init__(self, corda, casa, tempo_alvo, duracao):
        self.corda = corda
        self.casa = casa
        self.tempo_alvo = tempo_alvo
        self.duracao = duracao

        self.x = Config.get_string_x(corda)
        self.cor = Config.get_string_color(corda)
        self.tocada = False

    def draw(self, surface, current_time):
        time_diff = self.tempo_alvo - current_time
        y = Config.HIT_Y - (time_diff * Config.FALL_SPEED)

        # Só desenha se estiver visível na tela (com margem)
        if -50 < y < Config.HEIGHT + 50:
            radius = 15

            # Desenha a bolinha
            pygame.draw.circle(surface, self.cor, (int(self.x), int(y)), radius)
            pygame.draw.circle(surface, Config.WHITE, (int(self.x), int(y)), radius, 2)

            # Texto da casa
            font = pygame.font.SysFont("Arial", 16, bold=True)
            text = font.render(str(self.casa), True, Config.BLACK)
            rect = text.get_rect(center=(int(self.x), int(y)))
            surface.blit(text, rect)

            # Desenha o rastro (sustain) para notas longas
            if self.duracao > 0.5:
                sustain_height = (self.duracao * Config.FALL_SPEED) * 0.8
                rect_sustain = pygame.Rect(self.x - 5, y - sustain_height, 10, sustain_height)
                if rect_sustain.bottom < y:
                    pygame.draw.rect(surface, self.cor, rect_sustain)

            # Feedback visual se acabou de passar
            if not self.tocada and current_time >= self.tempo_alvo:
                self.tocada = True
                pygame.draw.circle(surface, self.cor, (int(self.x), int(Config.HIT_Y)), 22, 4)