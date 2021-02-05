#version 330 core

layout(location = 0) in vec3 position;
layout(location = 1) in vec3 col_cpu;

out vec3 col;
uniform mat4 matrix;

void main() {
    col = col_cpu;
    gl_Position = matrix * vec4(position, 1);
}
