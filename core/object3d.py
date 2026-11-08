"""Grafo de cena: Object3D (no com transformacao) e Mesh (no com geometria)."""
import numpy as np
from OpenGL.GL import *
from core import matrix as M


class Object3D:
    def __init__(self, nome=""):
        self.nome = nome
        self.pai = None
        self.filhos = []
        self.position = np.zeros(3, dtype=np.float32)
        self.rotation = np.zeros(3, dtype=np.float32)   # radianos (x, y, z)
        self.scale = np.ones(3, dtype=np.float32)

    def add(self, filho):
        filho.pai = self
        self.filhos.append(filho)
        return filho

    def matriz_local(self):
        return (M.translacao(*self.position)
                @ M.rotacao_y(self.rotation[1])
                @ M.rotacao_x(self.rotation[0])
                @ M.rotacao_z(self.rotation[2])
                @ M.escala(*self.scale))

    def matriz_mundo(self):
        if self.pai is None:
            return self.matriz_local()
        return self.pai.matriz_mundo() @ self.matriz_local()

    def descendentes(self):
        lista = []
        for f in self.filhos:
            lista.append(f)
            lista.extend(f.descendentes())
        return lista


class Mesh(Object3D):
    def __init__(self, geometria, cor, brilho=32.0, especular=0.3):
        super().__init__("mesh")
        self.geometria = geometria
        self.cor = cor
        self.brilho = brilho
        self.especular = especular

    def desenhar(self, loc):
        glUniformMatrix4fv(loc["uModel"], 1, GL_TRUE, self.matriz_mundo())
        glUniform3f(loc["uColor"], *self.cor)
        glUniform1f(loc["uShininess"], self.brilho)
        glUniform1f(loc["uSpecular"], self.especular)
        self.geometria.desenhar()


def adicionar_malha(pai, geometria, cor, pos=(0, 0, 0), rot=(0, 0, 0),
                    escala=(1, 1, 1), brilho=32.0, especular=0.3):
    """Cria uma Mesh, posiciona e pendura no 'pai'."""
    m = Mesh(geometria, cor, brilho, especular)
    m.position[:] = pos
    m.rotation[:] = rot
    m.scale[:] = escala
    pai.add(m)
    return m
