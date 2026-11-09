"""Gera as texturas de imagem (PNG, 512x512, ladrilhaveis) usadas na cena.

As imagens sao de autoria propria: geradas por este script com ruido filtrado no dominio da
frequencia (numpy). Nao ha imagens de terceiros. Uso (opcional, os PNGs ja estao no projeto):
    pip install pillow
    python tools/gerar_texturas.py
"""
import os
import numpy as np
from PIL import Image

N = 512
RAIZ = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SAIDA = os.path.join(RAIZ, "texturas")


def ruido(rng, sigma_x, sigma_y=None):
    """Ruido suave que se repete nas bordas (filtro gaussiano via FFT => periodico)."""
    sigma_y = sigma_x if sigma_y is None else sigma_y
    base = np.fft.fft2(rng.standard_normal((N, N)))
    fx = np.fft.fftfreq(N)[None, :]
    fy = np.fft.fftfreq(N)[:, None]
    filtro = np.exp(-0.5 * ((2 * np.pi * fx * sigma_x) ** 2 + (2 * np.pi * fy * sigma_y) ** 2))
    r = np.real(np.fft.ifft2(base * filtro))
    return (r - r.min()) / (r.max() - r.min())


def misturar(t, escuro, claro):
    escuro, claro = np.array(escuro, float), np.array(claro, float)
    return escuro + t[..., None] * (claro - escuro)


def salvar(nome, rgb):
    Image.fromarray(np.clip(rgb, 0, 255).astype(np.uint8)).save(os.path.join(SAIDA, nome))
    print("gerada:", nome)


def grama(rng):
    t = 0.45 * ruido(rng, 28) + 0.30 * ruido(rng, 7) + 0.25 * ruido(rng, 0.9, 3.5)  # lâminas verticais
    t = (t - t.min()) / (t.max() - t.min())
    img = misturar(t, (42, 98, 38), (112, 168, 66))
    manchas = ruido(rng, 40)
    img *= (0.88 + 0.24 * manchas)[..., None]
    return img


def asfalto(rng):
    t = 0.5 * ruido(rng, 22) + 0.5 * ruido(rng, 0.8)
    t = (t - t.min()) / (t.max() - t.min())
    img = misturar(t, (72, 70, 70), (112, 110, 108))
    pedras = rng.random((N, N)) > 0.985
    img[pedras] += rng.uniform(25, 60, size=(pedras.sum(), 1))
    return img


def terra(rng):
    t = 0.55 * ruido(rng, 20) + 0.30 * ruido(rng, 5) + 0.15 * ruido(rng, 1.2)
    t = (t - t.min()) / (t.max() - t.min())
    img = misturar(t, (104, 76, 46), (160, 124, 80))
    seixos = ruido(rng, 1.6) > 0.80
    img[seixos] *= 0.72
    return img


if __name__ == "__main__":
    os.makedirs(SAIDA, exist_ok=True)
    salvar("grama.png", grama(np.random.default_rng(1)))
    salvar("asfalto.png", asfalto(np.random.default_rng(2)))
    salvar("terra.png", terra(np.random.default_rng(3)))
