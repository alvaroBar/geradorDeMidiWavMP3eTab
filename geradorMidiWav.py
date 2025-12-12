import struct
import math
import wave
import os
import sys
import time

try:
    import pygame
    import numpy as np
    from pydub import AudioSegment
except ImportError:
    print("ERRO: Faltam bibliotecas. Instale: pip install pygame numpy pydub")
    sys.exit()

# ==============================================================================
# CONFIGURAÇÕES E BIBLIOTECA
# ==============================================================================
BPM_PADRAO = 110

NOTAS_FREQ = {
    'E': 82.41, 'A': 110.00, 'D': 146.83,
    'G': 196.00, 'B': 246.94, 'e': 329.63
}

BIBLIOTECA_MUSICAS = {
    "1": {
        "titulo": "Sapo Cururu",
        "bpm": 110,
        "compasso": (2, 4),  # 2/4 (Binário Simples)
        "seq": [
            # Notas do Sapo... (Mantive a última versão corrigida)
            ('G', 0, 0.5), ('G', 2, 0.5), ('G', 0, 0.5), ('D', 2, 0.5), ('B', 1, 2.0),
            ('G', 0, 0.5), ('G', 2, 0.5), ('G', 0, 0.5), ('D', 2, 0.5), ('B', 1, 2.0),
            ('e', 0, 0.5), ('e', 0, 0.5), ('B', 3, 0.5), ('e', 0, 0.5),
            ('e', 1, 0.5), ('B', 3, 0.35), ('B', 0, 0.35), ('G', 0, 1.75),
            ('PAUSA', 0, 0.5),
            ('B', 0, 0.5), ('B', 0, 0.5), ('G', 2, 0.5), ('B', 0, 0.5), ('B', 1, 3.5)
        ]
    },
    "2": {
        "titulo": "Parabéns pra Você (Completo)",
        "bpm": 100,
        "compasso": (3, 4), # 3/4 (Ritmo de Valsa)
        "seq": [
            # --- PARTE 1: "Pa-ra-béns pra vo-cê" ---
            # Notas: Sol Sol Lá Sol Dó Si
            ('G', 0, 0.75), ('G', 0, 0.25), # Pa-ra
            ('G', 2, 1.0),  ('G', 0, 1.0),  # béns pra
            ('B', 1, 1.0),  ('B', 0, 2.0),  # vo-cê

            # --- PARTE 2: "Nes-sa da-ta que-ri-da" ---
            # Notas: Sol Sol Lá Sol Ré Dó
            ('G', 0, 0.75), ('G', 0, 0.25), # Nes-sa
            ('G', 2, 1.0),  ('G', 0, 1.0),  # da-ta
            ('B', 3, 1.0),  ('B', 1, 2.0),  # queri-da

            # --- PARTE 3: "Mui-tas fe-li-ci-da-des" ---
            # Notas: Sol Sol Sol(Agudo) Mi Dó Si Lá
            ('G', 0, 0.75), ('G', 0, 0.25), # Mui-tas
            ('e', 3, 1.0),  # fe (Sol Agudo - Mizinha casa 3)
            ('e', 0, 1.0),  # li (Mi solto)
            ('B', 1, 1.0),  # ci (Dó)
            ('B', 0, 1.0),  # da (Si)
            ('G', 2, 2.0),  # des (Lá)

            # --- PARTE 4: "Mui-tos a-nos de vi-da" ---
            # Notas: Fá Fá Mi Dó Ré Dó
            # Obs: Fá Natural (Casa 1 da Mizinha)
            ('e', 1, 0.75), ('e', 1, 0.25), # Mui-tos (Fá Fá)
            ('e', 0, 1.0),  # a (Mi)
            ('B', 1, 1.0),  # nos (Dó)
            ('B', 3, 1.0),  # de (Ré)
            ('B', 1, 2.0)   # vi-da (Dó Final)
        ]
    },
    "3": {
        "titulo": "Marcha Soldado (Oficial)",
        "bpm": 110,
        "compasso": (2, 4),  # 2/4 (Binário de Marcha)
        "seq": [
            # Em 2/4, 1 tempo = semínima.
            # Aqui estamos usando 0.5 (colcheia) e 1.0 (semínima)

            # PARTE 1: Mar-cha sol-da-do (Sol Sol Mi Do Sol)
            ('e', 3, 1), ('e', 3, 0.5),  # Mar-cha (Sol Sol)
            ('e', 0, 0.5), ('B', 1, 1),  # sol-da  (Mi Dó)
            ('B', 1, 0.5),  # do      (Sol Grave)

            # PARTE 2: Ca-be-ça de pa-pel (Sol Sol Sol Mi Ré)
            # Melodia exata: G G G E D
            ('e', 0, 0.5), ('e',3, 0.5),  # Ca-be (Sol Sol)
            ('e', 3, 0.5), ('e', 3, 0.5),  # ça de (Sol Mi)
            ('e', 0, 0.5), ('B', 3, 1.5), # pa-pel (Ré - Longa)

            # PARTE 3: Quem não mar-char di-rei-to (Sol Sol Mi Fá Fá Mi Ré)
            ('e', 1, 0.5), ('e', 1, 0.5),  # Quem não
            ('e', 1, 0.5), ('e', 0, 0.5),  # mar-char (Mi Fá)
            ('B', 3, 0.5), ('e', 3, 1),  # di-rei (Fá Mi)
            ('e', 3, 0.5),  # to (Ré)

            # PARTE 4: Vai pre-so pro quar-tel (Ré Ré Ré Mi Fá Ré Dó)
            ('e', 5, 0.5), ('e', 3, 0.5),  # Vai pre
            ('e', 1, 0.5), ('e', 0, 0.5),  # so pro (Ré Mi)
            ('B', 3, 0.5), ('B', 1, 1),  # quar-tel (Fá Ré)

            # PARTE 5: O quartel pegou fogo
            ('B', 1, 0.5), ('e', 0, 0.5), ('e',3,1),  # O quar-tel
            ('e', 3, 0.5), ('e', 0, 0.5), ('B',1,1), # Pegou fo
            ('B', 1, 0.5),  # go

            # PARTE 5: São Francisco deu sinal
            ('e', 0, 0.5), ('e',3, 0.5),  # São-fran
            ('e', 3, 0.5), ('e', 3, 0.5),  # cis-co de (Sol Mi)
            ('e', 0, 0.5), ('B', 3, 1.5), # deu-sinal (Ré - Longa)

            # PARTE 6: Acode acode acode
            ('e', 1, 0.5), ('e', 1, 0.5),  # A-co
            ('e', 1, 0.5), ('e', 0, 0.5),  # de A
            ('B', 3, 0.5), ('e', 3, 1),  # co-de
            ('e', 3, 0.5),  # to (Ré)

            # PARTE 7: A bandeira nacional
            ('e', 5, 0.5), ('e', 3, 0.5),  # A ban-
            ('e', 1, 0.5), ('e', 0, 0.5),  # dei-ra
            ('B', 3, 0.5), ('B', 1, 1),  # na-cional (Fá Ré)


        ]
    },

"4": {
        "titulo": "Brilha Brilha Estrelinha",
        "bpm": 100,
        "compasso": (4, 4), # 4/4 (Tempo Comum)
        "seq": [
            # PARTE 1: "Bri-lha bri-lha es-tre-li-nha"
            # Notas: Sol Sol Ré Ré Mi Mi Ré
            # Usa corda Sol solta, Si presa na 3, e Mizinha solta
            ('G', 0, 1.0), ('G', 0, 1.0),  # Bri-lha (Sol)
            ('B', 3, 1.0), ('B', 3, 1.0),  # bri-lha (Ré)
            ('e', 0, 1.0), ('e', 0, 1.0),  # es-tre  (Mi)
            ('B', 3, 2.0),                 # li-nha  (Ré - Longa)

            # PARTE 2: "Que-ro ver vo-cê bri-lhar"
            # Notas: Dó Dó Si Si Lá Lá Sol
            # Desce a escala usando corda Si casa 1, Si solta, Sol casa 2, Sol solta
            ('B', 1, 1.0), ('B', 1, 1.0),  # Que-ro (Dó)
            ('B', 0, 1.0), ('B', 0, 1.0),  # ver vo (Si)
            ('G', 2, 1.0), ('G', 2, 1.0),  # cê bri (Lá)
            ('G', 0, 2.0),                 # lhar   (Sol - Longa)

            # PARTE 3: "Faz de con-ta queé só mi-nha"
            # Notas: Ré Ré Dó Dó Si Si Lá
            # O "Refrão" do meio
            ('B', 3, 1.0), ('B', 3, 1.0),  # Faz de (Ré)
            ('B', 1, 1.0), ('B', 1, 1.0),  # con-ta (Dó)
            ('B', 0, 1.0), ('B', 0, 1.0),  # queé só (Si)
            ('G', 2, 2.0),                 # mi-nha  (Lá - Longa)

            # PARTE 4: "Pa-ra sem-pre te a-mar"
            # Repete a melodia da Parte 3 exata
            ('B', 3, 1.0), ('B', 3, 1.0),  # Pa-ra
            ('B', 1, 1.0), ('B', 1, 1.0),  # sem-pre
            ('B', 0, 1.0), ('B', 0, 1.0),  # te a
            ('G', 2, 2.0),                 # mar

            # PARTE 5: Repete o Início (Parte 1)
            ('G', 0, 1.0), ('G', 0, 1.0),
            ('B', 3, 1.0), ('B', 3, 1.0),
            ('e', 0, 1.0), ('e', 0, 1.0),
            ('B', 3, 2.0),

            # PARTE 6: Repete a Descida (Parte 2)
            ('B', 1, 1.0), ('B', 1, 1.0),
            ('B', 0, 1.0), ('B', 0, 1.0),
            ('G', 2, 1.0), ('G', 2, 1.0),
            ('G', 0, 2.0)
        ]
    },

    "5": {
        "titulo": "Atirei o Pau no Gato",
        "bpm": 130,  # É uma música bem rapidinha
        "compasso": (2, 4),
        "seq": [
            # PARTE 1: "A-ti-rei o pau no ga-to-to"
            # Notas: Sol Fá Mi | Ré Mi Fá Sol | Sol Sol
            ('G', 0, 1.5), ('D', 3, 0.5), ('D', 2, 0.5),  # A-ti-rei (Sol Fá Mi)
            ('D', 0, 0.5), ('D', 2, 0.5), ('D', 3, 0.5), ('G', 0, 1),  # o pau no ga
            ('G', 0, 1), ('G', 0, 1.0),  # to-to

            # PARTE 2: "Mas o ga-to-to"
            # Notas: Sol Sol Lá Lá
            ('G', 2, 0.5), ('G', 0, 0.5),  # Mas o
            ('D', 3, 1), ('D', 3, 1.0), ('D', 3, 1.0), # ga-to (Lá)

            # PARTE 3: "Não mor-reu-reu-reu"
            # Notas: Fá Fá Sol Sol
            ('G', 0, 0.5), ('D', 3, 0.5),  # Não mo-
            ('D', 2, 1), ('D', 2, 1.0), ('D',2, 1.0),  # reu-reu-reu

            # PARTE 4: "Do-na Chi-ca-ca"
            # Notas: Mi Mi Fá Fá
            ('A', 3, 0.5), ('A', 3, 0.5),  # Do-na
            ('G', 2, 1), ('G', 2, 1.0), ('G', 2, 1.0),  # Chi-ca (Fá)

            # PARTE 5: "Ad-mi-rou-se-se"
            # Notas: Ré Ré Mi Mi
            ('B', 0, 0.5), ('G', 2, 0.5),  # Ad-mi
            ('G', 0, 1), ('G', 0, 1.0), ('G', 0, 1.0),  # rou-se (Mi)

            # PARTE 6: "Do ber-ro, do ber-ro que o ga-to deu"
            # Notas: Dó Dó Lá Lá | Sol Sol Fá Mi Ré Dó
            # Aqui usamos a corda Si (Dó agudo) e descemos até a corda Lá (Dó grave)

            ('D', 2, 0.5), ('D', 3, 0.5),  # Do ber (Dó Agudo)
            ('G', 0, 1),   # ro, do (Lá)

            ('D', 2, 0.5), ('D', 3, 0.5),  # Do ber (Dó Agudo)
            ('G', 0, 1),   # ro, do (Lá)

            ('D', 2, 0.5), ('D', 3, 0.5),  # ber-ro (Lá Sol)
            ('G', 0, 0.5), ('D', 3, 0.5),  # que o (Fá Mi)
            ('D', 2, 0.5), ('D', 0, 0.5), ('A', 3, 2.0)  # gato deu (Ré -> Dó Grave na corda A)
        ]
    },
    "6": {
        "titulo": "Ciranda Cirandinha",
        "bpm": 110,
        "compasso": (2, 4),  # 2/4 (Marcha / Cantiga)
        "seq": [
            # PARTE 1: "Ci-ran-da, Ci-ran-di-nha"
            # Notas: Dó Ré Mi | Ré Mi Fá Sol
            ('G', 0, 1), ('B', 1, 0.5), ('B', 1, 0.5),  # Ci-ran-da (Dó Ré Mi)
            ('e', 0, 0.5), ('e', 0, 0.5), ('e', 3, 0.5), ('e', 3, 0.5),  # Ci-ran-di-nha (Ré Mi Fá Sol)

            # PARTE 2: "Va-mos to-dos ci-ran-dar"
            # Notas: Fá Fá Mi Mi | Ré Ré Dó
            ('e', 1, 0.5), ('e', 0, 0.5),  # Va-mos (Fá Fá)
            ('B', 3, 0.5), ('e', 3, 0.5),  # to-dos (Mi Mi)
            ('e', 0, 0.5), ('B', 3, 0.5),  # ci-ran (Ré Ré)
            ('B', 1, 1.0),  # dar    (Dó)

            # PARTE 3: "Va-mos dar a mei-a vol-ta"
            # Notas: Sol Sol Fá Fá | Mi Mi Ré
            # Aqui sobe para a nota Sol aguda (Mizinha casa 3)
            ('e', 0, 0.5), ('e', 3, 0.5),  # Va-mos (Mi Sol)
            ('e', 1, 0.5), ('e', 0, 0.5),  # dar a  (Fá Mi)
            ('B', 3, 0.5), ('B', 1, 0.5),  # mei-a  (Re Do)
            ('B', 0, 0.5),  ('G', 0, 0.5),# vol-ta (Sì - Sol)

            # PARTE 4: "Vol-ta e mei-a va-mos dar"
            # Repete a mesma melodia da Parte 3
            ('e', 1, 0.5), ('B', 3, 0.5),  # Vol-ta e (Fá Re)
            ('e', 0, 0.5), ('B', 1, 0.5),  # mei-a    (Fá Fá)
            ('B', 3, 0.5), ('B', 0, 0.5),  # va-mos   (Mi Mi)
            ('B', 1, 2.0),  # dar      (Ré)

            # (Opcional: Para finalizar a música, repete-se a Parte 2 "O anel que tu me destes...")
            # Mas a estrutura acima cobre a estrofe principal inteira.
        ]
    },
}


