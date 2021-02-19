# Practical 1 - First Steps

## Simple Triangle

In the SimpleTriangle class, we define the 3 coordinates as well as the colour associated with each vertex:

```py
# triangle position buffer
position = np.array(((0, .5, 0), (.5, -.5, 0), (-.5, -.5, 0)), 'f')

# Triangle colour buffer, each for R, G, B
color = np.array(((1, 0, 0), (0, 1, 0), (0, 0, 1)), 'f')
```
We create 2 buffers memory area, fill them with our created arrays `position` and `color`, and upload them to the GPU using the below snippet:

```py
self.glid = GL.glGenVertexArrays(1)  # create OpenGL vertex array id
GL.glBindVertexArray(self.glid)      # activate to receive state below
self.buffers = GL.glGenBuffers(2)    # create 2 buffers for position & colour attrib

# bind the vbo, upload position data to GPU, declare its size and type
GL.glEnableVertexAttribArray(0)
GL.glBindBuffer(GL.GL_ARRAY_BUFFER, self.buffers[0])
GL.glBufferData(GL.GL_ARRAY_BUFFER, position, GL.GL_STATIC_DRAW)
GL.glVertexAttribPointer(0, 3, GL.GL_FLOAT, False, 0, None)

GL.glEnableVertexAttribArray(1)
GL.glBindBuffer(GL.GL_ARRAY_BUFFER, self.buffers[1])
GL.glBufferData(GL.GL_ARRAY_BUFFER, color, GL.GL_STATIC_DRAW)
GL.glVertexAttribPointer(1, 3, GL.GL_FLOAT, False, 0, None)

# cleanup and unbind so no accidental subsequent state update
GL.glBindVertexArray(0)
GL.glBindBuffer(GL.GL_ARRAY_BUFFER, 0)
```
The GPU part is what is called the shader part. In the vertex shader file (`color.vert`), we receive these 2 arrays-

```glsl
layout(location = 0) in vec3 position;
layout(location = 1) in vec3 col_cpu;
```

-and make use of them in the main function:

```glsl
void main()
{
    col = col_cpu;
    gl_Position = matrix * vec4(position, 1);
}
```
## Trackball

As taken from [this](http://morpheo.inrialpes.fr/~franco/3dgraphics/recipes.html#virtual-trackball) link, we add a new class `GLFWTrackball` which handles mouse specifics.

In the `Viewer` class, we declare an object of this GLFWTrackball, from which we (continuously in `run()`) extract the `view` and `projection` matrices. Both these matrices are sent to `SimpleTriangle` class through the `draw()` function.

Now there are 2 ways in which the product of these matrices can be calculated. 

* CPU side - the matrix multiplication happens in the SimpleTriangle's draw function, and then the result is sent to the vertex shader `color.vert`.

* GPU side - we send both the matrices to the vertex shader, and then do the multiplication, which is what we did in our case:

```glsl
gl_Position = projection_matrix * view_matrix * matrix * vec4(position, 1);
```

where `projection_matrix`, `view_matrix` are the 2 tracking matrices, and `matrix` matrix has info about rotation and/or translation, as done previously. The order of multiplication is indeed important, and this order was established through a bit of hit and trial.