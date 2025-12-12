import struct
import math
import wave
import os
import sys
import time

# --- Importação de bibliotecas externas ---
try:
    import pygame
    import numpy as np
    from pydub import AudioSegment

    # Bibliotecas para PDF
    from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, KeepTogether
    from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
    from reportlab.lib.pagesizes import letter
    from reportlab.lib.units import cm
except ImportError as e:
    print(f"ERRO: Faltam bibliotecas ({e}).")
    print("Instale: pip install pygame numpy pydub reportlab")
    sys.exit()

# ==============================================================================
# CONFIGURAÇÕES E DADOS
# ==============================================================================
BPM_PADRAO = 110

NOTAS_FREQ = {
    'E': 82.41, 'A': 110.00, 'D': 146.83,
    'G': 196.00, 'B': 246.94, 'e': 329.63
}

BIBLIOTECA_MUSICAS = {
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
            #Mar-cha sol-da-do
            ('e', 3, 1), ('e', 3, 0.5), ('e', 0, 0.5), ('B', 1, 1), ('B', 1, 0.5),
            #Ca-be-ça de pa-pel
            ('e', 0, 0.5), ('e', 3, 0.5), ('e', 3, 0.5), ('e', 3, 0.5), ('e', 0, 0.5), ('B', 3, 1.5),
            #Quem não mar-char di-rei-to
            ('e', 0, 0.5), ('e', 1, 0.5), ('e', 1, 0.5), ('e', 1, 0.5), ('B', 3, 0.5), ('e', 3, 1), ('e', 3, 0.5),
            #Vai pre-so no quar-tel
            ('e', 5, 0.5), ('e', 3, 0.5), ('e', 1, 0.5), ('e', 0, 0.5), ('B', 3, 0.5), ('B', 1, 1),
            #O quar-tel pe-gou fo-go
            ('B', 1, 0.5), ('e', 0, 0.5), ('e', 3, 1), ('e', 3, 0.5), ('e', 0, 0.5), ('B', 1, 1), ('B', 1, 0.5),
            #São Fran-cis-co deu si-nal
            ('e', 0, 0.5), ('e', 3, 0.5), ('e', 3, 0.5), ('e', 3, 0.5), ('e', 0, 0.5), ('B', 3, 1.5),
            #A-co-de a-co-de a-co-de
            ('e', 0, 0.5), ('e', 1, 0.5), ('e', 1, 0.5), ('e', 1, 0.5), ('B', 3, 0.5), ('e', 3, 1), ('e', 3, 0.5),
            #A ban-dei-ra na-cio-nal
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
            #Aaaa-ti-rei
            ('G', 0, 1.5), ('D', 3, 0.5), ('D', 2, 0.5),
            #Mas o ga-to-to
            ('D', 0, 0.5), ('D', 2, 0.5), ('D', 3, 0.5), ('G', 0, 1), ('G', 0, 1), ('G', 0, 1.0),
            #maaas o ga-to-to
            ('G', 2, 0.5), ('G', 0, 0.5), ('D', 3, 1), ('D', 3, 1), ('D', 3, 1),
            #não mo-reu-reu-reu
            ('G', 0, 0.5), ('D', 3, 0.5), ('D', 2, 1), ('D', 2, 1), ('D', 2, 1),
            #Do-na chi_ca-ca
            ('D', 0, 0.5), ('A', 3, 0.5), ('G', 2, 1), ('G', 2, 1), ('G', 2, 1),
            #Ad-mi-rou se-se
            ('B', 0, 0.5), ('G', 2, 0.5), ('G', 0, 1), ('G', 0, 1), ('G', 0, 1),
            #Do ber-ro do ber-ro
            ('D', 3, 0.5), ('D', 2, 0.5), ('G', 0, 1), ('D', 3, 0.5), ('D', 2, 0.5), ('G', 0, 0.5),
            #que o ga-to deu
            ('D', 3, 0.5), ('D', 2, 0.5), ('D', 0, 0.5), ('A', 3, 2),

        ]
    },
    "6": {
        "titulo": "Ciranda Cirandinha",
        "bpm": 100,
        "compasso": (2, 4),
        "seq": [
            #Ci-ran-da
            ('A', 3, 1), ('D', 3, 0.5), ('D', 3, 0.5),
            #Ci-ran-di-nha
            ('G', 2, 0.5), ('G', 2, 0.5), ('B', 1, 0.5), ('B', 1, 0.5),
            #Va-mos to-dos ci-ran-dar
            ('G', 3, 0.5), ('G', 2, 0.5), ('G', 0, 0.5), ('B', 1, 0.5), ('G', 2, 0.5), ('G', 0, 0.5), ('D', 3, 1),
            #Va-mos dar a meia vol-ta
            ('G', 2, 0.5), ('B', 1, 0.5), ('G', 3, 0.5), ('G', 2, 0.5), ('G', 0, 0.5), ('D', 3, 0.5), ('D', 2, 0.5), ('A', 3, 0.5),
            #volta e meia va-mos dar
            ('G', 2, 0.5), ('D', 3, 0.5), ('G', 0, 0.5), ('D', 2, 0.5), ('D', 3, 0.5), ('D', 2, 0.5), ('D', 3, 0.5)

        ]
    }
}


