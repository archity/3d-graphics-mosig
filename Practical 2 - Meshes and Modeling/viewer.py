#!/usr/bin/env python3
"""
Python OpenGL practical application.
"""
# Python built-in modules
import os                           # os function, i.e. checking file status

# External, non built-in modules
import OpenGL.GL as GL              # standard Python OpenGL wrapper
import glfw                         # lean window system wrapper for OpenGL
import numpy as np                  # all matrix manipulations & OpenGL args
import sys                          # for sys.exit

from itertools import cycle         # cyclic iterator to easily toggle polygon rendering modes

# ------------ low level OpenGL object wrappers ----------------------------
class Shader:
    """ Helper class to create and automatically destroy shader program """
    @staticmethod
    def _compile_shader(src, shader_type):
        src = open(src, 'r').read() if os.path.exists(src) else src
        src = src.decode('ascii') if isinstance(src, bytes) else src
        shader = GL.glCreateShader(shader_type)
        GL.glShaderSource(shader, src)
        GL.glCompileShader(shader)
        status = GL.glGetShaderiv(shader, GL.GL_COMPILE_STATUS)
        src = ('%3d: %s' % (i+1, l) for i, l in enumerate(src.splitlines()))
        if not status:
            log = GL.glGetShaderInfoLog(shader).decode('ascii')
            GL.glDeleteShader(shader)
            src = '\n'.join(src)
            print('Compile failed for %s\n%s\n%s' % (shader_type, log, src))
            sys.exit(1)
        return shader

    def __init__(self, vertex_source, fragment_source):
        """ Shader can be initialized with raw strings or source file names """
        self.glid = None
        vert = self._compile_shader(vertex_source, GL.GL_VERTEX_SHADER)
        frag = self._compile_shader(fragment_source, GL.GL_FRAGMENT_SHADER)
        if vert and frag:
            self.glid = GL.glCreateProgram()  # pylint: disable=E1111
            GL.glAttachShader(self.glid, vert)
            GL.glAttachShader(self.glid, frag)
            GL.glLinkProgram(self.glid)
            GL.glDeleteShader(vert)
            GL.glDeleteShader(frag)
            status = GL.glGetProgramiv(self.glid, GL.GL_LINK_STATUS)
            if not status:
                print(GL.glGetProgramInfoLog(self.glid).decode('ascii'))
                GL.glDeleteProgram(self.glid)
                sys.exit(1)

    def __del__(self):
        GL.glUseProgram(0)
        if self.glid:                      # if this is a valid shader object
            GL.glDeleteProgram(self.glid)  # object dies => destroy GL object


# ------------ OpenGL vertex array wrapper for Exercise 2 ---------------------
class VertexArray:
    """ helper class to create and self destroy OpenGL vertex array objects."""
    def __init__(self, attributes, index=None, usage=GL.GL_STATIC_DRAW):
        """ Vertex array from attributes and optional index array. Vertex
            Attributes should be list of arrays with one row per vertex. """

        # create vertex array object, bind it
        self.glid = GL.glGenVertexArrays(1)
        GL.glBindVertexArray(self.glid)
        self.buffers = []  # we will store buffers in a list
        nb_primitives, size = 0, 0

        # load buffer per vertex attribute (in list with index = shader layout)
        for loc, data in enumerate(attributes):
            if data is not None:
                # bind a new vbo, upload its data to GPU, declare size and type
                self.buffers.append(GL.glGenBuffers(1))
                data = np.array(data, np.float32, copy=False)  # ensure format
                nb_primitives, size = data.shape
                GL.glEnableVertexAttribArray(loc)
                GL.glBindBuffer(GL.GL_ARRAY_BUFFER, self.buffers[-1])
                GL.glBufferData(GL.GL_ARRAY_BUFFER, data, usage)
                GL.glVertexAttribPointer(loc, size, GL.GL_FLOAT, False, 0, None)

        # optionally create and upload an index buffer for this object
        self.draw_command = GL.glDrawArrays
        self.arguments = (0, nb_primitives)
        if index is not None:
            self.buffers += [GL.glGenBuffers(1)]
            index_buffer = np.array(index, np.int32, copy=False)  # good format
            GL.glBindBuffer(GL.GL_ELEMENT_ARRAY_BUFFER, self.buffers[-1])
            GL.glBufferData(GL.GL_ELEMENT_ARRAY_BUFFER, index_buffer, usage)
            self.draw_command = GL.glDrawElements
            self.arguments = (index_buffer.size, GL.GL_UNSIGNED_INT, None)

    def execute(self, primitive):
        """ draw a vertex array, either as direct array or indexed array """
        GL.glBindVertexArray(self.glid)
        self.draw_command(primitive, *self.arguments)

    def __del__(self):  # object dies => kill GL array and buffers from GPU
        GL.glDeleteVertexArrays(1, [self.glid])
        GL.glDeleteBuffers(len(self.buffers), self.buffers)

