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

    def _draw_static_neck(self, surface):
        # 1. Braço de Madeira (Começa APÓS a pestana)
        neck_width = Config.WIDTH - Config.NECK_START_X
        rect_neck = pygame.Rect(
            Config.NECK_START_X,
            Config.NECK_AREA_START_Y,
            neck_width,
            Config.NECK_HEIGHT
        )
        pygame.draw.rect(surface, Config.WOOD_COLOR, rect_neck)
        pygame.draw.rect(surface, (50, 30, 10), rect_neck, 3)

        # 2. Trastes (Casas 1 a 12) - Não desenhamos traste para a casa 0
        for i in range(1, 13):
            x = Config.get_fret_x(i) + 37
            pygame.draw.line(surface, Config.FRET_COLOR, (x, Config.NECK_AREA_START_Y),
                             (x, Config.NECK_AREA_START_Y + Config.NECK_HEIGHT), 4)
            # Número da casa
            num = self.small_font.render(str(i), True, Config.GRAY)
            surface.blit(num, (x - 45, Config.NECK_AREA_START_Y - 20))

        # 3. Pestana (Nut) - A barra grossa no início
        nut_x = Config.NECK_START_X
        pygame.draw.line(surface, Config.NUT_COLOR,
                         (nut_x, Config.NECK_AREA_START_Y),
                         (nut_x, Config.NECK_AREA_START_Y + Config.NECK_HEIGHT), 10)

        # 4. Cordas no Braço
        for s in Config.STRINGS_ORDER:
            y = Config.get_neck_y(s)
            c = Config.get_string_color(s)
            # Corda desenhada de ponta a ponta
            pygame.draw.line(surface, Config.GRAY, (0, y), (Config.WIDTH, y), 2)
            # Nome da corda
            txt = self.small_font.render(s, True, c)
            surface.blit(txt, (10, y - 8))

            # Marcador de "Corda Solta" (0) fixo, apagado, fora do braço
            zero_x = Config.get_fret_x(0)
            pygame.draw.circle(surface, Config.DARK_GRAY, (int(zero_x), int(y)), 12, 1)
            z_txt = self.small_font.render("0", True, Config.GRAY)
            surface.blit(z_txt, (int(zero_x) - 4, int(y) - 8))

    def _draw_tab_road(self, surface):
        rect = pygame.Rect(0, Config.TAB_MARGIN_Y, Config.WIDTH, Config.TAB_AREA_HEIGHT)
        pygame.draw.rect(surface, Config.DARK_GRAY, rect)
        pygame.draw.line(surface, Config.WHITE, (Config.HIT_X, Config.TAB_MARGIN_Y),
                         (Config.HIT_X, Config.TAB_MARGIN_Y + Config.TAB_AREA_HEIGHT), 4)
        for s in Config.STRINGS_ORDER:
            y = Config.get_tab_y(s)
            c = Config.get_string_color(s)
            pygame.draw.line(surface, Config.GRAY, (0, y), (Config.WIDTH, y), 1)
            txt = self.small_font.render(s, True, c)
            surface.blit(txt, (Config.HIT_X - 30, y - 10))

    def play_song(self, song_id):
        data = self.library.get_song(song_id)
        if not data: return

        print(f"Carregando {data['titulo']}...")
        wav = AudioEngine.generate_wav(data['seq'], data['bpm'])
        if not wav: return

        screen = pygame.display.set_mode((Config.WIDTH, Config.HEIGHT))
        pygame.display.set_caption(f"Guitar Learning - {data['titulo']}")
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
            self._draw_tab_road(screen)
            self._draw_static_neck(screen)

            info1 = self.small_font.render("RITMO (Olhe aqui para saber QUANDO tocar)", True, Config.WHITE)
            screen.blit(info1, (Config.HIT_X + 20, 20))
            info2 = self.small_font.render("POSIÇÃO (Olhe aqui para saber ONDE tocar)", True, Config.WHITE)
            screen.blit(info2, (Config.NECK_START_X, Config.NECK_AREA_START_Y - 45))

            for n in notes:
                n.update(current)
                n.draw_scrolling(screen, current)
                n.draw_on_neck(screen)

            if any(n.ativa for n in notes):
                pygame.draw.line(screen, (255, 255, 0), (Config.HIT_X, Config.TAB_MARGIN_Y),
                                 (Config.HIT_X, Config.TAB_MARGIN_Y + Config.TAB_AREA_HEIGHT), 2)

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
            print("   GUITAR LEARNING SYSTEM")
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