# ==============================================================================
# MOTOR DE ÁUDIO E MIDI
# ==============================================================================

def note_freq(string, fret):
    base = NOTAS_FREQ.get(string, 0)
    return base * (2 ** (fret / 12.0))


def create_midi(seq, filename, bpm, time_signature):
    string_base = {'E': 40, 'A': 45, 'D': 50, 'G': 55, 'B': 59, 'e': 64}
    TICKS_PER_BEAT = 480
    tempo_bytes = int(60_000_000 / bpm).to_bytes(3, 'big')
    num, den = time_signature
    den_log2 = int(math.log2(den))

    events = bytearray()
    events += b'\x00\xFF\x51\x03' + tempo_bytes
    events += b'\x00\xFF\x58\x04' + bytes([num, den_log2, 24, 8])
    events += b'\x00\xC0\x18'

    for item in seq:
        s, fret, dur = item
        if s == 'PAUSA':
            delta = int(dur * TICKS_PER_BEAT)
            events += _write_var_len(delta) + bytes([0x80, 0, 0])
            continue

        if s in string_base:
            note = string_base[s] + fret
            duration_ticks = int(dur * TICKS_PER_BEAT)
            events += b'\x00' + bytes([0x90, note, 95])
            events += _write_var_len(duration_ticks) + bytes([0x80, note, 0])

    events += b'\x00\xFF\x2F\x00'
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
            envelope = np.exp(-4 * t)
            tone = np.sin(2 * np.pi * freq * t)
            tone2 = 0.6 * np.sin(2 * np.pi * freq * 2 * t)
            wave_data = (tone + tone2) * envelope * 0.4
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
# GERADOR DE PDF
# ==============================================================================

def format_tab_block(seq):
    """Converte a sequência de notas em string de tablatura formatada."""
    strings_order = ['e', 'B', 'G', 'D', 'A', 'E']
    lines = {s: [f"{s}|"] for s in strings_order}

    # Limite de caracteres por linha antes de quebrar
    MAX_CHARS = 65
    blocks = []
    current_length = 2  # Começa contando "e|"

    for item in seq:
        s, fret, dur = item

        if s == 'PAUSA':
            step_str = "---"
        else:
            step_str = f"-{fret}-"

        step_len = len(step_str)

        # Verifica se precisa quebrar linha
        if current_length + step_len > MAX_CHARS:
            # Fecha o bloco atual
            block_str = ""
            for st in strings_order:
                block_str += "".join(lines[st]) + "|\n"
            blocks.append(block_str)

            # Reinicia linhas para novo bloco
            lines = {st: [f"{st}|"] for st in strings_order}
            current_length = 2

        # Adiciona a nota nas linhas
        for st in strings_order:
            if st == s and s != 'PAUSA':
                lines[st].append(step_str)
            else:
                lines[st].append("-" * step_len)

        current_length += step_len

    # Adiciona o último bloco
    block_str = ""
    for st in strings_order:
        block_str += "".join(lines[st]) + "|\n"
    blocks.append(block_str)

    return "\n".join(blocks)