# ------------  Scene object classes ------------------------------------------
class Pyramid:
    """ Exercise 1 and 2: Pyramid object """

    def __init__(self, shader):
        self.shader = shader
    
        # Interpolated colourful rendering
        # position = np.array(((-.5, 0, -.5), (-.5, 0, .5), (.5, 0, .5), (.5, 0, -.5), (0, 1, 0)), 'f')
        # color = np.array(((1, 1, 0), (0, 1, 0), (0, 0, 1), (1, 0, 1), (1, 0, 0)), 'f')
        # self.index = np.array((4,1,2, 4,2,3, 4,3,0, 4,0,1, 1,3,2, 1,0,3 ), np.uint32)

        # Flat colours rendering
        position = np.array(((-.5, 0, -.5), (-.5, 0, .5), (.5, 0, .5), (.5, 0, -.5), (0, 1, 0),
        (-.5, 0, -.5), (-.5, 0, .5), (.5, 0, .5), (.5, 0, -.5), (0, 1, 0),
        (-.5, 0, -.5), (-.5, 0, .5), (.5, 0, .5), (.5, 0, -.5), (0, 1, 0),
        (0, 1, 0), (-.5, 0, .5), (.5, 0, -.5)), 'f')

        color = np.array(((0, 0, 1), (1, 0, 0), (1, 0, 0), (0, 1, 0), (1, 0, 0),
        (0, 1, 1), (0, 1, 1), (0, 1, 0), (0, 0, 1), (0, 1, 0),
        (1, 1, 0), (1, 1, 0), (1, 1, 0), (1, 1, 0), (0, 0, 1),
        (0, 1, 1), (1, 1, 0), (1, 1, 0)), 'f')

        self.index = np.array((4,1,2, 9,7,3, 14,8,0, 15,5,6, 11,13,12, 16,10,17), np.uint32)

        self.array = VertexArray([position, color], self.index)

        

    def draw(self, projection, view, model):
        GL.glUseProgram(self.shader.glid)

        loc = GL.glGetUniformLocation(self.shader.glid, 'view')
        GL.glUniformMatrix4fv(loc, 1, True, view)

        loc = GL.glGetUniformLocation(self.shader.glid, 'projection')
        GL.glUniformMatrix4fv(loc, 1, True, projection)

        self.array.execute(GL.GL_TRIANGLES)

    def __del__(self):
        GL.glDeleteVertexArrays(1, [self.glid])
        GL.glDeleteBuffers(2, self.buffers)

    # Call mesh.draw here


# ------------ Exercise 3: Implement this generic mesh class ------------------
class Mesh:
    """ Generic mesh class with attributes passed as constructor arguments.
        Most mesh classes can then derive from this base implementation """
    def __init__(self, shader, attributes, index=None):
        self.shader = shader
        # TODO pass on these buffers to a VertexArray Object

    def draw(self, projection, view, model, primitives=GL.GL_TRIANGLES):
        GL.glUseProgram(self.shader.glid)
        # TODO: instantiate uniform matrices that are need in all drawables
        # TODO: draw th Mesh by executing the VertexArray


# ------------  Viewer class & window management ------------------------------
from transform import Trackball

