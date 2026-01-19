from pydub import AudioSegment, effects
from pydub.silence import detect_leading_silence
import os
import numpy as np  # Necessário se for usar arrays em algum momento, mas aqui é pydub

from Config import Config


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