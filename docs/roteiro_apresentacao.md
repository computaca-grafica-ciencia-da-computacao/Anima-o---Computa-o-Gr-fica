# Roteiro da apresentação (10 min, dupla)

Capturas de tela para os slides em `docs/capturas/`. Preencher [colchetes] com os nomes da dupla.

| # | Slide | Tempo | Quem | Conteúdo |
|---|---|---|---|---|
| 1 | Capa | 0:15 | A | "Trator x Caracol Robótico", Computação Gráfica, integrantes e temas (14 e 30), UNIPAC 2026/02 |
| 2 | Cena e interação | 1:00 | A | 4 passos: trator avança e freia; caracol percebe o trator e hesita; caracol atravessa; trator retoma. Frase-chave: nos dois sentidos, não são movimentos independentes (`Cena.atualizar`: `bloqueado`; `Caracol.atualizar`: `trator_x`, `trator_vel`) |
| — | **Demo ao vivo** | 1:00 | B | Rodar; orbitar com setas e mouse; zoom com W/S; **P** pausa (a câmera continua livre); **R** reinicia; mostrar a sombra do trator e do caracol se movendo |
| 3 | Arquitetura | 1:00 | B | `main → Cena → Trator/Caracol → Mesh → Renderer`. Tabela livro → projeto (README). Fonte: Stemkoski e Pascale (2022) |
| 4 | Modelagem e hierarquia | 1:00 | A | Trator = caixas + cilindros; rodas filhas do trator; antenas filhas da cabeça do caracol. `matriz_mundo = pai @ local`; escala do caracol (1,8) propaga para as partes |
| 5 | Animação por tempo | 1:00 | A | `dt` em segundos com limite de 0,05 s; rolamento sem deslizar (`ângulo = distância / raio`); frenagem proporcional (`K_FREIO`); pausa só suspende `cena.atualizar` |
| 6 | Shaders, atributos e uniforms | 1:30 | B | Vertex: `aPos`, `aNormal`, `aUV`; uniforms `uModel`, `uView`, `uProj`, `uSombraView`, `uSombraProj`. Fragment: `uColor`, `uLightDir`, `uCamPos`, `uShininess`, `uSpecular`, `uTextura`, `uSombraMapa`… Ligar cada uniform à transformação que ele representa |
| 7 | Luz, normais e textura | 1:00 | B | Normal transformada por `transpose(inverse(uModel))`; Blinn-Phong (ambiente + difusa + especular); textura com UV ladrilhado (`uv_por_unidade`), filtro mipmap + anisotrópico |
| 8 | Sombras (shadow mapping) | 1:30 | A | Passe 1: cena vista pela luz → textura de distâncias (2048²). Passe 2: cada fragmento calcula sua posição na luz e compara a distância. `bias` evita acne; média 3×3 suaviza. **Sombreamento ≠ sombra** (veja o README) |
| 9 | Contribuições, IA e fontes | 0:45 | A + B | Quem fez o quê; declaração de IA; fontes; texturas de autoria própria |

## Perguntas individuais prováveis

- **Sombreamento × sombra projetada?** Sombreamento depende da normal e da luz (`difusa`); sombra depende de outro objeto bloquear a luz (mapa de sombra).
- **Atributo × uniform?** Atributo muda por vértice (`aPos`, `aNormal`, `aUV`); uniform é igual para todos os vértices/fragmentos de uma chamada de desenho (`uModel`, `uLightDir`).
- **Por que a velocidade não depende do FPS?** Todo deslocamento é `velocidade * dt`, com `dt` medido por `Clock.tick`.
- **Como a roda gira junto com o trator?** A roda é filha do trator: `matriz_mundo = trator @ roda`; a rotação da roda usa `-v*dt/raio`.
- **Para que serve o `bias`?** Evita que a superfície se sombreie a si mesma por imprecisão numérica (shadow acne).
- **Por que o chão está fora do passe de sombra?** Superfícies planas só recebem sombra (`projeta_sombra=False`), o que evita acne e economiza desenho.
- **Onde a pausa é tratada e por que o render continua?** Em `main.py`: `if not pausado: cena.atualizar(dt)`; o `renderizar` e `camera.teclado` rodam sempre.
