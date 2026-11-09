"""Shaders GLSL (OpenGL 3.3 core).

Programa principal: iluminacao direcional (difusa + especular de Blinn-Phong) + luz
ambiente hemisferica + textura de imagem + sombra por shadow mapping (secao 6.9).
Programa de sombra: so grava a distancia ate a luz (DepthMaterial do livro)."""
from OpenGL.GL import GL_VERTEX_SHADER, GL_FRAGMENT_SHADER
from OpenGL.GL.shaders import compileProgram, compileShader

VERTEX = """
#version 330 core
layout(location = 0) in vec3 aPos;
layout(location = 1) in vec3 aNormal;
layout(location = 2) in vec2 aUV;
uniform mat4 uModel;
uniform mat4 uView;
uniform mat4 uProj;
uniform mat4 uSombraView;     // camera da sombra (a luz)
uniform mat4 uSombraProj;
out vec3 vNormal;
out vec3 vPos;
out vec2 vUV;
out vec3 vSombraPos;
void main() {
    vec4 mundo = uModel * vec4(aPos, 1.0);
    vPos = mundo.xyz;
    vNormal = mat3(transpose(inverse(uModel))) * aNormal;
    vUV = aUV;
    // posicao do vertice vista pela luz (clip space): o fragment shader usa para ler o mapa de sombra
    vSombraPos = (uSombraProj * uSombraView * mundo).xyz;
    gl_Position = uProj * uView * mundo;
}
"""

FRAGMENT = """
#version 330 core
in vec3 vNormal;
in vec3 vPos;
in vec2 vUV;
in vec3 vSombraPos;
uniform vec3 uColor;
uniform vec3 uLightDir;       // aponta da superficie PARA a luz
uniform vec3 uCamPos;
uniform float uShininess;
uniform float uSpecular;
uniform int uUsaTextura;
uniform sampler2D uTextura;   // unidade 0
uniform int uRecebeSombra;
uniform sampler2D uSombraMapa; // unidade 1
uniform float uSombraForca;
uniform float uSombraBias;
out vec4 FragColor;

// 0 = totalmente iluminado, 1 = totalmente em sombra (media 3x3 -> bordas suaves)
float calcularSombra(vec3 N, vec3 L) {
    float cosAngulo = dot(N, L);
    if (uRecebeSombra == 0 || cosAngulo <= 0.01) return 0.0;   // face de costas para a luz: so sombreamento
    vec3 coord = (vSombraPos + 1.0) * 0.5;                      // [-1,1] -> [0,1] (uv e profundidade)
    if (coord.x < 0.0 || coord.x > 1.0 || coord.y < 0.0 || coord.y > 1.0) return 0.0;
    float atual = clamp(coord.z, 0.0, 1.0);                     // distancia deste fragmento a luz
    float bias = uSombraBias * (1.0 + 3.0 * (1.0 - cosAngulo)); // superficies rasantes pedem bias maior
    vec2 texel = 1.0 / vec2(textureSize(uSombraMapa, 0));
    float emSombra = 0.0;
    for (int x = -1; x <= 1; x++) {
        for (int y = -1; y <= 1; y++) {
            float maisPerto = texture(uSombraMapa, coord.xy + vec2(x, y) * texel).r;
            emSombra += (atual > maisPerto + bias) ? 1.0 : 0.0;
        }
    }
    return emSombra / 9.0;
}

void main() {
    vec3 N = normalize(vNormal);
    vec3 L = normalize(uLightDir);
    vec3 V = normalize(uCamPos - vPos);
    vec3 H = normalize(L + V);
    vec3 albedo = uColor;
    if (uUsaTextura == 1) albedo *= texture(uTextura, vUV).rgb;

    float difusa = max(dot(N, L), 0.0);
    float hemi = 0.5 + 0.5 * N.y;
    vec3 ambiente = mix(vec3(0.22, 0.20, 0.18), vec3(0.42, 0.46, 0.55), hemi);
    float brilho = pow(max(dot(N, H), 0.0), uShininess) * uSpecular * step(0.001, difusa);

    float sombra = calcularSombra(N, L) * uSombraForca;
    float luzDireta = 1.0 - sombra;          // a sombra so tira a luz direta; o ambiente permanece
    vec3 cor = albedo * (ambiente + luzDireta * difusa * vec3(1.0, 0.96, 0.88) * 0.85)
             + vec3(brilho) * luzDireta;
    FragColor = vec4(cor, 1.0);
}
"""

VERTEX_SOMBRA = """
#version 330 core
layout(location = 0) in vec3 aPos;
uniform mat4 uModel;
uniform mat4 uView;     // camera da sombra
uniform mat4 uProj;
void main() {
    gl_Position = uProj * uView * uModel * vec4(aPos, 1.0);
}
"""

FRAGMENT_SOMBRA = """
#version 330 core
out vec4 FragColor;
void main() {
    float z = gl_FragCoord.z;      // distancia (0..1) deste ponto ate a luz
    FragColor = vec4(z, z, z, 1.0);
}
"""


def _programa(vertex, fragment):
    return compileProgram(
        compileShader(vertex, GL_VERTEX_SHADER),
        compileShader(fragment, GL_FRAGMENT_SHADER),
        validate=False,
    )


def criar_programa():
    return _programa(VERTEX, FRAGMENT)


def criar_programa_sombra():
    return _programa(VERTEX_SOMBRA, FRAGMENT_SOMBRA)
