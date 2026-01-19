import ctypes


# ==============================================================================
# 1. CONFIGURAÇÕES E CONSTANTES (MODO HORIZONTAL)
# ==============================================================================
class Config:
    # Ajuste de DPI do Windows
    try:
        ctypes.windll.user32.SetProcessDPIAware()
    except:
        pass

    # Tela (Widescreen para aproveitar a horizontalidade)
    WIDTH = 1000
    HEIGHT = 600
    FPS = 60

    # Cores
    BLACK = (20, 20, 20)
    WHITE = (255, 255, 255)
    GRAY = (100, 100, 100)
    DARK_GRAY = (50, 50, 50)  # Cor do braço/fundo da tablatura

    # Cores das cordas (Padrão Rocksmith/Guitar Hero)
    STRING_COLORS = [
        (255, 80, 80),  # E (Grave) - Vermelho
        (255, 255, 80),  # A - Amarelo
        (80, 80, 255),  # D - Azul
        (80, 255, 80),  # G - Verde
        (255, 165, 0),  # B - Laranja
        (200, 100, 255)  # e (Aguda) - Roxo
    ]

    # Geometria do Braço (Horizontal)
    # Vamos usar a convenção visual de olhar para o braço: E grave em CIMA ou EM BAIXO?
    # Tablatura padrão: e (aguda) em cima, E (grave) em baixo.
    # Mas visualmente "Guitar Hero" horizontal costuma por E (grave) em baixo.
    # Vamos seguir TABLATURA PADRÃO: Linha de cima = e (aguda).

    # Altura da área onde ficam as cordas
    TAB_HEIGHT = 300
    MARGIN_Y = (HEIGHT - TAB_HEIGHT) // 2

    # Onde a nota deve ser tocada (Linha Vertical à Esquerda)
    HIT_X = 150

    # Velocidade horizontal
    SCROLL_SPEED = 300  # Pixels por segundo

    # Ordem das cordas para desenho (Visual Tablatura: e aguda no topo)
    # Mas nossa lista de dados é ['E', 'A', 'D', 'G', 'B', 'e']
    STRINGS_ORDER = ['e', 'B', 'G', 'D', 'A', 'E']

    # Frequências (para síntese se faltar sample)
    FREQS = {'E': 82.41, 'A': 110.00, 'D': 146.83, 'G': 196.00, 'B': 246.94, 'e': 329.63}

    @staticmethod
    def get_string_y(string_name):
        """Retorna a posição Y da linha da corda (Horizontal)"""
        try:
            # Tablatura padrão: e (aguda) é a primeira linha (topo)
            idx = Config.STRINGS_ORDER.index(string_name)
            spacing = Config.TAB_HEIGHT / (len(Config.STRINGS_ORDER) - 1)
            return Config.MARGIN_Y + (idx * spacing)
        except ValueError:
            return 0

    @staticmethod
    def get_string_color(string_name):
        # Mapeamos a cor baseada na corda original E A D G B e
        original_order = ['E', 'A', 'D', 'G', 'B', 'e']
        try:
            idx = original_order.index(string_name)
            return Config.STRING_COLORS[idx]
        except ValueError:
            return Config.WHITE