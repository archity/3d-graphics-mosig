#version 330 core

// fragment position and normal of the fragment, in WORLD coordinates
// (you can also compute in VIEW coordinates, your choice! rename variables)
in vec3 w_position, w_normal;   // in world coodinates

// light dir, in world coordinates
uniform vec3 light_dir;

// material properties
uniform vec3 k_d;
uniform vec3 k_a;
uniform vec3 k_s;
// uniform vec3 r;
// uniform vec3 s;

// world camera position
uniform vec3 w_camera_position;

out vec4 out_color;

void main() {
    
    vec3 n = normalize(w_normal);
    vec3 l = normalize(-light_dir);
    vec3 r = normalize(reflect(light_dir, n));
    vec3 v = normalize(w_camera_position);
    float s = 10;

    // The Lambertian model
    // out_color = vec4(k_d * max(0, dot(n, l)), 1);

    // The Phong model
    out_color = vec4(k_a + k_d * max(0, dot(n, l)) + k_s * max(0, pow(dot(r, v), s)), 1);
}
