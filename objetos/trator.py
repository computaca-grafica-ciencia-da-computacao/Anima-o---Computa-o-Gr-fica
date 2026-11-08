"""Trator estilizado. Frente do trator = eixo +X. Rodas giram em torno do eixo Z."""
import math
from core.object3d import Object3D, adicionar_malha
from core.util import aproximar
from geometry.shapes import caixa, cilindro, esfera

COR_CORPO = (0.80, 0.15, 0.10)
COR_CHASSI = (0.18, 0.18, 0.20)
COR_VIDRO = (0.30, 0.55, 0.70)
COR_PNEU = (0.07, 0.07, 0.08)
COR_ARO = (0.95, 0.75, 0.10)
COR_FAROL = (1.00, 0.95, 0.70)


class Trator(Object3D):
    VEL_MAX = 4.5     # unidades/s
    ACEL = 3.5        # aceleracao
    FREIO = 8.0       # desaceleracao maxima

    def __init__(self):
        super().__init__("trator")
        self.velocidade = 0.0
        self.tempo = 0.0
        self.rodas = []                 # lista de (pivo, raio)
        self.corpo = self.add(Object3D("corpo"))
        self._montar_corpo()
        self._montar_rodas()

    # ---------- modelagem ----------
    def _montar_corpo(self):
        c = self.corpo
        adicionar_malha(c, caixa(3.4, 0.5, 1.1), COR_CHASSI, pos=(0, 1.0, 0))
        adicionar_malha(c, caixa(1.5, 0.8, 0.9), COR_CORPO, pos=(1.0, 1.65, 0))      # capo
        adicionar_malha(c, caixa(0.12, 0.5, 0.7), COR_CHASSI, pos=(1.78, 1.55, 0))   # grade
        adicionar_malha(c, caixa(1.2, 1.3, 1.2), COR_CORPO, pos=(-0.7, 1.9, 0))      # cabine
        adicionar_malha(c, caixa(0.9, 0.75, 1.24), COR_VIDRO, pos=(-0.7, 2.0, 0),
                        brilho=90, especular=0.9)                                    # vidros laterais
        adicionar_malha(c, caixa(1.24, 0.75, 0.9), COR_VIDRO, pos=(-0.7, 2.0, 0),
                        brilho=90, especular=0.9)                                    # vidros frente/tras
        adicionar_malha(c, caixa(1.5, 0.1, 1.5), COR_CHASSI, pos=(-0.7, 2.6, 0))     # teto
        adicionar_malha(c, cilindro(0.06, 0.8), COR_CHASSI, pos=(1.25, 2.45, 0.25))  # escape
        for lado in (1, -1):
            adicionar_malha(c, esfera(0.1), COR_FAROL, pos=(1.82, 1.55, 0.28 * lado),
                            brilho=120, especular=0.9)
            adicionar_malha(c, caixa(2.0, 0.08, 0.65), COR_CORPO,
                            pos=(-0.9, 1.92, 0.88 * lado))                           # paralama

    def _roda(self, x, z, raio, largura):
        pivo = self.add(Object3D("roda"))
        pivo.position[:] = (x, raio, z)
        eixo_z = (math.pi / 2, 0, 0)   # cilindro nasce com eixo Y; giramos para o eixo Z
        adicionar_malha(pivo, cilindro(raio * 0.9, largura), COR_PNEU, rot=eixo_z,
                        brilho=8, especular=0.05)
        adicionar_malha(pivo, cilindro(raio * 0.5, largura + 0.06), COR_ARO, rot=eixo_z)
        # barra no cubo: deixa a rotacao bem visivel
        adicionar_malha(pivo, caixa(raio * 0.9, raio * 0.08, largura + 0.08), COR_CHASSI)
        # garras do pneu (geometria compartilhada entre todas)
        garra = caixa(raio * 0.2, raio * 0.16, largura * 1.02)
        n = 10
        for i in range(n):
            a = 2 * math.pi * i / n
            adicionar_malha(pivo, garra, COR_PNEU,
                            pos=(raio * 0.9 * math.cos(a), raio * 0.9 * math.sin(a), 0),
                            rot=(0, 0, a), brilho=8, especular=0.05)
        self.rodas.append((pivo, raio))

    def _montar_rodas(self):
        for lado in (1, -1):
            self._roda(-0.9, 0.88 * lado, 0.9, 0.5)    # traseiras (grandes)
            self._roda(1.25, 0.80 * lado, 0.55, 0.35)  # dianteiras (pequenas)

    # ---------- animacao ----------
    def reiniciar(self, x_inicial):
        self.position[:] = (x_inicial, 0, 0)
        self.velocidade = self.VEL_MAX

    def atualizar(self, dt, vel_alvo, x_max=None):
        """Acelera/freia ate vel_alvo, anda, gira as rodas. x_max = linha de parada."""
        self.tempo += dt
        dv = vel_alvo - self.velocidade
        lim = (self.ACEL if dv > 0 else self.FREIO) * dt
        self.velocidade += max(-lim, min(lim, dv))
        self.position[0] += self.velocidade * dt
        if x_max is not None and x_max - self.position[0] < 0.01:
            self.position[0] = x_max
            self.velocidade = 0.0
        for pivo, raio in self.rodas:
            pivo.rotation[2] -= self.velocidade * dt / raio   # rolamento sem deslizar
        # motor ligado: vibra mesmo parado, mais forte em movimento
        amp = 0.004 + 0.012 * abs(self.velocidade) / self.VEL_MAX
        self.corpo.position[1] = amp * math.sin(self.tempo * 45)
