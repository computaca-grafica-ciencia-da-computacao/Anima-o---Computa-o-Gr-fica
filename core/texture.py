"""Texturas de imagem (secao 5.1 do livro): carrega o arquivo com pygame e envia para a GPU."""
import os
import pygame
from OpenGL.GL import *

RAIZ = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
PASTA_TEXTURAS = os.path.join(RAIZ, "texturas")
_cache = {}


class Textura:
    def __init__(self, caminho=None, repetir=True):
        self.id = glGenTextures(1)
        glBindTexture(GL_TEXTURE_2D, self.id)
        if caminho is None:                       # textura branca 1x1 (para malhas sem imagem)
            largura, altura, dados = 1, 1, bytes([255, 255, 255, 255])
        else:
            superficie = pygame.image.load(caminho)
            largura, altura = superficie.get_size()
            # flipped=True: a linha 0 da imagem fica em v=1 (convencao do OpenGL, como no livro)
            dados = pygame.image.tostring(superficie, "RGBA", True)
        glPixelStorei(GL_UNPACK_ALIGNMENT, 1)
        glTexImage2D(GL_TEXTURE_2D, 0, GL_RGBA, largura, altura, 0, GL_RGBA,
                     GL_UNSIGNED_BYTE, dados)
        glGenerateMipmap(GL_TEXTURE_2D)
        modo = GL_REPEAT if repetir else GL_CLAMP_TO_EDGE
        glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_WRAP_S, modo)
        glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_WRAP_T, modo)
        glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MIN_FILTER, GL_LINEAR_MIPMAP_LINEAR)
        glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MAG_FILTER, GL_LINEAR)
        self._anisotropia()

    @staticmethod
    def _anisotropia():
        """Filtro anisotropico (se a placa suportar): chao nao fica borrado ao longe."""
        try:
            from OpenGL.GL.EXT.texture_filter_anisotropic import (
                GL_TEXTURE_MAX_ANISOTROPY_EXT, GL_MAX_TEXTURE_MAX_ANISOTROPY_EXT)
            maximo = glGetFloatv(GL_MAX_TEXTURE_MAX_ANISOTROPY_EXT)
            glTexParameterf(GL_TEXTURE_2D, GL_TEXTURE_MAX_ANISOTROPY_EXT, min(8.0, float(maximo)))
        except Exception:
            pass


def carregar_textura(nome):
    """Carrega texturas/<nome> uma unica vez (cache) e reaproveita nas demais malhas."""
    if nome not in _cache:
        _cache[nome] = Textura(os.path.join(PASTA_TEXTURAS, nome))
    return _cache[nome]
