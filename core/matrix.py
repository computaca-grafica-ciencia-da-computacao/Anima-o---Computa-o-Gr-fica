"""Matrizes 4x4 (convencao de vetor-coluna, como no livro de Stemkoski e Pascale)."""
import numpy as np
from math import sin, cos, tan, radians


def identidade():
    return np.identity(4, dtype=np.float32)


def translacao(x, y, z):
    m = identidade()
    m[0, 3], m[1, 3], m[2, 3] = x, y, z
    return m


def escala(sx, sy, sz):
    m = identidade()
    m[0, 0], m[1, 1], m[2, 2] = sx, sy, sz
    return m


def rotacao_x(a):
    c, s = cos(a), sin(a)
    m = identidade()
    m[1, 1], m[1, 2], m[2, 1], m[2, 2] = c, -s, s, c
    return m


def rotacao_y(a):
    c, s = cos(a), sin(a)
    m = identidade()
    m[0, 0], m[0, 2], m[2, 0], m[2, 2] = c, s, -s, c
    return m


def rotacao_z(a):
    c, s = cos(a), sin(a)
    m = identidade()
    m[0, 0], m[0, 1], m[1, 0], m[1, 1] = c, -s, s, c
    return m


def perspectiva(fov_graus, aspecto, perto, longe):
    f = 1.0 / tan(radians(fov_graus) / 2)
    m = np.zeros((4, 4), dtype=np.float32)
    m[0, 0] = f / aspecto
    m[1, 1] = f
    m[2, 2] = (longe + perto) / (perto - longe)
    m[2, 3] = 2 * longe * perto / (perto - longe)
    m[3, 2] = -1
    return m


def olhar_para(olho, alvo, cima=(0, 1, 0)):
    olho = np.array(olho, dtype=np.float32)
    f = np.array(alvo, dtype=np.float32) - olho
    f /= np.linalg.norm(f)
    s = np.cross(f, np.array(cima, dtype=np.float32))
    s /= np.linalg.norm(s)
    u = np.cross(s, f)
    m = identidade()
    m[0, :3], m[1, :3], m[2, :3] = s, u, -f
    m[0, 3], m[1, 3], m[2, 3] = -np.dot(s, olho), -np.dot(u, olho), np.dot(f, olho)
    return m
