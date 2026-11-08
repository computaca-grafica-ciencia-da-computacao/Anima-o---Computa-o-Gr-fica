"""Camera orbital: arraste com o botao esquerdo, roda do mouse para zoom."""
from math import sin, cos, radians
import numpy as np
import pygame
from core import matrix as M


class CameraOrbital:
    def __init__(self, alvo=(-1.5, 1.0, 0.5), distancia=12.5, yaw=-25.0, pitch=20.0, fov=50.0):
        self.alvo = np.array(alvo, dtype=np.float32)
        self.distancia = distancia
        self.yaw = radians(yaw)
        self.pitch = radians(pitch)
        self.fov = fov

    def posicao(self):
        d = self.distancia
        return self.alvo + d * np.array([
            cos(self.pitch) * sin(self.yaw),
            sin(self.pitch),
            cos(self.pitch) * cos(self.yaw),
        ], dtype=np.float32)

    def view(self):
        return M.olhar_para(self.posicao(), self.alvo)

    def projecao(self, aspecto):
        return M.perspectiva(self.fov, aspecto, 0.1, 200.0)

    def evento(self, e):
        if e.type == pygame.MOUSEMOTION and e.buttons[0]:
            self.yaw -= e.rel[0] * 0.006
            self.pitch = max(0.05, min(1.45, self.pitch + e.rel[1] * 0.006))
        elif e.type == pygame.MOUSEWHEEL:
            self.distancia = max(4.0, min(60.0, self.distancia * (0.9 ** e.y)))
