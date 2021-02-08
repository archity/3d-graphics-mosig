#version 330 core

out vec4 outColor;
uniform vec3 color;
in vec3 col;

void main() {
    outColor = vec4(col, 1);
}
