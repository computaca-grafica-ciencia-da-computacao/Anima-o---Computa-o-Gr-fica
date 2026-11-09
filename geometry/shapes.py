"""Geometrias basicas: caixa, cilindro (eixo Y) e esfera.
Cada vertice = [x, y, z, nx, ny, nz, u, v] (posicao, normal, coordenada de textura)."""
from math import pi, sin, cos
import numpy as np
from geometry.geometry import Geometry


def caixa(largura, altura, profundidade, uv_por_unidade=None):
    """uv_por_unidade=None  -> cada face recebe a imagem inteira (u, v em 0..1).
    uv_por_unidade=k        -> a textura se repete k vezes por unidade de mundo
                               (ladrilhamento: chao e pista grandes sem esticar a imagem)."""
    meio = np.array([largura, altura, profundidade]) / 2
    # (normal, direita, cima) de cada face
    faces = [
        ((1, 0, 0), (0, 0, -1), (0, 1, 0)),
        ((-1, 0, 0), (0, 0, 1), (0, 1, 0)),
        ((0, 1, 0), (1, 0, 0), (0, 0, -1)),
        ((0, -1, 0), (1, 0, 0), (0, 0, 1)),
        ((0, 0, 1), (1, 0, 0), (0, 1, 0)),
        ((0, 0, -1), (-1, 0, 0), (0, 1, 0)),
    ]
    v, idx = [], []
    for n, r, u in faces:
        n, r, u = np.array(n), np.array(r), np.array(u)
        c, rr, uu = n * meio, r * meio, u * meio
        if uv_por_unidade is None:
            larg_uv, alt_uv = 1.0, 1.0
        else:
            larg_uv = 2 * np.linalg.norm(rr) * uv_por_unidade
            alt_uv = 2 * np.linalg.norm(uu) * uv_por_unidade
        cantos = ((c - rr - uu, (0, 0)), (c + rr - uu, (larg_uv, 0)),
                  (c + rr + uu, (larg_uv, alt_uv)), (c - rr + uu, (0, alt_uv)))
        base = len(v)
        for p, (tu, tv) in cantos:
            v.append([*p, *n, tu, tv])
        idx += [base, base + 1, base + 2, base, base + 2, base + 3]
    return Geometry(v, idx)


def cilindro(raio, altura, segmentos=28):
    h = altura / 2
    v, idx = [], []
    for i in range(segmentos + 1):
        a = 2 * pi * i / segmentos
        c, s = cos(a), sin(a)
        v.append([raio * c, -h, raio * s, c, 0, s, i / segmentos, 0])
        v.append([raio * c, h, raio * s, c, 0, s, i / segmentos, 1])
    for i in range(segmentos):
        b = 2 * i
        idx += [b, b + 1, b + 2, b + 1, b + 3, b + 2]
    for sinal in (1, -1):  # tampas (uv = projecao planar do disco)
        centro = len(v)
        v.append([0, sinal * h, 0, 0, sinal, 0, 0.5, 0.5])
        for i in range(segmentos + 1):
            a = 2 * pi * i / segmentos
            v.append([raio * cos(a), sinal * h, raio * sin(a), 0, sinal, 0,
                      0.5 + 0.5 * cos(a), 0.5 + 0.5 * sin(a)])
        for i in range(segmentos):
            idx += [centro, centro + 1 + i, centro + 2 + i]
    return Geometry(v, idx)


def esfera(raio, faixas=14, fatias=24):
    v, idx = [], []
    for i in range(faixas + 1):
        phi = pi * i / faixas
        y, r = cos(phi), sin(phi)
        for j in range(fatias + 1):
            th = 2 * pi * j / fatias
            x, z = r * cos(th), r * sin(th)
            v.append([raio * x, raio * y, raio * z, x, y, z, j / fatias, i / faixas])
    for i in range(faixas):
        for j in range(fatias):
            a = i * (fatias + 1) + j
            b = a + fatias + 1
            idx += [a, b, a + 1, a + 1, b, b + 1]
    return Geometry(v, idx)
