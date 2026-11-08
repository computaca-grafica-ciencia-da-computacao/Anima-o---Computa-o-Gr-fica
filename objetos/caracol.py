"""Caracol robotico. Frente do caracol = eixo +X local; o grupo gira -90 graus em Y
para caminhar rumo a +Z no mundo (atravessando a pista do trator)."""
import math
from core.object3d import Object3D, adicionar_malha
from core.util import aproximar
from geometry.shapes import caixa, cilindro, esfera

COR_CORPO = (0.55, 0.64, 0.60)
COR_CONCHA = (0.80, 0.45, 0.12)
COR_METAL = (0.65, 0.67, 0.70)
COR_ESTEIRA = (0.10, 0.10, 0.12)
COR_LED = (0.20, 0.95, 1.00)


class Caracol(Object3D):
    ESCALA = 1.8
    VEL = 1.3
    Z_INICIO = -9.5
    Z_CONFUSAO = -0.8    # ao chegar aqui (de frente para o trator), ele hesita
    T_CONFUSAO = 2.4     # segundos de "confusao"

    def __init__(self):
        super().__init__("caracol")
        self.rotation[1] = -math.pi / 2
        self.scale[:] = self.ESCALA      # caracol maior que o real, para destacar a cena
        self._montar()
        self.reiniciar()

    # ---------- modelagem ----------
    def _montar(self):
        adicionar_malha(self, caixa(1.1, 0.1, 0.5), COR_ESTEIRA, pos=(0, 0.05, 0))
        self.pe = adicionar_malha(self, esfera(0.5), COR_CORPO, pos=(0, 0.16, 0),
                                  escala=(1.3, 0.3, 0.6))
        self.concha = adicionar_malha(self, esfera(0.4), COR_CONCHA, pos=(-0.15, 0.62, 0),
                                      escala=(1, 1, 0.9), brilho=64, especular=0.6)
        for lado in (1, -1):   # placas metalicas dos dois lados da concha
            adicionar_malha(self.concha, cilindro(0.2, 0.05), COR_METAL,
                            pos=(0, 0, 0.345 * lado), rot=(math.pi / 2, 0, 0),
                            brilho=80, especular=0.8)
            adicionar_malha(self.concha, cilindro(0.1, 0.04), COR_LED,
                            pos=(0, 0, 0.375 * lado), rot=(math.pi / 2, 0, 0))
        # cabeca em um pivo (para poder girar na direcao do trator)
        self.cabeca = self.add(Object3D("cabeca"))
        self.cabeca.position[:] = (0.55, 0.28, 0)
        adicionar_malha(self.cabeca, esfera(0.17), COR_CORPO, pos=(0, 0.1, 0), escala=(1, 1.5, 1))
        adicionar_malha(self.cabeca, esfera(0.2), COR_CORPO, pos=(0.1, 0.36, 0))
        self.antenas = []
        for lado in (1, -1):
            piv = self.cabeca.add(Object3D("antena"))
            piv.position[:] = (0.12, 0.52, 0.1 * lado)
            adicionar_malha(piv, cilindro(0.025, 0.4), COR_METAL, pos=(0, 0.2, 0))
            adicionar_malha(piv, esfera(0.065), COR_LED, pos=(0, 0.42, 0))
            self.antenas.append((piv, lado))

    # ---------- animacao ----------
    def reiniciar(self):
        self.position[:] = (0, 0, self.Z_INICIO)
        self.estado = "andando"      # andando | confuso
        self.ja_olhou = False
        self.timer = 0.0
        self.vel = 0.0
        self.fase_corpo = 0.0
        self.fase_ant = 0.0
        self.amp, self.freq, self.defasagem = 0.18, 2.5, 0.7

    @property
    def z(self):
        return float(self.position[2])

    def atualizar(self, dt):
        # --- maquina de estados ---
        if self.estado == "andando":
            if self.z >= self.Z_CONFUSAO and not self.ja_olhou:
                self.estado, self.timer, self.ja_olhou = "confuso", 0.0, True
        else:
            self.timer += dt
            if self.timer >= self.T_CONFUSAO:
                self.estado = "andando"
        confuso = self.estado == "confuso"

        # --- deslizar (para suavemente durante a confusao) ---
        self.vel = aproximar(self.vel, 0.0 if confuso else self.VEL, 6, dt)
        self.position[2] += self.vel * dt
        self.fase_corpo += self.vel * dt * 7
        self.pe.scale[0] = 1.3 * (1 + 0.05 * math.sin(self.fase_corpo))
        self.concha.position[1] = 0.62 + 0.01 * math.sin(self.fase_corpo * 2)

        # --- antenas: balanco calmo normal; rapido e em oposicao quando confuso ---
        self.amp = aproximar(self.amp, 0.55 if confuso else 0.18, 5, dt)
        self.freq = aproximar(self.freq, 5.0 if confuso else 2.5, 5, dt)
        self.defasagem = aproximar(self.defasagem, math.pi if confuso else 0.7, 5, dt)
        self.fase_ant += self.freq * dt
        for piv, lado in self.antenas:
            fase = self.fase_ant + (self.defasagem if lado < 0 else 0.0)
            piv.rotation[2] = self.amp * math.sin(fase)
            piv.rotation[0] = lado * (0.25 + 0.08 * math.sin(fase * 0.7))

        # --- cabeca: vira para o trator (lado -X do mundo = +Z local) e inclina ---
        self.cabeca.rotation[1] = aproximar(float(self.cabeca.rotation[1]), -0.95 if confuso else 0.0, 6, dt)
        self.cabeca.rotation[2] = aproximar(float(self.cabeca.rotation[2]), 0.3 if confuso else 0.0, 5, dt)
