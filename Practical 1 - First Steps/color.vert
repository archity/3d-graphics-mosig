#version 330 core

layout(location = 0) in vec3 position;
layout(location = 1) in vec3 col_cpu;

out vec3 col;
uniform mat4 matrix;

uniform mat4 projection_matrix;
uniform mat4 view_matrix;

void main() {
    col = col_cpu;
    gl_Position = projection_matrix * view_matrix * matrix * vec4(position, 1);
}
