"""Shadow mapping para luz direcional (secao 6.9 do livro, adaptado).

Passe de sombra: a cena e desenhada do ponto de vista da luz (camera ortografica,
'camera da sombra') em um framebuffer. A textura resultante guarda, para cada pixel,
a distancia ate o ponto da cena mais proximo da luz (a 'textura de profundidade').
No passe principal o fragment shader compara a distancia de cada fragmento com esse
valor: se for maior, existe algo mais perto da luz -> o fragmento esta em sombra.

Diferencas em relacao ao livro: a textura e R32F (float de 32 bits, em vez de RGBA 8 bits),
o que evita bandas de precisao, e o framebuffer e criado aqui (o livro usa a classe RenderTarget)."""
import numpy as np
from OpenGL.GL import *
from core import matrix as M


class Sombra:
    def __init__(self, resolucao=2048, centro=(2.0, 0.0, -2.0), raio=24.0, distancia=30.0,
                 forca=0.65, bias=0.004):
        self.resolucao = resolucao
        self.centro = np.array(centro, dtype=np.float32)   # centro da regiao que recebe sombra
        self.raio = raio                                    # meia-largura da caixa da camera da sombra
        self.distancia = distancia                          # distancia da camera da sombra ao centro
        self.forca = forca                                  # 0 = sem sombra, 1 = sombra totalmente escura
        self.bias = bias                                    # evita 'shadow acne' (autossombreamento)
        self.view = M.identidade()
        self.proj = M.ortografica(-raio, raio, -raio, raio, 0.1, distancia + raio)
        self._criar_alvo()

    def _criar_alvo(self):
        n = self.resolucao
        self.textura = glGenTextures(1)
        glBindTexture(GL_TEXTURE_2D, self.textura)
        glTexImage2D(GL_TEXTURE_2D, 0, GL_R32F, n, n, 0, GL_RED, GL_FLOAT, None)
        glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MIN_FILTER, GL_NEAREST)
        glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MAG_FILTER, GL_NEAREST)
        # fora da caixa da camera da sombra a leitura devolve 1.0 (branco) -> nunca ha sombra
        glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_WRAP_S, GL_CLAMP_TO_BORDER)
        glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_WRAP_T, GL_CLAMP_TO_BORDER)
        glTexParameterfv(GL_TEXTURE_2D, GL_TEXTURE_BORDER_COLOR, [1.0, 1.0, 1.0, 1.0])
        profundidade = glGenRenderbuffers(1)
        glBindRenderbuffer(GL_RENDERBUFFER, profundidade)
        glRenderbufferStorage(GL_RENDERBUFFER, GL_DEPTH_COMPONENT24, n, n)
        self.fbo = glGenFramebuffers(1)
        glBindFramebuffer(GL_FRAMEBUFFER, self.fbo)
        glFramebufferTexture2D(GL_FRAMEBUFFER, GL_COLOR_ATTACHMENT0, GL_TEXTURE_2D, self.textura, 0)
        glFramebufferRenderbuffer(GL_FRAMEBUFFER, GL_DEPTH_ATTACHMENT, GL_RENDERBUFFER, profundidade)
        if glCheckFramebufferStatus(GL_FRAMEBUFFER) != GL_FRAMEBUFFER_COMPLETE:
            raise RuntimeError("Framebuffer da sombra incompleto")
        glBindFramebuffer(GL_FRAMEBUFFER, 0)

    def posicionar(self, luz):
        """Coloca a camera da sombra na direcao da luz, olhando para o centro da cena."""
        d = np.array(luz, dtype=np.float32)
        d /= np.linalg.norm(d)
        self.view = M.olhar_para(self.centro + d * self.distancia, self.centro)

    def iniciar_passe(self):
        glBindFramebuffer(GL_FRAMEBUFFER, self.fbo)
        glViewport(0, 0, self.resolucao, self.resolucao)
        glClearColor(1.0, 1.0, 1.0, 1.0)      # branco = "nada bloqueia a luz aqui"
        glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)

    def encerrar_passe(self, largura, altura):
        glBindFramebuffer(GL_FRAMEBUFFER, 0)
        glViewport(0, 0, largura, altura)
