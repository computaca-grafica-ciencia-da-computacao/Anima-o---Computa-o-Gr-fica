"""Camera orbital em perspectiva.
Mouse: arrastar = orbitar, roda = zoom.
Teclado: setas/A/D = orbitar, setas cima/baixo = inclinar, W/S (ou +/-) = zoom."""
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

    def teclado(self, teclas, dt):
        """Controle pelo teclado, proporcional ao tempo decorrido (independe do FPS)."""
        giro = 1.6 * dt
        if teclas[pygame.K_LEFT] or teclas[pygame.K_a]:
            self.yaw -= giro
        if teclas[pygame.K_RIGHT] or teclas[pygame.K_d]:
            self.yaw += giro
        if teclas[pygame.K_UP]:
            self.pitch = min(1.45, self.pitch + giro)
        if teclas[pygame.K_DOWN]:
            self.pitch = max(0.05, self.pitch - giro)
        fator = 0.4 ** dt        # aproximar: -60% da distancia por segundo
        if teclas[pygame.K_w] or teclas[pygame.K_EQUALS] or teclas[pygame.K_KP_PLUS]:
            self.distancia = max(4.0, self.distancia * fator)
        if teclas[pygame.K_s] or teclas[pygame.K_MINUS] or teclas[pygame.K_KP_MINUS]:
            self.distancia = min(60.0, self.distancia / fator)
