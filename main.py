import pygame
import os
import sys
import ctypes
import math
from pydub import AudioSegment, effects
from pydub.silence import detect_leading_silence


# ==============================================================================
# 1. CONFIGURAÇÕES
# ==============================================================================
class Config:
    try:
        ctypes.windll.user32.SetProcessDPIAware()
    except:
        pass

    WIDTH = 1000
    HEIGHT = 700
    FPS = 60

    # Cores
    BLACK = (10, 10, 15)
    WHITE = (255, 255, 255)
    GRAY = (100, 100, 100)
    DARK_GRAY = (30, 30, 30)

    # Cores Neon (Estilo Rocksmith)
    STRING_COLORS = [
        (255, 60, 60),  # E - Vermelho
        (255, 255, 60),  # A - Amarelo
        (60, 100, 255),  # D - Azul
        (60, 255, 60),  # G - Verde
        (255, 165, 0),  # B - Laranja
        (200, 80, 255)  # e - Roxo
    ]

    START_DELAY = 3000

    # --- GEOMETRIA 3D ---
    HORIZON_Y = 100
    HIT_Y = 600
    BOTTOM_WIDTH = 750  # Um pouco mais largo para caber melhor os números
    TOP_WIDTH = 80
    CENTER_X = WIDTH // 2

    STRINGS_ORDER = ['E', 'A', 'D', 'G', 'B', 'e']

    @staticmethod
    def get_string_color(string_name):
        std_order = ['E', 'A', 'D', 'G', 'B', 'e']
        try:
            return Config.STRING_COLORS[std_order.index(string_name)]
        except:
            return Config.WHITE

    @staticmethod
    def project_coordinates(string_name, progress):
        y = Config.HIT_Y - (progress * (Config.HIT_Y - Config.HORIZON_Y))
        current_track_width = Config.BOTTOM_WIDTH - (progress * (Config.BOTTOM_WIDTH - Config.TOP_WIDTH))

        idx = Config.STRINGS_ORDER.index(string_name)
        center_offset = idx - 2.5

        string_spacing = current_track_width / 6
        x = Config.CENTER_X + (center_offset * string_spacing) + (string_spacing / 2)

        scale = 1.0 - (progress * 0.7)

        return int(x), int(y), scale


# ==============================================================================
# 2. MOTOR DE ÁUDIO
# ==============================================================================
class AudioEngine:
    _samples_cache = {}

    @staticmethod
    def _trim_silence(audio, silence_threshold=-40.0, chunk_size=10):
        trim_ms = detect_leading_silence(audio, silence_threshold=silence_threshold, chunk_size=chunk_size)
        return audio[max(0, trim_ms - 5):]

    @staticmethod
    def load_string_sample(string_name):
        if string_name in AudioEngine._samples_cache: return AudioEngine._samples_cache[string_name]
        file_map = {'e': 'e_aguda.wav', 'E': 'E.wav'}
        target = file_map.get(string_name, f"{string_name}.wav")
        options = [f"samples/{target}", f"samples/{string_name}.m4a"]
        audio = None
        for path in options:
            if os.path.exists(path):
                try:
                    audio = AudioSegment.from_file(path)
                    break
                except:
                    pass
        if audio:
            audio = audio.set_channels(1)
            audio = AudioEngine._trim_silence(audio)
            audio = audio.high_pass_filter(80).low_pass_filter(6000)
            audio = effects.normalize(audio)
            AudioEngine._samples_cache[string_name] = audio
            return audio
        return None

    @staticmethod
    def pitch_shift(audio, semitones):
        if semitones == 0: return audio
        new_rate = int(audio.frame_rate * (2.0 ** (semitones / 12.0)))
        return audio._spawn(audio.raw_data, overrides={'frame_rate': new_rate}).set_frame_rate(44100)

    @staticmethod
    def generate_wav(seq, bpm, filename="temp.wav"):
        try:
            song = AudioSegment.silent(duration=Config.START_DELAY)
            ms_per_beat = (60.0 / bpm) * 1000.0
            pos = Config.START_DELAY

            print("   > Renderizando áudio...")
            for item in seq:
                s, f, b = item
                dur = b * ms_per_beat
                if s == 'PAUSA':
                    pos += dur
                else:
                    samp = AudioEngine.load_string_sample(s)
                    if samp:
                        note = AudioEngine.pitch_shift(samp, f)
                        play_dur = dur + 200
                        if len(note) > play_dur + 100: note = note[:play_dur + 100].fade_out(100)
                        if pos + len(note) > len(song):
                            song += AudioSegment.silent(duration=(pos + len(note) - len(song) + 500))
                        song = song.overlay(note - 2.0, position=int(pos))
                    pos += dur
            song.export(filename, format="wav")
            return filename
        except Exception as e:
            print(f"Erro Audio: {e}")
            return None


