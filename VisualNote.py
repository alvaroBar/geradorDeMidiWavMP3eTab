# ==============================================================================
# 4. OBJETO VISUAL (NOTA)
# ==============================================================================
import pygame

from Config import Config


# ==============================================================================
# 4. OBJETO VISUAL
# ==============================================================================
class VisualNote:
    def __init__(self, corda, casa, tempo_alvo, duracao):
        self.corda = corda
        self.casa = casa
        self.tempo_alvo = tempo_alvo
        self.duracao = duracao

        self.y_tab = Config.get_tab_y(corda)
        self.y_neck = Config.get_neck_y(corda)
        self.x_neck = Config.get_fret_x(casa)
        self.cor = Config.get_string_color(corda)
        self.ativa = False

    def update(self, current_time):
        if self.tempo_alvo <= current_time <= (self.tempo_alvo + self.duracao):
            self.ativa = True
        else:
            self.ativa = False

    def draw_scrolling(self, surface, current_time):
        time_diff = self.tempo_alvo - current_time
        x = Config.HIT_X + (time_diff * Config.SCROLL_SPEED)

        if -50 < x < Config.WIDTH + 50:
            radius = 16
            pygame.draw.circle(surface, self.cor, (int(x), int(self.y_tab)), radius)
            pygame.draw.circle(surface, Config.BLACK, (int(x), int(self.y_tab)), radius, 2)

            font = pygame.font.SysFont("Arial", 18, bold=True)
            text = font.render(str(self.casa), True, Config.BLACK)
            surface.blit(text, text.get_rect(center=(int(x), int(self.y_tab))))

            if self.duracao > 0.3:
                sustain_width = (self.duracao * Config.SCROLL_SPEED)
                rect = pygame.Rect(x + 10, self.y_tab - 4, sustain_width, 8)
                if rect.right > 0: pygame.draw.rect(surface, self.cor, rect)

    def draw_on_neck(self, surface):
        if self.ativa:
            pygame.draw.circle(surface, self.cor, (int(self.x_neck), int(self.y_neck)), 18)
            pygame.draw.circle(surface, Config.WHITE, (int(self.x_neck), int(self.y_neck)), 20, 2)
            font = pygame.font.SysFont("Arial", 16, bold=True)
            txt = font.render(str(self.casa), True, Config.BLACK)
            surface.blit(txt, txt.get_rect(center=(int(self.x_neck), int(self.y_neck))))