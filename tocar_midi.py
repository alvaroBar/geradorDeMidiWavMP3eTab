import pygame
import time


def tocar_midi(arquivo):
    # Inicializa o mixer de áudio do Pygame
    pygame.mixer.init()

    try:
        # Carrega o arquivo MIDI
        pygame.mixer.music.load(arquivo)
        print(f"Tocando {arquivo}...")

        # Começa a tocar
        pygame.mixer.music.play()

        # O script precisa continuar rodando enquanto a música toca.
        # Este loop verifica se a música ainda está tocando.
        while pygame.mixer.music.get_busy():
            time.sleep(1)  # Espera 1 segundo antes de checar de novo

        print("Fim da reprodução.")

    except pygame.error as e:
        print(f"Erro ao tentar tocar o arquivo: {e}")
        print("Verifique se o arquivo existe e se o nome está correto.")


if __name__ == '__main__':
    # Use o nome do arquivo que você criou no passo anterior
    tocar_midi('violao_ritmo.mid')