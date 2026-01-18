import random
import wave

import numpy as np

from Config import Config


# ==============================================================================
# 2. MOTOR DE ÁUDIO (KARPLUS-STRONG - SÍNTESE FÍSICA)
# ==============================================================================
class AudioEngine:
    @staticmethod
    def _get_freq(string, fret):
        base = Config.FREQS.get(string, 0)
        return base * (2 ** (fret / 12.0))

    @staticmethod
    def karplus_strong(freq, duration, sample_rate=44100):
        """
        Gera o som de uma corda vibrando usando o algoritmo Karplus-Strong.
        Isso cria um som de violão muito mais realista.
        """
        N = int(sample_rate / freq)
        # Inicializa com ruído branco (o "ataque" da palheta)
        buf = np.random.uniform(-1, 1, N)

        n_samples = int(sample_rate * duration)
        samples = np.zeros(n_samples)

        # Ponteiro atual no buffer
        idx = 0

        # Fator de decaimento (simula a perda de energia da corda)
        # 0.990 a 0.999 (quanto maior, mais "aço" e sustain tem a corda)
        decay = 0.996

        for i in range(n_samples):
            samples[i] = buf[idx]
            # Média entre o ponto atual e o anterior (filtro passa-baixa simples)
            avg = 0.5 * (buf[idx] + buf[(idx + 1) % N])
            # Atualiza o buffer com o decaimento
            buf[idx] = avg * decay
            idx = (idx + 1) % N

        return samples

    @staticmethod
    def generate_wav(sequence, bpm, filename="temp_music.wav"):
        try:
            sample_rate = 44100
            audio_data = []
            seconds_per_beat = 60.0 / bpm

            # Adiciona um pequeno silêncio no início para garantir sincronia
            audio_data.append(np.zeros(int(sample_rate * 0.1)))

            for item in sequence:
                string, fret, beats = item
                duration = beats * seconds_per_beat
                # Deixar a nota soar um pouco mais que a duração (overlap) dá mais realismo
                sustain_duration = duration + 0.2

                if string == 'PAUSA':
                    wave_chunk = np.zeros(int(sample_rate * duration))
                else:
                    freq = AudioEngine._get_freq(string, fret)
                    # Gera som com física de corda
                    wave_chunk = AudioEngine.karplus_strong(freq, sustain_duration, sample_rate)

                    # Corta se ficar muito longo, mas idealmente mixaria (overlap)
                    # Aqui vamos cortar suavemente para simplificar a lógica de lista
                    target_len = int(sample_rate * duration)
                    if len(wave_chunk) > target_len:
                        # Fade out rápido no final para não "clicar"
                        fade_len = 200
                        wave_chunk = wave_chunk[:target_len]
                        if len(wave_chunk) > fade_len:
                            wave_chunk[-fade_len:] *= np.linspace(1, 0, fade_len)
                    else:
                        # Se for curto, preenche com silêncio (padding)
                        padding = np.zeros(target_len - len(wave_chunk))
                        wave_chunk = np.concatenate((wave_chunk, padding))

                audio_data.append(wave_chunk)

            if not audio_data: return None

            audio_concat = np.concatenate(audio_data)

            # Normalização (para o volume ficar bom e não estourar)
            max_val = np.max(np.abs(audio_concat))
            if max_val > 0:
                audio_concat = audio_concat / max_val * 0.9

            audio_int16 = (audio_concat * 32767).astype(np.int16)

            with wave.open(filename, 'w') as wav_file:
                wav_file.setnchannels(1)
                wav_file.setsampwidth(2)
                wav_file.setframerate(sample_rate)
                wav_file.writeframes(audio_int16.tobytes())

            return filename
        except Exception as e:
            print(f"Erro no AudioEngine: {e}")
            import traceback
            traceback.print_exc()
            return None