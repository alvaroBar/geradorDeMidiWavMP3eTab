# ==============================================================================
# 5. JOGO (CLASSE PRINCIPAL)
# ==============================================================================
import os

import pygame

from AudioEngine import AudioEngine
from Config import Config
from MusicLibrary import MusicLibrary
from VisualNote import VisualNote


# ==============================================================================
# 5. JOGO PRINCIPAL
# ==============================================================================
class GuitarGame:
    def __init__(self):
        pygame.init()
        pygame.mixer.init()
        self.library = MusicLibrary()
        self.font = pygame.font.SysFont("Arial", 22, bold=True)
        self.small_font = pygame.font.SysFont("Arial", 16)

    def _draw_highway(self, surface):
        bottom_left = (Config.CENTER_X - Config.BOTTOM_WIDTH // 2, Config.HIT_Y + 50)
        bottom_right = (Config.CENTER_X + Config.BOTTOM_WIDTH // 2, Config.HIT_Y + 50)
        top_left = (Config.CENTER_X - Config.TOP_WIDTH // 2, Config.HORIZON_Y)
        top_right = (Config.CENTER_X + Config.TOP_WIDTH // 2, Config.HORIZON_Y)

        pygame.draw.polygon(surface, (20, 20, 30), [bottom_left, top_left, top_right, bottom_right])
        pygame.draw.line(surface, Config.WHITE, (Config.CENTER_X - Config.BOTTOM_WIDTH // 2, Config.HIT_Y),
                         (Config.CENTER_X + Config.BOTTOM_WIDTH // 2, Config.HIT_Y), 4)
        pygame.draw.line(surface, (255, 255, 100), (Config.CENTER_X - Config.BOTTOM_WIDTH // 2, Config.HIT_Y),
                         (Config.CENTER_X + Config.BOTTOM_WIDTH // 2, Config.HIT_Y), 2)

        for s in Config.STRINGS_ORDER:
            x_near, y_near, _ = Config.project_coordinates(s, -0.1)
            x_far, y_far, _ = Config.project_coordinates(s, 1.0)
            color = Config.get_string_color(s)
            pygame.draw.line(surface, color, (x_near, y_near), (x_far, y_far), 2)
            font = pygame.font.SysFont("Arial", 20, bold=True)
            txt = font.render(s, True, color)
            surface.blit(txt, (x_near - 5, y_near + 10))

    def play_song(self, song_id):
        data = self.library.get_song(song_id)
        if not data: return
        print(f"Carregando {data['titulo']}...")
        wav = AudioEngine.generate_wav(data['seq'], data['bpm'])
        if not wav: return

        screen = pygame.display.set_mode((Config.WIDTH, Config.HEIGHT))
        pygame.display.set_caption(f"Guitar 3D - {data['titulo']}")
        clock = pygame.time.Clock()

        notes = []
        sec_per_beat = 60.0 / data['bpm']
        acc_time = Config.START_DELAY / 1000.0

        for item in data['seq']:
            s, f, b = item
            dur = b * sec_per_beat
            if s != 'PAUSA': notes.append(VisualNote(s, f, acc_time, dur))
            acc_time += dur

        try:
            pygame.mixer.music.load(wav)
        except:
            pass

        running = True
        pygame.mixer.music.play()
        start_ticks = pygame.time.get_ticks()

        while running:
            current = (pygame.time.get_ticks() - start_ticks) / 1000.0

            for e in pygame.event.get():
                if e.type == pygame.QUIT: running = False
                if e.type == pygame.KEYDOWN and e.key == pygame.K_ESCAPE: running = False

            screen.fill(Config.BLACK)

            # 1. DESENHA O CENÁRIO (FUNDO)
            self._draw_highway(screen)
            title = self.font.render(data['titulo'], True, Config.WHITE)
            screen.blit(title, (20, 20))

            # 2. ATUALIZA ESTADO E IDENTIFICA CORDAS ATIVAS
            active_strings = []
            for n in notes:
                n.update(current)
                if n.ativa: active_strings.append(n.corda)

            # 3. DESENHA EFEITO DE CORDA ATIVA (MEIO)
            # Desenhado ANTES das notas para ficar por baixo
            for s in list(set(active_strings)):
                x_near, y_near, _ = Config.project_coordinates(s, 0.0)
                x_far, y_far, _ = Config.project_coordinates(s, 1.0)
                c = Config.get_string_color(s)

                # Linha brilhante (Fica sob a nota)
                pygame.draw.line(screen, Config.WHITE, (x_near, y_near), (x_far, y_far), 4)

                # Explosão de luz na base
                pygame.draw.circle(screen, c, (x_near, y_near), 15)
                pygame.draw.circle(screen, Config.WHITE, (x_near, y_near), 10)

            # 4. DESENHA AS NOTAS (TOPO)
            # Desenhado POR ÚLTIMO para garantir que a nota e o número cubram a linha da corda
            for n in notes:
                n.draw_3d(screen, current)

            pygame.display.flip()
            clock.tick(Config.FPS)

            if current > acc_time + 4.0: running = False

        pygame.mixer.music.stop()
        pygame.mixer.music.unload()
        try:
            os.remove(wav)
        except:
            pass

    def run_menu(self):
        while True:
            print("\n" + "=" * 40)
            print("   GUITAR 3D SYSTEM")
            print("=" * 40)
            for k, v in self.library.get_all():
                print(f"{k} - {v['titulo']}")
            print("0 - Sair")
            op = input("\nEscolha: ")
            if op == '0': break
            self.play_song(op)
        pygame.quit()


if __name__ == "__main__":
    game = GuitarGame()
    game.run_menu()