# ==============================================================================
# FUNÇÕES CORE
# ==============================================================================

def note_freq(string, fret):
    base = NOTAS_FREQ.get(string, 0)
    return base * (2 ** (fret / 12.0))


def create_midi(seq, filename, bpm, time_signature=(4, 4)):
    string_base = {'E': 40, 'A': 45, 'D': 50, 'G': 55, 'B': 59, 'e': 64}
    TICKS_PER_BEAT = 480

    # 1. TEMPO (BPM)
    tempo_bytes = int(60_000_000 / bpm).to_bytes(3, 'big')

    # 2. TIME SIGNATURE (Compasso)
    # Formato MIDI: FF 58 04 nn dd cc bb
    # nn = numerador (ex: 2)
    # dd = log2 do denominador (ex: 4 -> 2^2 -> dd=2)
    num, den = time_signature
    den_log2 = int(math.log2(den))

    # Header Track
    events = bytearray()
    events += b'\x00\xFF\x51\x03' + tempo_bytes  # Set Tempo
    # Set Time Signature: 00 FF 58 04 [num] [den_log2] [24 clocks] [8 notes]
    events += b'\x00\xFF\x58\x04' + bytes([num, den_log2, 24, 8])

    events += b'\x00\xC0\x18'  # Troca Instrumento (Violão)

    # Note Events
    for item in seq:
        s, fret, dur = item
        if s == 'PAUSA':
            delta = int(dur * TICKS_PER_BEAT)
            events += _write_var_len(delta) + bytes([0x80, 0, 0])
            continue

        if s in string_base:
            note = string_base[s] + fret
            duration_ticks = int(dur * TICKS_PER_BEAT)
            # Note On (90)
            events += b'\x00' + bytes([0x90, note, 95])
            # Note Off (80)
            events += _write_var_len(duration_ticks) + bytes([0x80, note, 0])

    events += b'\x00\xFF\x2F\x00'  # End Track

    header = b'MThd' + struct.pack('>IHHH', 6, 0, 1, TICKS_PER_BEAT)
    track = b'MTrk' + struct.pack('>I', len(events)) + events

    with open(filename, 'wb') as f:
        f.write(header + track)
    return filename


