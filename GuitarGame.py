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
# 5. JOGO HORIZONTAL (TABLATURA VIEW)
# ==============================================================================
class GuitarGame:
    def __init__(self):
        pygame.init()
        pygame.mixer.init()
        self.library = MusicLibrary()
        self.font_title = pygame.font.SysFont("Arial", 28, bold=True)
        self.font_string = pygame.font.SysFont("Arial", 20, bold=True)

    def _draw_tab_road(self, surface):
        # Fundo da Tablatura (Retângulo Horizontal)
        rect_tab = pygame.Rect(
            0,
            Config.MARGIN_Y - 20,
            Config.WIDTH,
            Config.TAB_HEIGHT + 40
        )
        pygame.draw.rect(surface, Config.DARK_GRAY, rect_tab)

        # Linha de Hit (Alvo) - Vertical
        pygame.draw.line(surface, Config.WHITE,
                         (Config.HIT_X, Config.MARGIN_Y - 20),
                         (Config.HIT_X, Config.HEIGHT - Config.MARGIN_Y + 20), 4)
        pygame.draw.line(surface, (255, 255, 0),  # Amarelo (Centro)
                         (Config.HIT_X, Config.MARGIN_Y - 20),
                         (Config.HIT_X, Config.HEIGHT - Config.MARGIN_Y + 20), 1)

        # Desenha as 6 cordas (Linhas Horizontais)
        for string_name in Config.STRINGS_ORDER:
            y = int(Config.get_string_y(string_name))
            color = Config.get_string_color(string_name)

            # Linha da corda (Horizontal)
            pygame.draw.line(surface, Config.GRAY, (0, y), (Config.WIDTH, y), 2)

            # Nome da corda (Fixo à esquerda)
            txt = self.font_string.render(string_name, True, color)
            surface.blit(txt, (20, y - 10))

    def play_song(self, song_id):
        song_data = self.library.get_song(song_id)
        if not song_data: return

        print(f"Carregando: {song_data['titulo']}...")
        wav_file = AudioEngine.generate_wav(song_data['seq'], song_data['bpm'])
        if not wav_file: return

        screen = pygame.display.set_mode((Config.WIDTH, Config.HEIGHT))
        pygame.display.set_caption(f"Guitar Hero Tab - {song_data['titulo']}")
        clock = pygame.time.Clock()

        # Preparar Notas
        notes = []
        sec_per_beat = 60.0 / song_data['bpm']
        accumulated_time = 3.0  # Aumentei para 3s para dar tempo de ver as notas chegando

        for item in song_data['seq']:
            string, fret, beats = item
            duration = beats * sec_per_beat
            if string != 'PAUSA':
                notes.append(VisualNote(string, fret, accumulated_time, duration))
            accumulated_time += duration

        try:
            pygame.mixer.music.load(wav_file)
        except Exception as e:
            print(f"Erro no mixer: {e}")

        running = True
        audio_started = False
        start_ticks = pygame.time.get_ticks()

        while running:
            current_time = (pygame.time.get_ticks() - start_ticks) / 1000.0

            # Sync Audio (Toca quando o tempo chega em 3.0s, que é onde a música começa visualmente)
            if not audio_started and current_time >= 3.0:
                pygame.mixer.music.play()
                audio_started = True

            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False
                if event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
                    running = False

            # Desenho
            screen.fill(Config.BLACK)
            self._draw_tab_road(screen)

            # Título
            title_surf = self.font_title.render(song_data['titulo'], True, Config.WHITE)
            screen.blit(title_surf, (Config.WIDTH // 2 - title_surf.get_width() // 2, 30))

            # Atualizar Notas
            for note in notes:
                note.draw(screen, current_time)

            pygame.display.flip()
            clock.tick(Config.FPS)

            if current_time > accumulated_time + 4.0:
                running = False

        pygame.mixer.music.stop()
        pygame.mixer.music.unload()
        try:
            os.remove(wav_file)
        except:
            pass

    def run_menu(self):
        while True:
            print("\n" + "=" * 40)
            print("   GUITAR TAB PLAYER (Horizontal)")
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