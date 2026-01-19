# ==============================================================================
# 2. MOTOR DE ÁUDIO (KARPLUS-STRONG - VERSÃO GRAVE/BASS BOOST)
# ==============================================================================
import wave

import numpy as np

from Config import Config


class AudioEngine:
    @staticmethod
    def _get_freq(string, fret):
        base = Config.FREQS.get(string, 0)
        return base * (2 ** (fret / 12.0))

    @staticmethod
    def karplus_strong(freq, duration, sample_rate=44100):
        """
        Gera som com física de corda, ajustado para timbre mais grave/encorpado.
        """
        N = int(sample_rate / freq)

        # 1. Excitação Inicial (O "Pluck")
        buf = np.random.uniform(-1, 1, N)

        # --- BASS BOOST TRICK 1: Suavizar o ataque ---
        # Passamos um filtro no ruído inicial para simular tocar com o dedo (mais grave)
        # em vez de palheta (muito agudo/estalo).
        for _ in range(4):  # Repetir 4x remove bem os agudos iniciais
            buf = 0.5 * (buf + np.roll(buf, 1))

        n_samples = int(sample_rate * duration)
        samples = np.zeros(n_samples)

        idx = 0
        # Decay mais alto (0.997) aumenta o sustain (comum em cordas graves)
        decay = 0.997

        # Variável para o filtro de saída (Low Pass)
        last_output = 0

        for i in range(n_samples):
            # Algoritmo Karplus-Strong Padrão
            current_sample = buf[idx]
            next_sample = buf[(idx + 1) % N]

            # Média (filtro da corda)
            new_val = 0.5 * (current_sample + next_sample)
            buf[idx] = new_val * decay
            idx = (idx + 1) % N

            # --- BASS BOOST TRICK 2: Filtro de Tom na Saída ---
            # Funciona como um equalizador cortando frequências altas
            # Mistura 60% do som atual com 40% do som anterior (suavização)
            output = 0.6 * current_sample + 0.4 * last_output
            last_output = output

            samples[i] = output

        return samples

    @staticmethod
    def generate_wav(sequence, bpm, filename="temp_music.wav"):
        try:
            sample_rate = 44100
            audio_data = []
            seconds_per_beat = 60.0 / bpm

            # Silêncio inicial para garantir buffer de áudio
            audio_data.append(np.zeros(int(sample_rate * 0.1)))

            for item in sequence:
                string, fret, beats = item
                duration = beats * seconds_per_beat
                # Sustain extra para dar corpo ao som
                sustain_duration = duration + 0.25

                if string == 'PAUSA':
                    wave_chunk = np.zeros(int(sample_rate * duration))
                else:
                    freq = AudioEngine._get_freq(string, fret)
                    wave_chunk = AudioEngine.karplus_strong(freq, sustain_duration, sample_rate)

                    # Lógica de corte suave (Fade Out)
                    target_len = int(sample_rate * duration)
                    if len(wave_chunk) > target_len:
                        fade_len = 300
                        wave_chunk = wave_chunk[:target_len]
                        if len(wave_chunk) > fade_len:
                            wave_chunk[-fade_len:] *= np.linspace(1, 0, fade_len)
                    else:
                        padding = np.zeros(target_len - len(wave_chunk))
                        wave_chunk = np.concatenate((wave_chunk, padding))

                audio_data.append(wave_chunk)

            if not audio_data: return None

            audio_concat = np.concatenate(audio_data)

            # Normalização Segura
            max_val = np.max(np.abs(audio_concat))
            if max_val > 0:
                # Volume a 95% para garantir presença
                audio_concat = audio_concat / max_val * 0.95

            audio_int16 = (audio_concat * 32767).astype(np.int16)

            with wave.open(filename, 'w') as wav_file:
                wav_file.setnchannels(1)
                wav_file.setsampwidth(2)
                wav_file.setframerate(sample_rate)
                wav_file.writeframes(audio_int16.tobytes())

            return filename
        except Exception as e:
            print(f"Erro no AudioEngine: {e}")
            # Import traceback apenas se der erro para debug
            import traceback
            traceback.print_exc()
            return None