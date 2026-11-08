"""Shaders GLSL (OpenGL 3.3 core): iluminacao direcional + ambiente + brilho."""
from OpenGL.GL import GL_VERTEX_SHADER, GL_FRAGMENT_SHADER
from OpenGL.GL.shaders import compileProgram, compileShader

VERTEX = """
#version 330 core
layout(location = 0) in vec3 aPos;
layout(location = 1) in vec3 aNormal;
uniform mat4 uModel;
uniform mat4 uView;
uniform mat4 uProj;
out vec3 vNormal;
out vec3 vPos;
void main() {
    vec4 mundo = uModel * vec4(aPos, 1.0);
    vPos = mundo.xyz;
    vNormal = mat3(transpose(inverse(uModel))) * aNormal;
    gl_Position = uProj * uView * mundo;
}
"""

FRAGMENT = """
#version 330 core
in vec3 vNormal;
in vec3 vPos;
uniform vec3 uColor;
uniform vec3 uLightDir;
uniform vec3 uCamPos;
uniform float uShininess;
uniform float uSpecular;
out vec4 FragColor;
void main() {
    vec3 N = normalize(vNormal);
    vec3 L = normalize(uLightDir);
    vec3 V = normalize(uCamPos - vPos);
    vec3 H = normalize(L + V);
    float difusa = max(dot(N, L), 0.0);
    float hemi = 0.5 + 0.5 * N.y;
    vec3 ambiente = mix(vec3(0.22, 0.20, 0.18), vec3(0.42, 0.46, 0.55), hemi);
    float brilho = pow(max(dot(N, H), 0.0), uShininess) * uSpecular * step(0.001, difusa);
    vec3 cor = uColor * (ambiente + difusa * vec3(1.0, 0.96, 0.88) * 0.85) + vec3(brilho);
    FragColor = vec4(cor, 1.0);
}
"""


def criar_programa():
    return compileProgram(
        compileShader(VERTEX, GL_VERTEX_SHADER),
        compileShader(FRAGMENT, GL_FRAGMENT_SHADER),
        validate=False,
    )
