import ctypes


# ==============================================================================
# 1. CONFIGURAÇÕES
# ==============================================================================
class Config:
    try:
        ctypes.windll.user32.SetProcessDPIAware()
    except:
        pass

    WIDTH = 1100
    HEIGHT = 700
    FPS = 60

    # Cores
    BLACK = (20, 20, 20)
    WHITE = (255, 255, 255)
    GRAY = (100, 100, 100)
    DARK_GRAY = (40, 40, 40)
    WOOD_COLOR = (101, 67, 33)
    FRET_COLOR = (180, 180, 180)
    NUT_COLOR = (230, 230, 210)  # Cor de osso/marfim para a pestana

    # Cores das cordas
    STRING_COLORS = [
        (255, 80, 80),  # E - Vermelho
        (255, 255, 80),  # A - Amarelo
        (80, 80, 255),  # D - Azul
        (80, 255, 80),  # G - Verde
        (255, 165, 0),  # B - Laranja
        (200, 100, 255)  # e - Roxo
    ]

    # Sincronia de Áudio/Vídeo
    START_DELAY = 3000

    # --- TABLATURA (CIMA) ---
    TAB_AREA_HEIGHT = 350
    TAB_MARGIN_Y = 50
    HIT_X = 200
    SCROLL_SPEED = 350

    # --- BRAÇO ESTÁTICO (BAIXO) ---
    NECK_AREA_START_Y = 400
    NECK_HEIGHT = 200

    # Ajuste: O braço começa um pouco mais para a direita para caber o "0" fora dele
    NECK_START_X = 100

    STRINGS_ORDER = ['e', 'B', 'G', 'D', 'A', 'E']

    @staticmethod
    def get_tab_y(string_name):
        try:
            idx = Config.STRINGS_ORDER.index(string_name)
            spacing = (Config.TAB_AREA_HEIGHT - 40) / (len(Config.STRINGS_ORDER) - 1)
            return Config.TAB_MARGIN_Y + 20 + (idx * spacing)
        except ValueError:
            return 0

    @staticmethod
    def get_neck_y(string_name):
        try:
            idx = Config.STRINGS_ORDER.index(string_name)
            spacing = (Config.NECK_HEIGHT - 40) / (len(Config.STRINGS_ORDER) - 1)
            return Config.NECK_AREA_START_Y + 20 + (idx * spacing)
        except ValueError:
            return 0

    @staticmethod
    def get_fret_x(fret_number):
        """
        Lógica alterada:
        - Casa 0: Fica À ESQUERDA da pestana (fora do braço).
        - Casa 1+: Fica DENTRO do braço.
        """
        fret_width = 75

        if fret_number == 0:
            # Posição da corda solta (antes do braço começar)
            return Config.NECK_START_X - 35
        else:
            # Posição normal (start + (casa * largura) - metade_da_largura)
            # O '-1' é porque agora o loop começa da casa 1 fisicamente
            return Config.NECK_START_X + (fret_number * fret_width) - (fret_width / 2)

    @staticmethod
    def get_string_color(string_name):
        order = ['E', 'A', 'D', 'G', 'B', 'e']
        try:
            return Config.STRING_COLORS[order.index(string_name)]
        except:
            return Config.WHITE