class MusicLibrary:
    def __init__(self):
        self._songs = {
            "1": {
                "titulo": "Sapo Cururu",
                "bpm": 100,
                "compasso": (2, 4),
                "seq": [
                    ('G', 0, 0.5), ('G', 2, 0.5), ('G', 0, 0.5), ('D', 2, 0.5), ('B', 1, 2.0),
                    ('G', 0, 0.5), ('G', 2, 0.5), ('G', 0, 0.5), ('D', 2, 0.5), ('B', 1, 2.0),
                    ('e', 0, 0.5), ('e', 0, 0.5), ('B', 3, 0.5), ('e', 0, 0.5),
                    ('e', 1, 0.5), ('B', 3, 0.25), ('B', 0, 0.25), ('G', 0, 1.75),
                    ('B', 0, 0.5), ('B', 0, 0.5), ('G', 2, 0.5), ('B', 0, 0.5), ('B', 1, 3.5)
                ]
            },
            "2": {
                "titulo": "Parabéns pra Você",
                "bpm": 100,
                "compasso": (3, 4),
                "seq": [
                    ('G', 0, 0.75), ('G', 0, 0.25), ('G', 2, 1.0), ('G', 0, 1.0), ('B', 1, 1.0), ('B', 0, 2.0),
                    ('G', 0, 0.75), ('G', 0, 0.25), ('G', 2, 1.0), ('G', 0, 1.0), ('B', 3, 1.0), ('B', 1, 2.0),
                    ('G', 0, 0.75), ('G', 0, 0.25), ('e', 3, 1.0), ('e', 0, 1.0), ('B', 1, 1.0), ('B', 0, 1.0), ('G', 2, 2.0),
                    ('e', 1, 0.75), ('e', 1, 0.25), ('e', 0, 1.0), ('B', 1, 1.0), ('B', 3, 1.0), ('B', 1, 2.0)
                ]
            },
            "3": {
                "titulo": "Marcha Soldado",
                "bpm": 115,
                "compasso": (2, 4),
                "seq": [
                    # Mar-cha sol-da-do
                    ('e', 3, 1), ('e', 3, 0.5), ('e', 0, 0.5), ('B', 1, 1), ('B', 1, 0.5),
                    # Ca-be-ça de pa-pel
                    ('e', 0, 0.5), ('e', 3, 0.5), ('e', 3, 0.5), ('e', 3, 0.5), ('e', 0, 0.5), ('B', 3, 1.5),
                    # Quem não mar-char di-rei-to
                    ('e', 0, 0.5), ('e', 1, 0.5), ('e', 1, 0.5), ('e', 1, 0.5), ('B', 3, 0.5), ('e', 3, 1), ('e', 3, 0.5),
                    # Vai pre-so no quar-tel
                    ('e', 5, 0.5), ('e', 3, 0.5), ('e', 1, 0.5), ('e', 0, 0.5), ('B', 3, 0.5), ('B', 1, 1),
                    # O quar-tel pe-gou fo-go
                    ('B', 1, 0.5), ('e', 0, 0.5), ('e', 3, 1), ('e', 3, 0.5), ('e', 0, 0.5), ('B', 1, 1), ('B', 1, 0.5),
                    # São Fran-cis-co deu si-nal
                    ('e', 0, 0.5), ('e', 3, 0.5), ('e', 3, 0.5), ('e', 3, 0.5), ('e', 0, 0.5), ('B', 3, 1.5),
                    # A-co-de a-co-de a-co-de
                    ('e', 0, 0.5), ('e', 1, 0.5), ('e', 1, 0.5), ('e', 1, 0.5), ('B', 3, 0.5), ('e', 3, 1), ('e', 3, 0.5),
                    # A ban-dei-ra na-cio-nal
                    ('e', 5, 0.5), ('e', 3, 0.5), ('e', 1, 0.5), ('e', 0, 0.5), ('B', 3, 0.5), ('B', 1, 1),
                ]
            },
            "4": {
                "titulo": "Brilha Brilha Estrelinha",
                "bpm": 100,
                "compasso": (4, 4),
                "seq": [
                    ('G', 0, 1.0), ('G', 0, 1.0), ('B', 3, 1.0), ('B', 3, 1.0), ('e', 0, 1.0), ('e', 0, 1.0), ('B', 3, 1.0), ('B', 3, 1.0),
                    ('B', 1, 1.0), ('B', 1, 1.0), ('B', 0, 1.0), ('B', 0, 1.0), ('G', 2, 1.0), ('G', 2, 1.0), ('G', 0, 2.0),
                    ('B', 3, 1.0), ('B', 3, 1.0), ('B', 1, 1.0), ('B', 1, 1.0), ('B', 0, 1.0), ('B', 0, 1.0), ('G', 2, 2.0),
                    ('B', 3, 1.0), ('B', 3, 1.0), ('B', 1, 1.0), ('B', 1, 1.0), ('B', 0, 1.0), ('B', 0, 1.0), ('G', 2, 2.0),
                    ('G', 0, 1.0), ('G', 0, 1.0), ('B', 3, 1.0), ('B', 3, 1.0), ('e', 0, 1.0), ('e', 0, 1.0), ('B', 3, 1.0), ('B', 3, 1.0),
                    ('B', 1, 1.0), ('B', 1, 1.0), ('B', 0, 1.0), ('B', 0, 1.0), ('G', 2, 1.0), ('G', 2, 1.0), ('G', 0, 2.0)
                ]
            },
            "5": {
                "titulo": "Atirei o Pau no Gato",
                "bpm": 100,
                "compasso": (4, 4),
                "seq": [
                    # Aaaa-ti-rei
                    ('G', 0, 1.5), ('D', 3, 0.5), ('D', 2, 0.5),
                    # Mas o ga-to-to
                    ('D', 0, 0.5), ('D', 2, 0.5), ('D', 3, 0.5), ('G', 0, 1), ('G', 0, 1), ('G', 0, 1.0),
                    # maaas o ga-to-to
                    ('G', 2, 0.5), ('G', 0, 0.5), ('D', 3, 1), ('D', 3, 1), ('D', 3, 1),
                    # não mo-reu-reu-reu
                    ('G', 0, 0.5), ('D', 3, 0.5), ('D', 2, 1), ('D', 2, 1), ('D', 2, 1),
                    # Do-na chi_ca-ca
                    ('D', 0, 0.5), ('A', 3, 0.5), ('G', 2, 1), ('G', 2, 1), ('G', 2, 1),
                    # Ad-mi-rou se-se
                    ('B', 0, 0.5), ('G', 2, 0.5), ('G', 0, 1), ('G', 0, 1), ('G', 0, 1),
                    # Do ber-ro do ber-ro
                    ('D', 3, 0.5), ('D', 2, 0.5), ('G', 0, 1), ('D', 3, 0.5), ('D', 2, 0.5), ('G', 0, 0.5),
                    # que o ga-to deu
                    ('D', 3, 0.5), ('D', 2, 0.5), ('D', 0, 0.5), ('A', 3, 2),
                ]
            },
            "6": {
                "titulo": "Ciranda Cirandinha",
                "bpm": 100,
                "compasso": (2, 4),
                "seq": [
                    # Ci-ran-da
                    ('A', 3, 1), ('D', 3, 0.5), ('D', 3, 0.5),
                    # Ci-ran-di-nha
                    ('G', 2, 0.5), ('G', 2, 0.5), ('B', 1, 0.5), ('B', 1, 0.5),
                    # Va-mos to-dos ci-ran-dar
                    ('G', 3, 0.5), ('G', 2, 0.5), ('G', 0, 0.5), ('B', 1, 0.5), ('G', 2, 0.5), ('G', 0, 0.5), ('D', 3, 1),
                    # Va-mos dar a meia vol-ta
                    ('G', 2, 0.5), ('B', 1, 0.5), ('G', 3, 0.5), ('G', 2, 0.5), ('G', 0, 0.5), ('D', 3, 0.5), ('D', 2, 0.5), ('A', 3, 0.5),
                    # volta e meia va-mos dar
                    ('G', 2, 0.5), ('D', 3, 0.5), ('G', 0, 0.5), ('D', 2, 0.5), ('D', 3, 0.5), ('D', 2, 0.5), ('D', 3, 0.5)
                ]
            },
            "7": {
                "titulo": "O Cravo Brigou com a Rosa",
                "bpm": 115,
                "compasso": (3, 4),
                "seq": [
                    # PARTE 1: "O cra-vo bri-gou com a ro-sa"
                    ('G', 0, 1), ('G', 0, 1),  # O cra
                    ('D', 2, 0.5), ('B', 1, 0.5),  # vo bri
                    ('B', 0, 0.5), ('G', 2, 0.5),  # gou com
                    ('G', 0, 1), ('D', 3, 1.0),  # a ro-sa (Lá)

                    # PARTE 2: "De-bai-xo de u-ma sa-ca-da"
                    ('G', 2, 1), ('G', 2, 1),  # De-bai
                    ('D', 3, 0.5), ('B', 1, 0.5),  # xo de_u
                    ('B', 0, 0.5), ('G', 2, 0.5),  # ma sa
                    ('G', 0, 2), ('G', 0, 1),  # ca-da (Sol)

                    # PARTE 3: "O cra-vo sa-iu fe-ri-do"
                    ('B', 1, 1), ('B', 1, 0.5),  # O cra
                    ('B', 1, 0.5), ('B', 3, 0.5),  # vo sa
                    ('B', 1, 0.5), ('B', 0, 1),  # iu fe
                    ('G', 2, 1.0),  # ri-do (Lá)

                    # PARTE 4: "E a ro-sa des-pe-da-ça-da"
                    ('G', 2, 1), ('G', 0, 1),  # E_a ro
                    ('B', 0, 0.5), ('G', 2, 0.5),  # sa des
                    ('D', 3, 0.5), ('D', 0, 0.5),  # pe-da
                    ('A', 3, 2.0)  # ça-da (Sol final)
                ]
            },
            "8": {
                "titulo": "Cai Cai Balão",
                "bpm": 100,
                "compasso": (2, 4),
                "seq": [
                    # PARTE 1: "Cai cai ba-lão"
                    ('G', 0, 1), ('G', 0, 1.5),  # Cai cai
                    ('D', 3, 0.5), ('D', 2, 1),  # ba-lão (Ré Dó)
                    # PARTE 2: "Cai cai ba-lão" (Repete)
                    ('G', 0, 1), ('G', 0, 1.5),
                    ('D', 3, 0.5), ('D', 2, 1),
                    # PARTE 3: "A-qui na mi-nha mão"
                    ('G', 0, 1), ('G', 2, 1),  # A-qui
                    ('G', 0, 1), ('D', 3, 1),  # na mi
                    ('D', 2, 1), ('D', 0, 2),  # nha mão (Si)
                    # PARTE 4: "Não cai não"
                    ('D', 0, 0.5), ('D', 2, 0.5),  # Não cai
                    ('D', 3, 1.0),  # não (Lá)
                    # PARTE 5: "Não cai não"
                    ('D', 0, 0.5), ('D', 2, 0.5),  # Não cai
                    ('D', 3, 1.0),  # não (Sol)
                    # PARTE 6: "Não cai não"
                    ('D', 0, 0.5), ('D', 2, 0.5),  # Não cai
                    ('D', 3, 2),  # não (Fá Natural)
                    # PARTE 7: "Cai na ru-a do sa-bão"
                    ('G', 0, 1), ('G', 2, 1),  # Cai na
                    ('G', 0, 1), ('D', 3, 1),  # ru-a
                    ('D', 2, 1), ('D', 0, 1),  # do sa- (Dó final)
                    ('A', 3, 2)  # bão
                ]
            },
            "9": {
                "titulo": "A Dona Aranha",
                "bpm": 120,
                "compasso": (4, 4),
                "seq": [
                    # PARTE 1: "A do-na a-ra-nha su-biu pe-la pa-re-de"
                    ('B', 1, 2), ('B', 1, 1), ('B', 3, 1),  # A do-na a-
                    ('e', 0, 2), ('e', 0, 1), ('e', 0, 1),  # ra-nha su-
                    ('B', 3, 1), ('B', 1, 1), ('B', 3, 1), ('e', 0, 1),  # biu pe-la pa-
                    ('B', 1, 2), ('B', 1, 2),  # re-de
                    # PARTE 2: "Veio a chu-va for-te e a de-rru-bou"
                    ('B', 1, 1), ('B', 1, 1), ('B', 1, 1), ('B', 3, 1),  # Veio a chu-va
                    ('e', 0, 2), ('e', 0, 2),  # for-te
                    ('B', 3, 1), ('B', 1, 1), ('B', 3, 1), ('e', 0, 1.0),  # e a de-rru-
                    ('B', 1, 4),
                    # PARTE 3: "Já pa-ssou a chu-va e o Sol já vai sur-gin-do"
                    ('e', 5, 1), ('e', 5, 1), ('e', 5, 1), ('e', 5, 1),  # Já pa-ssou a
                    ('e', 3, 2), ('B', 1, 2),  # chu-va
                    ('e', 5, 1), ('e', 5, 1), ('e', 5, 1), ('e', 5, 1),  # Já pa-ssou a
                    ('e', 3, 2), ('B', 1, 2),  # chu-va
                    ('B', 1, 1), ('B', 1, 1), ('B', 1, 1), ('B', 3, 1),  # e o Sol já vai
                    ('e', 0, 1), ('e', 0, 1), ('e', 0, 1), ('e', 0, 1),  # sur-gin-do
                    ('B', 3, 1), ('B', 1, 1), ('B', 3, 1), ('e', 0, 1),
                    ('B', 1, 2), ('B', 1, 2)
                ]
            },
            "10": {
                "titulo": "Baby Shark",
                "bpm": 116,
                "compasso": (2, 4),
                "seq": [
                    # --- PARTE 1: "Ba-by Shark doo doo doo..." ---
                    ('B', 3, 1.0), ('e', 0, 1.0),  # Ba-by (Ré Mi)
                    # O "doo doo doo..." são 7 notas rápidas (Sol)
                    ('e', 3, 0.5), ('e', 3, 0.5), ('e', 3, 0.5), ('e', 3, 0.25),
                    ('e', 3, 0.5), ('e', 3, 0.25), ('e', 3, 0.5),
                    ('B', 3, 0.5), ('e', 0, 0.5),
                    # --- PARTE 2: Repete a mesma frase ---
                    ('e', 3, 0.5), ('e', 3, 0.5), ('e', 3, 0.5), ('e', 3, 0.25),
                    ('e', 3, 0.5), ('e', 3, 0.25), ('e', 3, 0.5),
                    ('B', 3, 0.5), ('e', 0, 0.5),
                    # --- PARTE 3: Repete mais uma vez ---
                    ('e', 3, 0.5), ('e', 3, 0.5), ('e', 3, 0.5), ('e', 3, 0.25),
                    ('e', 3, 0.5), ('e', 3, 0.25), ('e', 3, 0.5),
                    ('e', 3, 0.5), ('e', 3, 0.5),
                    # --- PARTE 4: "Ba-by Shark!" (Finalização) ---
                    ('e', 2, 2)
                ]
            }
        }

    def get_song(self, song_id):
        return self._songs.get(song_id)

    def get_all(self):
        return self._songs.items()


