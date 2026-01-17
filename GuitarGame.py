# ==============================================================================
# 5. JOGO (CLASSE PRINCIPAL)
# ==============================================================================
import os

import pygame

from AudioEngine import AudioEngine
from Config import Config
from MusicLibrary import MusicLibrary
from VisualNote import VisualNote


class GuitarGame:
    def __init__(self):
        pygame.init()
        pygame.mixer.init()
        self.library = MusicLibrary()
        self.font_title = pygame.font.SysFont("Arial", 24, bold=True)
        self.font_fret = pygame.font.SysFont("Arial", 16, bold=True)

    def _draw_neck(self, surface):
        # Fundo do Braço (Madeira)
        rect_neck = pygame.Rect(
            Config.MARGIN_X - 10,
            0,
            Config.NECK_WIDTH + 20,
            Config.HEIGHT
        )
        pygame.draw.rect(surface, Config.WOOD_COLOR, rect_neck)

        # Cordas e Linha de Hit
        pygame.draw.line(surface, Config.WHITE,
                         (Config.MARGIN_X - 20, Config.HIT_Y),
                         (Config.WIDTH - Config.MARGIN_X + 20, Config.HIT_Y), 3)
        pygame.draw.line(surface, (255, 255, 0),  # Amarelo Fix
                         (Config.MARGIN_X - 20, Config.HIT_Y),
                         (Config.WIDTH - Config.MARGIN_X + 20, Config.HIT_Y), 1)

        # Desenha as 6 cordas
        for i, string_name in enumerate(Config.STRINGS):
            x = int(Config.get_string_x(string_name))
            color = Config.get_string_color(string_name)

            # Linha da corda
            pygame.draw.line(surface, Config.GRAY, (x, 0), (x, Config.HEIGHT), 2)

            # Nome da corda embaixo
            txt_shadow = self.font_fret.render(string_name, True, Config.BLACK)
            surface.blit(txt_shadow, (x - 4, Config.HEIGHT - 49))

            txt_col = self.font_fret.render(string_name, True, color)
            surface.blit(txt_col, (x - 5, Config.HEIGHT - 50))

    def play_song(self, song_id):
        song_data = self.library.get_song(song_id)
        if not song_data: return

        print(f"Carregando: {song_data['titulo']}...")

        # 1. Gerar Áudio
        wav_file = AudioEngine.generate_wav(song_data['seq'], song_data['bpm'])
        if not wav_file: return

        # 2. Configurar Tela
        screen = pygame.display.set_mode((Config.WIDTH, Config.HEIGHT))
        pygame.display.set_caption(f"Guitar Hero Tutorial - {song_data['titulo']}")
        clock = pygame.time.Clock()

        # 3. Preparar Notas
        notes = []
        sec_per_beat = 60.0 / song_data['bpm']
        accumulated_time = 2.0  # Delay inicial

        for item in song_data['seq']:
            string, fret, beats = item
            duration = beats * sec_per_beat
            if string != 'PAUSA':
                notes.append(VisualNote(string, fret, accumulated_time, duration))
            accumulated_time += duration

        # 4. Carregar Som
        try:
            pygame.mixer.music.load(wav_file)
        except Exception as e:
            print(f"Erro no mixer: {e}")

        # 5. Loop do Jogo
        running = True
        audio_started = False
        start_ticks = pygame.time.get_ticks()

        while running:
            current_time = (pygame.time.get_ticks() - start_ticks) / 1000.0

            # Sync Audio
            if not audio_started and current_time >= 2.0:
                pygame.mixer.music.play()
                audio_started = True

            # Eventos
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False
                if event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
                    running = False

            # Desenho
            screen.fill(Config.BLACK)
            self._draw_neck(screen)

            # Título
            title_surf = self.font_title.render(song_data['titulo'], True, Config.WHITE)
            screen.blit(title_surf, title_surf.get_rect(center=(Config.WIDTH // 2, 30)))

            # Atualizar Notas
            for note in notes:
                note.draw(screen, current_time)

            pygame.display.flip()
            clock.tick(Config.FPS)

            if current_time > accumulated_time + 2.0:
                running = False

        # Limpeza
        pygame.mixer.music.stop()
        pygame.mixer.music.unload()
        try:
            os.remove(wav_file)
        except:
            pass

    def run_menu(self):
        while True:
            print("\n" + "=" * 40)
            print("   GUITAR HERO TUTORIAL (Versão Refatorada)")
            print("=" * 40)
            for k, v in self.library.get_all():
                print(f"{k} - {v['titulo']}")
            print("0 - Sair")

            op = input("\nEscolha: ")
            if op == '0': break

            self.play_song(op)

        pygame.quit()


# ==============================================================================
# ENTRY POINT
# ==============================================================================
if __name__ == "__main__":
    game = GuitarGame()
    game.run_menu()