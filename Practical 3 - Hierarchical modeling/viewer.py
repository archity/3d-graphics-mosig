#!/usr/bin/env python3
"""
Python OpenGL practical application.
"""

import sys                          # for system arguments

# External, non built-in modules
import OpenGL.GL as GL              # standard Python OpenGL wrapper
import glfw                         # lean window system wrapper for OpenGL
import numpy as np                  # all matrix manipulations & OpenGL args
import assimpcy                     # 3D resource loader

from core import Shader, Mesh, Node, Viewer
from transform import translate, rotate, scale


class Axis(Mesh):
    """ Axis object useful for debugging coordinate frames """
    def __init__(self, shader):
        pos = ((0, 0, 0), (1, 0, 0), (0, 0, 0), (0, 1, 0), (0, 0, 0), (0, 0, 1))
        col = ((1, 0, 0), (1, 0, 0), (0, 1, 0), (0, 1, 0), (0, 0, 1), (0, 0, 1))
        super().__init__(shader, [pos, col])

    def draw(self, projection, view, model, primitives=GL.GL_LINES):
        super().draw(projection, view, model, primitives)


class SimpleTriangle(Mesh):
    """Hello triangle object"""

    def __init__(self, shader):

        # triangle position buffer
        position = np.array(((0, .5, 0), (.5, -.5, 0), (-.5, -.5, 0)), 'f')
        color = np.array(((1, 0, 0), (0, 1, 0), (0, 0, 1)), 'f')

        super().__init__(shader, [position, color])


class Cylinder(Node):
    """ Very simple cylinder based on practical 2 load function """
    def __init__(self, shader):
        super().__init__()
        self.add(*load('cylinder.obj', shader))  # just load cylinder from file


# -------------- 3D resource loader -----------------------------------------
def load(file, shader):
    """ load resources from file using assimpcy, return list of ColorMesh """
    try:
        pp = assimpcy.aiPostProcessSteps
        flags = pp.aiProcess_Triangulate | pp.aiProcess_GenSmoothNormals
        scene = assimpcy.aiImportFile(file, flags)
    except assimpcy.all.AssimpError as exception:
        print('ERROR loading', file + ': ', exception.args[0].decode())
        return []

    meshes = [Mesh(shader, [m.mVertices, m.mNormals], m.mFaces)
              for m in scene.mMeshes]
    size = sum((mesh.mNumFaces for mesh in scene.mMeshes))
    print('Loaded %s\t(%d meshes, %d faces)' % (file, len(meshes), size))
    return meshes


# -------------- main program and scene setup --------------------------------
def main():
    """ create a window, add scene objects, then run rendering loop """
    viewer = Viewer()

    # default color shader
    shader = Shader("color.vert", "color.frag")

    axis = Axis(shader)

    # construct our robot arm hierarchy for drawing in viewer
    cylinder = Cylinder(shader)
    
    # ---- let's make our shapes ---------------------------------------
    base_shape = Node(transform=scale(x=0.5, y=0.1, z=0.5))
    base_shape.add(cylinder)

    arm_shape = Node(transform=translate(y=0.8) @ scale(x=0.1, y=0.8, z=0.1))
    arm_shape.add(cylinder)

    forearm_shape = Node(transform=translate(y=0.5, z=0.4) @ scale(x=0.05, y=0.4, z=0.05))
    forearm_shape.add(cylinder)

    # ---- construct our robot arm hierarchy ---------------------------
    theta = 45.0        # base horizontal rotation angle
    phi1 = 25.0         # arm angle
    phi2 = 120.0        # forearm angle

    # Forearm
    transform_forearm = Node(transform = translate(y=2, z=0.15) @ rotate((1, 0, 0), phi2))
    transform_forearm.add(forearm_shape)

    # Arm
    transform_arm = Node(transform = rotate((1, 0, 0), phi1))
    transform_arm.add(arm_shape, transform_forearm)

    # Base
    transform_base = Node(transform = rotate((0, 1, 0), theta))
    transform_base.add(base_shape, transform_arm)

    # transform_arm.add(axis)
    # transform_forearm.add(axis)
    # transform_base.add(axis)

    # viewer.add(transform_forearm)
    # viewer.add(transform_arm)
    viewer.add(transform_base)


    # start rendering loop
    viewer.run()


if __name__ == '__main__':
    glfw.init()                # initialize window system glfw
    main()                     # main function keeps variables locally scoped
    glfw.terminate()           # destroy all glfw windows and GL contexts