class Viewer:
    """ GLFW viewer window, with classic initialization & graphics loop """

    def __init__(self, width=1280, height=720):

        # version hints: create GL window with >= OpenGL 3.3 and core profile
        glfw.window_hint(glfw.CONTEXT_VERSION_MAJOR, 3)
        glfw.window_hint(glfw.CONTEXT_VERSION_MINOR, 3)
        glfw.window_hint(glfw.OPENGL_FORWARD_COMPAT, GL.GL_TRUE)
        glfw.window_hint(glfw.OPENGL_PROFILE, glfw.OPENGL_CORE_PROFILE)
        glfw.window_hint(glfw.RESIZABLE, False)
        self.win = glfw.create_window(width, height, 'Viewer', None, None)

        # make win's OpenGL context current; no OpenGL calls can happen before
        glfw.make_context_current(self.win)

        # initialize trackball
        self.trackball = Trackball()
        self.mouse = (0, 0)

        # register event handlers
        glfw.set_key_callback(self.win, self.on_key)
        glfw.set_cursor_pos_callback(self.win, self.on_mouse_move)
        glfw.set_scroll_callback(self.win, self.on_scroll)

        # useful message to check OpenGL renderer characteristics
        print('OpenGL', GL.glGetString(GL.GL_VERSION).decode() + ', GLSL',
              GL.glGetString(GL.GL_SHADING_LANGUAGE_VERSION).decode() +
              ', Renderer', GL.glGetString(GL.GL_RENDERER).decode())

        # initialize GL by setting viewport and default render characteristics
        GL.glClearColor(0.1, 0.1, 0.1, 0.1)
        GL.glEnable(GL.GL_CULL_FACE)   # enable backface culling (Exercise 1)
        GL.glEnable(GL.GL_DEPTH_TEST)  # enable depth test (Exercise 1)

        # initially empty list of object to draw
        self.drawables = []

        self.fill_modes = cycle([GL.GL_LINE, GL.GL_POINT, GL.GL_FILL])


    def run(self):
        """ Main render loop for this OpenGL window """
        while not glfw.window_should_close(self.win):
            # clear draw buffer, but also need to clear Z-buffer! (Exercise 1)
            # GL.glClear(GL.GL_COLOR_BUFFER_BIT)  # comment this, uncomment next
            GL.glClear(GL.GL_COLOR_BUFFER_BIT | GL.GL_DEPTH_BUFFER_BIT)

            win_size = glfw.get_window_size(self.win)
            view = self.trackball.view_matrix()
            projection = self.trackball.projection_matrix(win_size)

            # draw our scene objects
            for drawable in self.drawables:
                drawable.draw(projection, view, None)

            # flush render commands, and swap draw buffers
            glfw.swap_buffers(self.win)

            # Poll for and process events
            glfw.poll_events()

    def add(self, *drawables):
        """ add objects to draw in this window """
        self.drawables.extend(drawables)

    def on_key(self, _win, key, _scancode, action, _mods):
        """ 'Q' or 'Escape' quits """
        if action == glfw.PRESS or action == glfw.REPEAT:
            if key == glfw.KEY_ESCAPE or key == glfw.KEY_Q:
                glfw.set_window_should_close(self.win, True)

            # Toggle wireframe mode
            if key == glfw.KEY_W:
                GL.glPolygonMode(GL.GL_FRONT_AND_BACK, next(self.fill_modes))

            for drawable in self.drawables:
                if hasattr(drawable, 'key_handler'):
                    drawable.key_handler(key)

    def on_mouse_move(self, win, xpos, ypos):
        """ Rotate on left-click & drag, pan on right-click & drag """
        old = self.mouse
        self.mouse = (xpos, glfw.get_window_size(win)[1] - ypos)
        if glfw.get_mouse_button(win, glfw.MOUSE_BUTTON_LEFT):
            self.trackball.drag(old, self.mouse, glfw.get_window_size(win))
        if glfw.get_mouse_button(win, glfw.MOUSE_BUTTON_RIGHT):
            self.trackball.pan(old, self.mouse)

    def on_scroll(self, win, _deltax, deltay):
        """ Scroll controls the camera distance to trackball center """
        self.trackball.zoom(deltay, glfw.get_window_size(win)[1])


# -------------- main program and scene setup --------------------------------
def main():
    """ create window, add shaders & scene objects, then run rendering loop """
    viewer = Viewer()
    color_shader = Shader("color.vert", "color.frag")

    # place instances of our basic objects
    viewer.add(Pyramid(color_shader))

    # start rendering loop
    viewer.run()


if __name__ == '__main__':
    glfw.init()                # initialize window system glfw
    main()                     # main function keeps variables locally scoped
    glfw.terminate()           # destroy all glfw windows and GL contexts
