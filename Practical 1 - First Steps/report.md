# Practical 1 - First Steps

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