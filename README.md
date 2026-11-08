# Trator x Caracol Robótico

Cena 3D animada em Python (pygame + PyOpenGL + numpy) para a disciplina de Computação Gráfica.
Um trator avança com as rodas girando e para para esperar um caracol robótico atravessar a pista;
o caracol olha confuso para o trator e segue seu caminho; depois o trator retoma a marcha.

## Como rodar
```
python -m venv .venv
.venv\Scripts\activate        # Linux/Mac: source .venv/bin/activate
pip install -r requirements.txt
python main.py
```
Controles: arrastar o mouse = orbitar a câmera | roda = zoom | R = reiniciar | P = pausar | ESC = sair

## Estrutura
- `core/` – matrizes, shaders, grafo de cena (Object3D/Mesh), câmera orbital e renderer
- `geometry/` – geometrias (caixa, cilindro, esfera)
- `objetos/` – modelos e animações do trator e do caracol
- `cena.py` – ambiente e sequência (máquina de estados) da dupla
- `main.py` – janela, laço principal e eventos

## Sequência da cena
1. Trator avança com as rodas girando (rolamento sem deslizar: ângulo = distância / raio).
2. Trator freia suavemente até a linha de parada, enquanto o caracol se aproxima da pista.
3. Caracol desliza, para, vira a cabeça para o trator (antenas em oposição) e segue.
4. Pista livre: trator acelera e sai de cena. A cena reinicia sozinha.
