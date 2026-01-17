import pygame
import numpy as np
import wave
import os
import sys
import ctypes


# ==============================================================================
# 1. CONFIGURAÇÕES E CONSTANTES (Classe Estática)
# ==============================================================================
class Config:
    # Ajuste de DPI do Windows
    try:
        ctypes.windll.user32.SetProcessDPIAware()
    except:
        pass

    # Tela
    WIDTH = 800
    HEIGHT = 700
    FPS = 60

    # Cores
    BLACK = (20, 20, 20)
    WHITE = (255, 255, 255)
    GRAY = (100, 100, 100)
    WOOD_COLOR = (60, 40, 20)

    STRING_COLORS = [
        (255, 80, 80),  # E - Vermelho
        (255, 255, 80),  # A - Amarelo
        (80, 80, 255),  # D - Azul
        (80, 255, 80),  # G - Verde
        (255, 165, 0),  # B - Laranja
        (200, 100, 255)  # e - Roxo
    ]

    # Geometria do Violão
    NECK_WIDTH = 400
    MARGIN_X = (WIDTH - NECK_WIDTH) // 2
    HIT_Y = HEIGHT - 100
    FALL_SPEED = 250  # Pixels por segundo

    # Dados Musicais
    STRINGS = ['E', 'A', 'D', 'G', 'B', 'e']
    FREQS = {'E': 82.41, 'A': 110.00, 'D': 146.83, 'G': 196.00, 'B': 246.94, 'e': 329.63}

    @staticmethod
    def get_string_x(string_name):
        try:
            idx = Config.STRINGS.index(string_name)
            spacing = Config.NECK_WIDTH / (len(Config.STRINGS) - 1)
            return Config.MARGIN_X + (idx * spacing)
        except ValueError:
            return 0

    @staticmethod
    def get_string_color(string_name):
        try:
            idx = Config.STRINGS.index(string_name)
            return Config.STRING_COLORS[idx]
        except ValueError:
            return Config.WHITE