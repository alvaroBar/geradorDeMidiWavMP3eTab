import struct
import pygame
import time

# --- CONFIGURAÇÕES ---
BPM = 110
ARQUIVO_MIDI = "sapo_cururu_corrigido.mid"


def create_midi(seq, filename):
    string_base = {'E': 40, 'A': 45, 'D': 50, 'G': 55, 'B': 59, 'e': 64}
    TICKS_PER_BEAT = 480

    # Função para converter BPM em tempo MIDI
    def get_tempo_bytes(bpm):
        microseconds = int(60_000_000 / bpm)
        return microseconds.to_bytes(3, byteorder='big')

    def write_var_len(val):
        buf = [val & 0x7F]
        val >>= 7
        while val > 0:
            buf.append((val & 0x7F) | 0x80)
            val >>= 7
        return bytes(reversed(buf))

    events = bytearray()
    events += b'\x00\xFF\x51\x03' + get_tempo_bytes(BPM)  # Define BPM
    events += b'\x00\xC0\x18'  # Violão

    for s, fret, dur in seq:
        if s in string_base:
            note = string_base[s] + fret
            duration_ticks = int(dur * TICKS_PER_BEAT)

            # Note On (Velocity 90)
            events += b'\x00' + bytes([0x90, note, 90])

            # Note Off
            events += write_var_len(duration_ticks) + bytes([0x80, note, 0])

    events += b'\x00\xFF\x2F\x00'
    header = b'MThd' + struct.pack('>IHHH', 6, 0, 1, TICKS_PER_BEAT)
    track = b'MTrk' + struct.pack('>I', len(events)) + events

    with open(filename, 'wb') as f:
        f.write(header + track)
    return filename


def play_midi(filename):
    pygame.mixer.init()
    try:
        pygame.mixer.music.load(filename)
        print(f"Tocando melodia corrigida ({BPM} BPM)...")
        pygame.mixer.music.play()
        while pygame.mixer.music.get_busy():
            time.sleep(0.1)
        print("Fim.")
    except Exception as e:
        print(f"Erro: {e}")


# --- SEQUÊNCIA BASEADA NAS SUAS NOTAS ---
# Notas pedidas:
# 1. G A G D C
# 2. G A G D C
# 3. E E D E F# D B G
# 4. B B A B C

seq = [
    # PARTE 1: G - A - G - D - C
    ('G', 0, 0.5), ('G', 2, 0.5), ('G', 0, 0.5), ('D', 2, 0.5), ('B', 1, 2.0),
    # Nota D (Ré) feita na corda Si casa 3 para manter o brilho

    # PARTE 2: G - A - G - D - C (Repete)
    ('G', 0, 0.5), ('G', 2, 0.5), ('G', 0, 0.5), ('D', 2, 0.5), ('B', 1, 2.0),

    # PARTE 3: E - E - D - E - F - D - B - G
    ('e', 0, 0.5), ('e', 0, 0.5),  # E E
    ('B', 3, 0.5), ('e', 0, 0.5),  # D E
    ('e', 1, 0.5), ('B', 3, 0.35),  # F# D (F# é corda Mizinha casa 2)
    ('B', 0, 0.35), ('G', 0, 1.75),  # B G  (Finaliza na corda Sol solta)

    # Pausa breve para respirar antes do final
    ('G', 0, 0.5),  # (Silêncio técnico ou nota de ligação se preferir, aqui mantive o ritmo fluido)

    # PARTE 4: B - B - A - B - C
    ('B', 0, 0.5),  # B B
    ('G', 2, 0.5), ('B', 0, 0.5),  # A B
    ('B', 1, 3.5)  # C (Final)
]

if __name__ == '__main__':
    arquivo = create_midi(seq, ARQUIVO_MIDI)
    play_midi(arquivo)