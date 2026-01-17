# ==============================================================================
# 2. MOTOR DE ÁUDIO
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
    def generate_wav(sequence, bpm, filename="temp_music.wav"):
        try:
            sample_rate = 44100
            audio_data = []
            seconds_per_beat = 60.0 / bpm

            for item in sequence:
                string, fret, beats = item
                duration = beats * seconds_per_beat
                if duration <= 0: duration = 0.1

                t = np.linspace(0, duration, int(sample_rate * duration), False)

                if string == 'PAUSA':
                    wave_chunk = np.zeros_like(t)
                else:
                    freq = AudioEngine._get_freq(string, fret)
                    envelope = np.exp(-4 * t)
                    tone = np.sin(2 * np.pi * freq * t)
                    wave_chunk = tone * envelope * 0.5

                audio_data.append(wave_chunk)

            if not audio_data: return None

            audio_concat = np.concatenate(audio_data)
            audio_int16 = (audio_concat * 32767).astype(np.int16)

            with wave.open(filename, 'w') as wav_file:
                wav_file.setnchannels(1)
                wav_file.setsampwidth(2)
                wav_file.setframerate(sample_rate)
                wav_file.writeframes(audio_int16.tobytes())

            return filename
        except Exception as e:
            print(f"Erro no AudioEngine: {e}")
            return None