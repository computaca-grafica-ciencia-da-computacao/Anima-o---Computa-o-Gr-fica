"""Cena completa: ambiente + trator + caracol e a sequencia da dupla."""
import random
from core.object3d import Object3D, adicionar_malha
from core.util import limitar
from geometry.shapes import caixa, cilindro, esfera
from objetos.trator import Trator
from objetos.caracol import Caracol


class Cena(Object3D):
    X_INICIO = -11.0
    X_PARADA = -3.4      # linha de parada do trator (o caracol cruza em x = 0)
    X_FIM = 15.0
    Z_LIBERA = 4.4       # caracol alem daqui = pista livre
    K_FREIO = 1.2        # quanto maior, mais tarde o trator freia

    def __init__(self):
        super().__init__("cena")
        self._ambiente()
        self.trator = self.add(Trator())
        self.caracol = self.add(Caracol())
        self.fase = ""
        self.reiniciar()

    def _ambiente(self):
        adicionar_malha(self, caixa(70, 0.2, 70), (0.30, 0.55, 0.25), pos=(0, -0.1, 0),
                        especular=0.02)                                    # grama
        adicionar_malha(self, caixa(70, 0.04, 5), (0.35, 0.33, 0.32), pos=(0, 0.0, 0),
                        especular=0.05)                                    # pista do trator
        adicionar_malha(self, caixa(1.4, 0.04, 30), (0.55, 0.42, 0.26), pos=(0, 0.01, 0),
                        especular=0.02)                                    # trilha do caracol
        faixa = caixa(1.2, 0.03, 0.12)
        for x in range(-30, 31, 3):
            if abs(x) > 2:
                adicionar_malha(self, faixa, (0.9, 0.9, 0.85), pos=(x, 0.015, 0), especular=0.02)
        rnd = random.Random(7)
        tronco, copa = cilindro(0.18, 1.2), esfera(0.9)
        for _ in range(9):
            x, z = rnd.uniform(-22, 22), rnd.uniform(-15, -8)
            if abs(x) < 2.5:
                continue
            adicionar_malha(self, tronco, (0.35, 0.22, 0.12), pos=(x, 0.6, z))
            adicionar_malha(self, copa, (0.15, 0.42, 0.18), pos=(x, 1.9, z), especular=0.05)
        pedra = esfera(0.5)
        for x, z in [(-6, 5.5), (5, 6.2), (9, -4.5), (-13, 4.8)]:
            adicionar_malha(self, pedra, (0.5, 0.5, 0.52), pos=(x, 0.2, z),
                            escala=(1, 0.6, 0.8), especular=0.1)

    def reiniciar(self):
        self.trator.reiniciar(self.X_INICIO)
        self.caracol.reiniciar()
        self.tempo_fim = 0.0

    def atualizar(self, dt):
        t, c = self.trator, self.caracol
        c.atualizar(dt)

        # O trator so precisa esperar se o caracol ainda nao liberou a pista
        # e o trator ainda nao passou do ponto de cruzamento.
        bloqueado = c.z < self.Z_LIBERA and t.position[0] < 0
        if bloqueado:
            alvo = limitar(self.K_FREIO * (self.X_PARADA - t.position[0]), 0.0, t.VEL_MAX)
            t.atualizar(dt, alvo, x_max=self.X_PARADA)
        else:
            t.atualizar(dt, t.VEL_MAX)

        if c.estado == "confuso":
            self.fase = "Caracol olha confuso para o trator"
        elif bloqueado and t.velocidade < 0.05:
            self.fase = "Trator parado, esperando o caracol atravessar"
        elif bloqueado:
            self.fase = "Trator avancando / freando"
        else:
            self.fase = "Pista livre: trator retoma a marcha"

        if t.position[0] > self.X_FIM:      # fim: espera um pouco e recomeca
            self.tempo_fim += dt
            if self.tempo_fim > 2.0:
                self.reiniciar()