def _write_var_len(val):
    buf = [val & 0x7F]
    val >>= 7
    while val > 0:
        buf.append((val & 0x7F) | 0x80)
        val >>= 7
    return bytes(reversed(buf))


def create_wav(seq, filename, bpm):
    sample_rate = 44100
    audio = []
    seconds_per_beat = 60.0 / bpm

    print(f"Sintetizando {filename}...", end='')
    for item in seq:
        string, fret, beats = item
        duration = beats * seconds_per_beat
        if duration <= 0: duration = 0.1

        t = np.linspace(0, duration, int(sample_rate * duration), False)

        if string == 'PAUSA':
            wave_data = np.zeros_like(t)
        else:
            freq = note_freq(string, fret)
            # Timbre simulando corda nylon (harmônicos suaves)
            envelope = np.exp(-4 * t)
            tone = np.sin(2 * np.pi * freq * t)
            tone2 = 0.6 * np.sin(2 * np.pi * freq * 2 * t)
            tone3 = 0.3 * np.sin(2 * np.pi * freq * 3 * t)
            wave_data = (tone + tone2 + tone3) * envelope * 0.4

        audio.append(wave_data)
    print(" OK.")

    if not audio: return None
    audio_concat = np.concatenate(audio)
    audio_int16 = (audio_concat * 32767).astype(np.int16)

    with wave.open(filename, 'w') as wav_file:
        wav_file.setnchannels(1)
        wav_file.setsampwidth(2)
        wav_file.setframerate(sample_rate)
        wav_file.writeframes(audio_int16.tobytes())
    return filename


