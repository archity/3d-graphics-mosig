#version 330 core

layout(location = 0) in vec3 position;
layout(location = 1) in vec3 col_cpu;

out vec3 col;

void main() {
    col = col_cpu;
    gl_Position = vec4(position, 1);
}
