import numpy as np
from OpenGL.GL import *
from core.shaders import criar_programa, criar_programa_sombra
from core.object3d import Mesh
from core.shadow import Sombra
from core.texture import Textura


class Renderer:
    UNIDADE_TEXTURA = 0     # textura de imagem (uTextura)
    UNIDADE_SOMBRA = 1      # mapa de sombra (uSombraMapa)

    def __init__(self, cor_ceu=(0.55, 0.76, 0.93), resolucao_sombra=2048):
        self.cor_ceu = cor_ceu
        self.programa = criar_programa()
        self.programa_sombra = criar_programa_sombra()
        glEnable(GL_DEPTH_TEST)
        nomes = ["uModel", "uView", "uProj", "uColor", "uLightDir", "uCamPos", "uShininess",
                 "uSpecular", "uUsaTextura", "uTextura", "uRecebeSombra", "uSombraMapa",
                 "uSombraForca", "uSombraBias", "uSombraView", "uSombraProj"]
        self.loc = {n: glGetUniformLocation(self.programa, n) for n in nomes}
        self.loc_sombra = {n: glGetUniformLocation(self.programa_sombra, n)
                           for n in ("uModel", "uView", "uProj")}
        self.luz = np.array([0.5, 1.0, 0.6], dtype=np.float32)   # direcao PARA a luz
        self.sombra = Sombra(resolucao_sombra)
        self.sombra.posicionar(self.luz)
        self.textura_branca = Textura()
        self.largura, self.altura = 1, 1

    def redimensionar(self, w, h):
        self.largura, self.altura = w, h
        glViewport(0, 0, w, h)

    def renderizar(self, cena, camera, aspecto):
        malhas = [o for o in cena.descendentes() if isinstance(o, Mesh)]
        self._passe_sombra(malhas)
        self._passe_principal(malhas, camera, aspecto)

    # ---- passe 1: cena vista pela luz -> mapa de sombra (refeito a cada quadro) ----
    def _passe_sombra(self, malhas):
        s = self.sombra
        glUseProgram(self.programa_sombra)
        glUniformMatrix4fv(self.loc_sombra["uView"], 1, GL_TRUE, s.view)
        glUniformMatrix4fv(self.loc_sombra["uProj"], 1, GL_TRUE, s.proj)
        s.iniciar_passe()
        for m in malhas:
            if m.projeta_sombra:
                m.desenhar_sombra(self.loc_sombra)
        s.encerrar_passe(self.largura, self.altura)

    # ---- passe 2: cena vista pela camera, consultando o mapa de sombra ----
    def _passe_principal(self, malhas, camera, aspecto):
        s, loc = self.sombra, self.loc
        glClearColor(*self.cor_ceu, 1.0)
        glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)
        glUseProgram(self.programa)
        glUniformMatrix4fv(loc["uView"], 1, GL_TRUE, camera.view())
        glUniformMatrix4fv(loc["uProj"], 1, GL_TRUE, camera.projecao(aspecto))
        glUniform3f(loc["uCamPos"], *camera.posicao())
        glUniform3f(loc["uLightDir"], *self.luz)
        glUniformMatrix4fv(loc["uSombraView"], 1, GL_TRUE, s.view)
        glUniformMatrix4fv(loc["uSombraProj"], 1, GL_TRUE, s.proj)
        glUniform1f(loc["uSombraForca"], s.forca)
        glUniform1f(loc["uSombraBias"], s.bias)
        glUniform1i(loc["uTextura"], self.UNIDADE_TEXTURA)
        glUniform1i(loc["uSombraMapa"], self.UNIDADE_SOMBRA)
        glActiveTexture(GL_TEXTURE0 + self.UNIDADE_SOMBRA)
        glBindTexture(GL_TEXTURE_2D, s.textura)
        glActiveTexture(GL_TEXTURE0 + self.UNIDADE_TEXTURA)
        glBindTexture(GL_TEXTURE_2D, self.textura_branca.id)
        for m in malhas:
            m.desenhar(loc)
