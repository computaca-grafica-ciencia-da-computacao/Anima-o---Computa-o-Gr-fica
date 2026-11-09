import ctypes
import numpy as np
from OpenGL.GL import *


class Geometry:
    """Vertices intercalados (posicao + normal + uv) e indices.

    Atributos de vertice (mesmo layout em todas as formas):
        location 0 -> aPos    (vec3)  offset  0 bytes
        location 1 -> aNormal (vec3)  offset 12 bytes
        location 2 -> aUV     (vec2)  offset 24 bytes
    O upload para a GPU e feito so no primeiro desenho (assim a geometria pode
    ser criada sem contexto GL)."""

    FLOATS_POR_VERTICE = 8
    STRIDE = FLOATS_POR_VERTICE * 4

    def __init__(self, vertices, indices):
        self.vertices = np.array(vertices, dtype=np.float32).reshape(-1, self.FLOATS_POR_VERTICE)
        self.indices = np.array(indices, dtype=np.uint32)
        self._vao = None

    def _enviar_para_gpu(self):
        self._vao = glGenVertexArrays(1)
        glBindVertexArray(self._vao)
        vbo = glGenBuffers(1)
        glBindBuffer(GL_ARRAY_BUFFER, vbo)
        glBufferData(GL_ARRAY_BUFFER, self.vertices.nbytes, self.vertices, GL_STATIC_DRAW)
        ebo = glGenBuffers(1)
        glBindBuffer(GL_ELEMENT_ARRAY_BUFFER, ebo)
        glBufferData(GL_ELEMENT_ARRAY_BUFFER, self.indices.nbytes, self.indices, GL_STATIC_DRAW)
        glVertexAttribPointer(0, 3, GL_FLOAT, GL_FALSE, self.STRIDE, ctypes.c_void_p(0))
        glEnableVertexAttribArray(0)
        glVertexAttribPointer(1, 3, GL_FLOAT, GL_FALSE, self.STRIDE, ctypes.c_void_p(12))
        glEnableVertexAttribArray(1)
        glVertexAttribPointer(2, 2, GL_FLOAT, GL_FALSE, self.STRIDE, ctypes.c_void_p(24))
        glEnableVertexAttribArray(2)

    def desenhar(self):
        if self._vao is None:
            self._enviar_para_gpu()
        glBindVertexArray(self._vao)
        glDrawElements(GL_TRIANGLES, len(self.indices), GL_UNSIGNED_INT, None)