# ==============================================================================
# 4. OBJETO VISUAL 3D (Z-ORDER CORRIGIDO)
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
        # Calcular progresso (0 = Hit, 1 = Horizonte)
        time_diff = self.tempo_alvo - current_time
        progress = time_diff / (Config.START_DELAY / 1000.0)

        # Só desenha se estiver no campo de visão
        if -0.1 < progress < 1.1:
            x, y, scale = Config.project_coordinates(self.corda, progress)
            w = int(60 * scale)
            h = int(30 * scale)

            # Centro da nota
            center_pos = (x, y)

            # ==============================================================
            # CAMADA 1: RASTRO/SUSTAIN (FUNDO)
            # Desenha isso PRIMEIRO para ficar atrás da nota
            # ==============================================================
            if self.duracao > 0.2:
                end_time_diff = (self.tempo_alvo + self.duracao) - current_time
                end_progress = end_time_diff / (Config.START_DELAY / 1000.0)

                # Se o final do sustain ainda está na "estrada"
                if end_progress < 1.2:
                    # Se o sustain for muito longo e passar do horizonte, clamp em 1.0
                    draw_end_progress = min(end_progress, 1.0)
                    end_x, end_y, _ = Config.project_coordinates(self.corda, draw_end_progress)

                    # Espessura do rastro (mais fino que a nota)
                    tail_width = int(12 * scale)
                    if tail_width < 2: tail_width = 2

                    pygame.draw.line(surface, self.cor, (x, y), (end_x, end_y), tail_width)

            # ==============================================================
            # CAMADA 2: CORPO DA NOTA (MEIO)
            # ==============================================================
            if self.casa == 0:
                # CORDA SOLTA: Barra Horizontal Larga (Estilo Rocksmith)
                # Não usamos mais o quadrado branco. Usamos a cor da corda.
                bar_w = int(Config.BOTTOM_WIDTH / 6 * scale * 0.9)  # Quase a largura da pista
                bar_h = int(8 * scale)
                if bar_h < 3: bar_h = 3

                bar_rect = pygame.Rect(x - bar_w // 2, y - bar_h // 2, bar_w, bar_h)

                # Barra sólida colorida
                pygame.draw.rect(surface, self.cor, bar_rect, border_radius=2)
                # Brilho branco no centro
                pygame.draw.rect(surface, (255, 255, 255), (x - bar_w // 4, y - 1, bar_w // 2, 2))

            else:
                # NOTA NORMAL: Gem (Retângulo Arredondado)
                rect = pygame.Rect(x - w // 2, y - h // 2, w, h)
                pygame.draw.rect(surface, self.cor, rect, border_radius=5)
                # Borda branca para destacar
                pygame.draw.rect(surface, Config.WHITE, rect, 2, border_radius=5)

            # ==============================================================
            # CAMADA 3: NÚMERO (FRENTE)
            # ==============================================================
            if self.casa > 0:
                font_size = int(24 * scale)
                if font_size > 10:
                    font = pygame.font.SysFont("Arial", font_size, bold=True)
                    # Texto preto para contraste
                    text = font.render(str(self.casa), True, Config.BLACK)
                    surface.blit(text, text.get_rect(center=(x, y)))


# ==============================================================================
# 5. JOGO PRINCIPAL (HIGHWAY)
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
            self._draw_highway(screen)
            title = self.font.render(data['titulo'], True, Config.WHITE)
            screen.blit(title, (20, 20))

            active_strings = []
            for n in notes:
                n.update(current)
                n.draw_3d(screen, current)
                if n.ativa: active_strings.append(n.corda)

            for s in list(set(active_strings)):
                x_near, y_near, _ = Config.project_coordinates(s, 0.0)
                x_far, y_far, _ = Config.project_coordinates(s, 1.0)
                c = Config.get_string_color(s)
                pygame.draw.line(screen, Config.WHITE, (x_near, y_near), (x_far, y_far), 4)
                pygame.draw.circle(screen, c, (x_near, y_near), 15)
                pygame.draw.circle(screen, Config.WHITE, (x_near, y_near), 10)

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