def convert_to_mp3(wav_file, mp3_file):
    if not os.path.exists(wav_file): return None
    try:
        sound = AudioSegment.from_wav(wav_file)
        sound.export(mp3_file, format="mp3")
        return mp3_file
    except:
        return None


def tocar_arquivo(filename):
    if not filename or not os.path.exists(filename): return
    print(f"--> Tocando: {filename}")
    try:
        pygame.mixer.init()
        pygame.mixer.music.load(filename)
        pygame.mixer.music.play()
        while pygame.mixer.music.get_busy():
            time.sleep(0.1)
    except KeyboardInterrupt:
        pygame.mixer.music.stop()
    except Exception as e:
        print(e)


# ==============================================================================
# MENUS
# ==============================================================================

def processar_musica(id_musica):
    dados = BIBLIOTECA_MUSICAS[id_musica]
    nome_safe = dados['titulo'].replace(" ", "_").lower()
    bpm = dados.get('bpm', BPM_PADRAO)
    compasso = dados.get('compasso', (4, 4))  # Padrão 4/4 se não informado

    print(f"\n[{dados['titulo']}] BPM:{bpm} Compasso:{compasso[0]}/{compasso[1]}")

    midi = create_midi(dados['seq'], f"{nome_safe}.mid", bpm, compasso)
    wav = create_wav(dados['seq'], f"{nome_safe}.wav", bpm)
    mp3 = convert_to_mp3(wav, f"{nome_safe}.mp3")

    while True:
        print(f"\n1. Tocar WAV (Recomendado)")
        if mp3: print(f"2. Tocar MP3")
        print(f"3. Tocar MIDI")
        print(f"0. Voltar")
        op = input("Opção: ")
        if op == '1':
            tocar_arquivo(wav)
        elif op == '2' and mp3:
            tocar_arquivo(mp3)
        elif op == '3':
            tocar_arquivo(midi)
        elif op == '0':
            break


if __name__ == '__main__':
    while True:
        print("\n=== JUKEBOX VIOLÃO ===")
        for k, v in BIBLIOTECA_MUSICAS.items():
            print(f"{k} - {v['titulo']}")
        print("0 - Sair")

        esc = input("Escolha: ")
        if esc == '0': break
        if esc in BIBLIOTECA_MUSICAS: processar_musica(esc)