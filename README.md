# Trator x Caracol Robótico

Trabalho Prático de Computação Gráfica — Ciência da Computação, UNIPAC, 2026/02.
Cena 3D animada em Python (pygame + PyOpenGL + numpy), baseada no framework do livro
*Developing Graphics Frameworks with Python and OpenGL* (Stemkoski e Pascale, 2022).

## Integrantes e temas sorteados na sala

> **PREENCHER antes da entrega.**

| Integrante | Matrícula | Tema sorteado |
|---|---|---|
| [Gabriel Augusto Bedeschi Domingos] | [241-007248] | 14. Trator estilizado (ou 30 — conferir o sorteio) |
| [João Emanuel] | [matrícula] | 30. Caracol robótico (ou 14 — conferir o sorteio) |

## Descrição da cena e da interação

Um trator vermelho avança por uma pista de asfalto, com as rodas girando, enquanto um caracol
robótico caminha por uma trilha de terra que cruza a pista. A sequência é coordenada nos dois sentidos:

1. O trator avança e **freia suavemente** até a linha de parada, porque o caracol ainda não liberou a pista.
2. O caracol chega à pista, **percebe o trator** (distância e velocidade dele), para e **vira a cabeça**
   para o trator, com as antenas balançando em oposição. Ele só volta a andar depois que o trator parou.
3. O caracol termina a travessia. Só então o trator **retoma a marcha** e sai de cena.
4. A cena reinicia sozinha.

Não são dois movimentos independentes: o trator depende da posição do caracol (`Cena.atualizar`,
variável `bloqueado`) e o caracol depende da posição e da velocidade do trator (`Caracol.atualizar`,
parâmetros `trator_x` e `trator_vel`). O nome da fase atual aparece no título da janela.

## Instalação e execução

Requer Python 3.10+ e uma placa/driver com OpenGL 3.3 ou superior.
Testado com Python 3.12, pygame 2.6.1, PyOpenGL 3.1.10 e numpy 2.5.4.

```
python -m venv .venv
.venv\Scripts\activate        # Linux/Mac: source .venv/bin/activate
pip install -r requirements.txt
python main.py
```

## Controles

| Tecla / mouse | Ação |
|---|---|
| Setas ←/→ ou A/D | Orbitar a câmera |
| Setas ↑/↓ | Inclinar a câmera |
| W/S (ou +/−) | Aproximar / afastar |
| Mouse: arrastar / roda | Orbitar / zoom |
| P | Pausar e retomar a animação (a câmera continua funcionando) |
| R | Reiniciar a sequência |
| ESC | Sair |

## Onde estão os recursos gráficos

| Recurso | Arquivo | Classe / função |
|---|---|---|
| Laço principal, `dt`, pausa, eventos | `main.py` | `main()` |
| Movimentos controlados pelo tempo (independem do FPS) | `main.py`, `cena.py`, `objetos/` | `dt` em `main()`; `Cena.atualizar`, `Trator.atualizar`, `Caracol.atualizar` |
| Translação, rotação e escala | `core/matrix.py`, `core/object3d.py` | `translacao`, `rotacao_*`, `escala`; `Object3D.matriz_local` |
| Hierarquia (grafo de cena) | `core/object3d.py` | `Object3D.add`, `matriz_mundo` (rodas filhas do trator, antenas filhas da cabeça) |
| Modelagem por formas geométricas | `geometry/shapes.py`, `objetos/` | `caixa`, `cilindro`, `esfera`; `Trator._montar_corpo`, `Caracol._montar` |
| Câmera em perspectiva + teclado | `core/camera.py`, `core/matrix.py` | `CameraOrbital.teclado`, `perspectiva`, `olhar_para` |
| Textura de imagem + coordenadas UV | `core/texture.py`, `geometry/shapes.py`, `cena.py` | `Textura`, `carregar_textura`; UV em `caixa(uv_por_unidade=...)`; uso em `Cena._ambiente` |
| Iluminação direcional, normais, material | `core/shaders.py`, `core/object3d.py` | `FRAGMENT` (ambiente + difusa + especular Blinn-Phong); `Mesh.brilho`, `Mesh.especular` |
| Sombra por shadow mapping (seção 6.9) | `core/shadow.py`, `core/renderer.py`, `core/shaders.py` | `Sombra`; `Renderer._passe_sombra`; `calcularSombra` no `FRAGMENT` |
| Pistas de interação | `cena.py`, `objetos/caracol.py` | `Fase`, `Cena.atualizar`, `Caracol.atualizar` |

## Shaders, atributos de vértice e uniforms

Os shaders estão em `core/shaders.py`, como strings GLSL 3.30 core (como no livro).

**Atributos de vértice** (`geometry/geometry.py`, um VBO intercalado de 32 bytes por vértice):

| location | Nome | Tipo | Uso |
|---|---|---|---|
| 0 | `aPos` | vec3 | posição no espaço do objeto |
| 1 | `aNormal` | vec3 | normal da superfície (iluminação) |
| 2 | `aUV` | vec2 | coordenada de textura |

**Uniforms do programa principal** (enviados em `Renderer._passe_principal` e `Mesh.desenhar`):

