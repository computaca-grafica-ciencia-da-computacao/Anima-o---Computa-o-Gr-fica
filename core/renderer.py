import numpy as np
from OpenGL.GL import *
from core.shaders import criar_programa
from core.object3d import Mesh


class Renderer:
    def __init__(self, cor_ceu=(0.55, 0.76, 0.93)):
        self.programa = criar_programa()
        glEnable(GL_DEPTH_TEST)
        glClearColor(*cor_ceu, 1.0)
        nomes = ["uModel", "uView", "uProj", "uColor", "uLightDir",
                 "uCamPos", "uShininess", "uSpecular"]
        self.loc = {n: glGetUniformLocation(self.programa, n) for n in nomes}
        self.luz = np.array([0.5, 1.0, 0.6], dtype=np.float32)

    def redimensionar(self, w, h):
        glViewport(0, 0, w, h)

    def renderizar(self, cena, camera, aspecto):
        glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)
        glUseProgram(self.programa)
        glUniformMatrix4fv(self.loc["uView"], 1, GL_TRUE, camera.view())
        glUniformMatrix4fv(self.loc["uProj"], 1, GL_TRUE, camera.projecao(aspecto))
        glUniform3f(self.loc["uCamPos"], *camera.posicao())
        glUniform3f(self.loc["uLightDir"], *self.luz)
        for obj in cena.descendentes():
            if isinstance(obj, Mesh):
                obj.desenhar(self.loc)
