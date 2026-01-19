from pydub import AudioSegment, effects
from pydub.silence import detect_leading_silence
import os
import numpy as np  # Necessário se for usar arrays em algum momento, mas aqui é pydub


# ==============================================================================
# 2. MOTOR DE ÁUDIO (SAMPLES REAIS + FIX WINDOWS + PITCH SHIFT)
# ==============================================================================
class AudioEngine:
    _samples_cache = {}

    @staticmethod
    def _trim_silence(audio, silence_threshold=-40.0, chunk_size=10):
        """
        Corta o silêncio inicial para evitar LAG no jogo.
        O áudio deve começar exatamente no ataque da corda.
        """
        trim_ms = detect_leading_silence(audio, silence_threshold=silence_threshold, chunk_size=chunk_size)
        # Deixa uma margemzinha minúscula (5ms) para não cortar o ataque transitório
        trim_ms = max(0, trim_ms - 5)
        return audio[trim_ms:]

    @staticmethod
    def load_string_sample(string_name):
        """Carrega, limpa e normaliza o sample."""
        if string_name in AudioEngine._samples_cache:
            return AudioEngine._samples_cache[string_name]

        # --- CORREÇÃO DO WINDOWS (Case Insensitive) ---
        file_map = {
            'e': 'e_aguda.wav',  # Mizinha (renomeie o arquivo na pasta para e_aguda.wav)
            'E': 'E.wav'  # Mizona
        }

        # Define o nome do arquivo alvo
        target_file = file_map.get(string_name, f"{string_name}.wav")

        # Lista de tentativas (WAV preferido, M4A backup)
        options = [
            f"samples/{target_file}",
            f"samples/{string_name}.m4a"
        ]

        audio = None
        for path in options:
            if os.path.exists(path):
                try:
                    audio = AudioSegment.from_file(path)
                    # print(f"   > Carregado: {path}") # Descomente para debug
                    break
                except Exception as e:
                    print(f"   > Erro ao ler {path}: {e}")

        if audio:
            # --- TRATAMENTO AUTOMÁTICO ---
            audio = audio.set_channels(1)
            audio = AudioEngine._trim_silence(audio)

            # Filtros para limpar ruído de celular
            audio = audio.high_pass_filter(80)  # Tira "pups" graves
            audio = audio.low_pass_filter(6000)  # Tira chiado muito agudo

            audio = effects.normalize(audio)

            AudioEngine._samples_cache[string_name] = audio
            return audio
        else:
            print(f"!!! ARQUIVO NÃO ENCONTRADO PARA CORDA: {string_name}")
            if string_name == 'e':
                print("    (Lembre-se de renomear a mizinha para 'e_aguda.wav' na pasta samples)")
            return None

    @staticmethod
    def pitch_shift(audio_segment, semitones):
        """
        Altera a afinação mudando a taxa de amostragem (Sample Rate).
        Simula a física real de encurtar a corda no traste.
        """
        if semitones == 0:
            return audio_segment

        # Calcula novo sample rate para mudar o tom
        new_rate = int(audio_segment.frame_rate * (2.0 ** (semitones / 12.0)))

        # Cria novo áudio com taxa alterada
        shifted = audio_segment._spawn(audio_segment.raw_data, overrides={'frame_rate': new_rate})

        # Retorna para taxa padrão (44100) para poder mixar com o resto
        return shifted.set_frame_rate(44100)

    @staticmethod
    def generate_wav(sequence, bpm, filename="temp_music.wav"):
        try:
            # Cria base de silêncio
            song_audio = AudioSegment.silent(duration=100)
            ms_per_beat = (60.0 / bpm) * 1000.0
            current_pos_ms = 500  # 0.5s de margem inicial

            print("   > Renderizando áudio com samples...")

            for item in sequence:
                string, fret, beats = item
                duration_ms = beats * ms_per_beat

                if string == 'PAUSA':
                    current_pos_ms += duration_ms
                else:
                    # 1. Carrega Sample
                    base_sample = AudioEngine.load_string_sample(string)

                    if base_sample:
                        # 2. Muda o Tom (Pitch Shift)
                        # AQUI ESTAVA O ERRO: A função pitch_shift precisa existir na classe
                        note_audio = AudioEngine.pitch_shift(base_sample, fret)

                        # 3. Ajuste de Duração
                        play_duration = duration_ms + 150  # Sustain extra

                        # Fade out se for muito longo
                        if len(note_audio) > play_duration + 200:
                            note_audio = note_audio[:play_duration + 200].fade_out(150)

                        # 4. Mixagem (Aumenta o canvas se precisar)
                        if current_pos_ms + len(note_audio) > len(song_audio):
                            padding = (current_pos_ms + len(note_audio)) - len(song_audio) + 500
                            song_audio += AudioSegment.silent(duration=padding)

                        # Cola a nota (reduz volume levemente para não estourar na soma)
                        song_audio = song_audio.overlay(note_audio - 1.5, position=int(current_pos_ms))

                    current_pos_ms += duration_ms

            # Salva
            song_audio.export(filename, format="wav")
            return filename

        except Exception as e:
            print(f"Erro no AudioEngine: {e}")
            import traceback
            traceback.print_exc()
            return None