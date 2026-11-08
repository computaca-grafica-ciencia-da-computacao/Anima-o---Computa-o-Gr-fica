"""Trator x Caracol robotico - Computacao Grafica (pygame + PyOpenGL).

Controles: arrastar com o mouse = orbitar | roda = zoom | R = reiniciar |
           P = pausar | ESC = sair
"""
import pygame
from core.camera import CameraOrbital
from core.renderer import Renderer
from cena import Cena


def criar_janela(largura, altura):
    gl = pygame.display
    gl.gl_set_attribute(pygame.GL_CONTEXT_MAJOR_VERSION, 3)
    gl.gl_set_attribute(pygame.GL_CONTEXT_MINOR_VERSION, 3)
    gl.gl_set_attribute(pygame.GL_CONTEXT_PROFILE_MASK, pygame.GL_CONTEXT_PROFILE_CORE)
    gl.gl_set_attribute(pygame.GL_CONTEXT_FORWARD_COMPATIBLE_FLAG, True)
    gl.gl_set_attribute(pygame.GL_DEPTH_SIZE, 24)
    flags = pygame.OPENGL | pygame.DOUBLEBUF | pygame.RESIZABLE
    try:   # antialiasing; se a placa nao suportar, abre sem
        gl.gl_set_attribute(pygame.GL_MULTISAMPLEBUFFERS, 1)
        gl.gl_set_attribute(pygame.GL_MULTISAMPLESAMPLES, 4)
        return gl.set_mode((largura, altura), flags)
    except pygame.error:
        gl.gl_set_attribute(pygame.GL_MULTISAMPLEBUFFERS, 0)
        gl.gl_set_attribute(pygame.GL_MULTISAMPLESAMPLES, 0)
        return gl.set_mode((largura, altura), flags)


def main():
    pygame.init()
    tela = criar_janela(1100, 700)
    renderer = Renderer()
    camera = CameraOrbital()
    cena = Cena()
    relogio = pygame.time.Clock()
    tamanho, pausado, rodando = (0, 0), False, True

    while rodando:
        dt = min(relogio.tick(60) / 1000.0, 0.05)
        for e in pygame.event.get():
            if e.type == pygame.QUIT:
                rodando = False
            elif e.type == pygame.KEYDOWN:
                if e.key == pygame.K_ESCAPE:
                    rodando = False
                elif e.key == pygame.K_r:
                    cena.reiniciar()
                elif e.key == pygame.K_p:
                    pausado = not pausado
            camera.evento(e)

        if not pausado:
            cena.atualizar(dt)

        w, h = pygame.display.get_surface().get_size()
        if (w, h) != tamanho:
            tamanho = (w, h)
            renderer.redimensionar(w, h)
        renderer.renderizar(cena, camera, w / max(h, 1))
        pygame.display.set_caption(f"Trator x Caracol  |  {cena.fase}")
        pygame.display.flip()

    pygame.quit()


if __name__ == "__main__":
    main()
