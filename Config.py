import ctypes


# ==============================================================================
# 1. CONFIGURAÇÕES
# ==============================================================================
class Config:
    try:
        ctypes.windll.user32.SetProcessDPIAware()
    except:
        pass

    WIDTH = 1000
    HEIGHT = 700
    FPS = 60

    # Cores
    BLACK = (10, 10, 15)
    WHITE = (255, 255, 255)
    GRAY = (100, 100, 100)
    DARK_GRAY = (30, 30, 30)

    # Cores Neon (Estilo Rocksmith)
    STRING_COLORS = [
        (255, 60, 60),  # E - Vermelho
        (255, 255, 60),  # A - Amarelo
        (60, 100, 255),  # D - Azul
        (60, 255, 60),  # G - Verde
        (255, 165, 0),  # B - Laranja
        (200, 80, 255)  # e - Roxo
    ]

    START_DELAY = 3000

    # --- GEOMETRIA 3D ---
    HORIZON_Y = 100
    HIT_Y = 600
    BOTTOM_WIDTH = 750
    TOP_WIDTH = 80
    CENTER_X = WIDTH // 2

    STRINGS_ORDER = ['E', 'A', 'D', 'G', 'B', 'e']

    @staticmethod
    def get_string_color(string_name):
        std_order = ['E', 'A', 'D', 'G', 'B', 'e']
        try:
            return Config.STRING_COLORS[std_order.index(string_name)]
        except:
            return Config.WHITE

    @staticmethod
    def project_coordinates(string_name, progress):
        y = Config.HIT_Y - (progress * (Config.HIT_Y - Config.HORIZON_Y))
        current_track_width = Config.BOTTOM_WIDTH - (progress * (Config.BOTTOM_WIDTH - Config.TOP_WIDTH))

        idx = Config.STRINGS_ORDER.index(string_name)
        center_offset = idx - 2.5

        string_spacing = current_track_width / 6
        x = Config.CENTER_X + (center_offset * string_spacing) + (string_spacing / 2)

        scale = 1.0 - (progress * 0.7)

        return int(x), int(y), scale