| Uniform | Significado |
|---|---|
| `uModel` | matriz de modelo (mundo) do objeto: translação, rotação e escala acumuladas na hierarquia |
| `uView`, `uProj` | matrizes de visão e projeção em perspectiva da câmera |
| `uCamPos` | posição da câmera (cálculo do brilho especular) |
| `uLightDir` | direção da superfície para a luz direcional |
| `uColor`, `uShininess`, `uSpecular` | material: cor (ou tinta da textura), expoente e intensidade do brilho |
| `uUsaTextura`, `uTextura` | liga a textura e indica a unidade 0 |
| `uSombraView`, `uSombraProj` | matrizes da câmera da sombra (a luz, projeção ortográfica) |
| `uSombraMapa`, `uSombraForca`, `uSombraBias`, `uRecebeSombra` | mapa de sombra (unidade 1), escurecimento, tolerância anti-acne e se a malha recebe sombra |

O **programa de sombra** (`VERTEX_SOMBRA` e `FRAGMENT_SOMBRA`) usa só `aPos`, `uModel`, `uView` e
`uProj`, e grava `gl_FragCoord.z` (a distância até a luz).

### Sombreamento × sombra projetada

- **Sombreamento** (shading): o escurecimento de uma superfície em função do ângulo entre a normal
  e a luz (`difusa = max(dot(N, L), 0)`). Depende só da própria superfície e da luz.
- **Sombra projetada** (shadow mapping): o escurecimento causado por *outro objeto* que bloqueia a luz.
  1. Passe de sombra: a cena é desenhada do ponto de vista da luz para uma textura de distâncias.
  2. Passe principal: para cada fragmento, calcula-se sua posição vista pela luz e compara-se a distância
     dele com a da textura. Se for maior, existe algo mais perto da luz e o fragmento está em sombra.
  3. A sombra só retira a luz direta; a luz ambiente continua.

## Mapeamento com o livro e adaptações

| Livro | Neste projeto |
|---|---|
| Cap. 3 — matrizes e transformações | `core/matrix.py` (convenção de vetor-coluna, como no livro) |
| Cap. 4 — `Object3D`, `Scene`, `Mesh`, `Camera`, `Renderer`, geometrias | `core/object3d.py`, `core/camera.py`, `core/renderer.py`, `geometry/` |
| Cap. 5 — `Texture`, coordenadas UV, uso em shaders | `core/texture.py`, UV em `geometry/shapes.py` |
| Cap. 6 — luz direcional, normais, material Phong | `core/shaders.py` (`FRAGMENT`) |
| Seção 6.9 — `Shadow`, `DepthMaterial`, `RenderTarget` | `core/shadow.py`, `VERTEX_SOMBRA`/`FRAGMENT_SOMBRA` |

Adaptações em relação ao livro (nomes em português e estrutura simplificada):

- Geometrias são funções (`caixa`, `cilindro`, `esfera`) em vez de classes `BoxGeometry` etc.
- O material é guardado na própria `Mesh` (cor, brilho, especular, textura), sem classes `Material`.
- A câmera é orbital (`CameraOrbital`), no lugar do `MovementRig`.
- No shadow mapping: textura de distâncias em formato float de 32 bits (R32F, mais preciso que o RGBA de
  8 bits) e média 3×3 das amostras (bordas suaves). Mantêm-se do livro: câmera ortográfica da luz,
  textura com `CLAMP_TO_BORDER` branca, condição "superfície voltada para a luz" (cosseno > 0,01),
  `strength` e `bias`.

## Contribuições individuais

> **PREENCHER antes da entrega.**

- [Integrante 1]: [descreva: modelagem, animação, shaders…]
- [Integrante 2]: [descreva: modelagem, animação, shaders…]

## Fontes consultadas

- STEMKOSKI, Lee; PASCALE, Michael. *Developing graphics frameworks with Python and OpenGL*.
  1. ed. Boca Raton: CRC Press, 2022. DOI: 10.1201/9781003181378. (estrutura do framework, matrizes,
  texturas, iluminação Phong e shadow mapping da seção 6.9, adaptados)
- Documentação do pygame, do PyOpenGL e da especificação OpenGL 3.3.

**Texturas** (`texturas/grama.png`, `asfalto.png`, `terra.png`): imagens de autoria própria, geradas
por `tools/gerar_texturas.py` (ruído filtrado com numpy, ladrilháveis). Não há imagens de terceiros.

## Declaração de uso de inteligência artificial

> **CONFERIR e completar antes da entrega.**

- **Ferramenta:** Claude (Anthropic).
- **Finalidade e trechos desenvolvidos ou revisados com apoio da ferramenta** (revisão do projeto contra
  os requisitos do trabalho e implementação das melhorias):
  - câmera pelo teclado (`CameraOrbital.teclado`);
  - coordenadas UV em `geometry/` e carregamento de texturas (`core/texture.py`);
  - shadow mapping (`core/shadow.py`, passes em `core/renderer.py`, shaders em `core/shaders.py`);
  - reação do caracol ao trator (`Caracol.atualizar`) e `Enum Fase` em `cena.py`;
  - geração das texturas (`tools/gerar_texturas.py`) e este README.
- [Informe aqui se a ferramenta também foi usada no restante do código original.]
- O código foi revisado pela dupla, que se responsabiliza por explicá-lo na apresentação.

## Estrutura

```
main.py            janela, laço principal, eventos
cena.py            ambiente + sequência da dupla (Fase, Cena)
core/              matrix, object3d (grafo de cena + Mesh), camera, renderer, shaders, shadow, texture, util
geometry/          Geometry (VBO/VAO) e formas (caixa, cilindro, esfera)
objetos/           trator.py e caracol.py (modelos e animações)
texturas/          imagens PNG usadas como textura
tools/             gerar_texturas.py (opcional)
docs/              roteiro da apresentação
```
