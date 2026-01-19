# ==============================================================================
# 4. OBJETO VISUAL (NOTA)
# ==============================================================================
import pygame

from Config import Config


# ==============================================================================
# 4. OBJETO VISUAL 3D
# ==============================================================================
class VisualNote:
    def __init__(self, corda, casa, tempo_alvo, duracao):
        self.corda = corda
        self.casa = casa
        self.tempo_alvo = tempo_alvo
        self.duracao = duracao
        self.cor = Config.get_string_color(corda)
        self.ativa = False

    def update(self, current_time):
        if self.tempo_alvo <= current_time <= (self.tempo_alvo + self.duracao):
            self.ativa = True
        else:
            self.ativa = False

    def draw_3d(self, surface, current_time):
        time_diff = self.tempo_alvo - current_time
        progress = time_diff / (Config.START_DELAY / 1000.0)

        if -0.1 < progress < 1.1:
            x, y, scale = Config.project_coordinates(self.corda, progress)
            w = int(60 * scale)
            h = int(30 * scale)

            # --- CAMADA 1: RASTRO (FUNDO) ---
            if self.duracao > 0.2:
                end_time_diff = (self.tempo_alvo + self.duracao) - current_time
                end_progress = end_time_diff / (Config.START_DELAY / 1000.0)

                if end_progress < 1.2:
                    draw_end_progress = min(end_progress, 1.0)
                    end_x, end_y, _ = Config.project_coordinates(self.corda, draw_end_progress)

                    tail_width = int(12 * scale)
                    if tail_width < 2: tail_width = 2

                    pygame.draw.line(surface, self.cor, (x, y), (end_x, end_y), tail_width)

            # --- CAMADA 2: CORPO DA NOTA ---
            # Retângulo arredondado para todas as notas (incluindo 0)
            rect = pygame.Rect(x - w // 2, y - h // 2, w, h)
            pygame.draw.rect(surface, self.cor, rect, border_radius=5)
            pygame.draw.rect(surface, Config.WHITE, rect, 2, border_radius=5)

            # --- CAMADA 3: NÚMERO ---
            # O número é desenhado POR ÚLTIMO, garantindo que fique sobre tudo
            font_size = int(24 * scale)
            if font_size > 10:
                font = pygame.font.SysFont("Arial", font_size, bold=True)
                text = font.render(str(self.casa), True, Config.BLACK)
                surface.blit(text, text.get_rect(center=(x, y)))