def gerar_livro_pdf(filename="Violao_Infantil_Tabs.pdf"):
    print(f"\nGerando PDF: {filename}...")
    doc = SimpleDocTemplate(filename, pagesize=letter)
    styles = getSampleStyleSheet()
    story = []

    # Título Principal
    header = "<h1>Coletânea de Violão Infantil</h1><p> Tablaturas geradas automaticamente</p><br/><br/>"
    story.append(Paragraph(header, styles["Title"]))

    # Estilo da Tablatura (Monoespaçado)
    tab_style = ParagraphStyle(
        'Tablatura',
        parent=styles['Code'],
        fontName='Courier',
        fontSize=10,
        leading=12,
        spaceAfter=10
    )

    # Itera sobre todas as músicas da biblioteca
    for key, dados in BIBLIOTECA_MUSICAS.items():
        title = dados['titulo']
        seq = dados['seq']

        # Título da Música
        story.append(Paragraph(f"<b>{title}</b>", styles["Heading2"]))

        # Gera o texto da tablatura
        tab_text = format_tab_block(seq)

        # Converte quebras de linha para HTML <br/>
        tab_html = tab_text.replace("\n", "<br/>")
        tab_html = tab_html.replace(" ", "&nbsp;")  # Garante espaçamento

        # Adiciona ao PDF
        story.append(Paragraph(tab_html, tab_style))
        story.append(Spacer(1, 0.5 * cm))
        story.append(Paragraph("<hr width='100%' color='#e0e0e0'/>", styles["Normal"]))
        story.append(Spacer(1, 0.5 * cm))

    try:
        doc.build(story)
        print(f"[SUCESSO] PDF criado em: {os.path.abspath(filename)}")
        # Tenta abrir o PDF automaticamente (Windows)
        if os.name == 'nt':
            os.startfile(filename)
    except Exception as e:
        print(f"[ERRO] Falha ao criar PDF: {e}")


# ==============================================================================
# MENUS
# ==============================================================================

def processar_musica(id_musica):
    dados = BIBLIOTECA_MUSICAS[id_musica]
    nome_safe = dados['titulo'].replace(" ", "_").lower()
    bpm = dados.get('bpm', BPM_PADRAO)
    compasso = dados.get('compasso', (4, 4))

    print(f"\n[{dados['titulo']}] BPM:{bpm} Compasso:{compasso[0]}/{compasso[1]}")

    midi = create_midi(dados['seq'], f"{nome_safe}.mid", bpm, compasso)
    wav = create_wav(dados['seq'], f"{nome_safe}.wav", bpm)
    mp3 = convert_to_mp3(wav, f"{nome_safe}.mp3")

    while True:
        print(f"\n1. Tocar WAV")
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


def menu_principal():
    while True:
        print("\n" + "=" * 40)
        print("      JUKEBOX DE VIOLÃO PYTHON")
        print("=" * 40)
        print("Escolha uma música para tocar:")

        for k, v in BIBLIOTECA_MUSICAS.items():
            print(f"{k} - {v['titulo']}")

        print("-" * 20)
        print("P - Gerar PDF com todas as músicas")
        print("0 - Sair")

        escolha = input(">> Digite o número ou letra: ").upper()

        if escolha == '0':
            print("Encerrando...")
            break
        elif escolha == 'P':
            gerar_livro_pdf()
        elif escolha in BIBLIOTECA_MUSICAS:
            processar_musica(escolha)
        else:
            print("Opção inválida!")


if __name__ == '__main__':
    menu_principal()