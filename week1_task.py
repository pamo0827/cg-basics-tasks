import sys
import random
from OpenGL.GLUT import *
from OpenGL.GL import *
from OpenGL.GLU import *

def draw_triangle(vertices, color):
    glColor3f(color[0], color[1], color[2])
    glBegin(GL_TRIANGLES)
    for vertex in vertices:
        glVertex2f(vertex[0], vertex[1])
    glEnd()

def get_midpoint(p1, p2):
    return ((p1[0] + p2[0]) / 2, (p1[1] + p2[1]) / 2)

def sierpinski(vertices, level):
    if level == 0:
        color = (random.random(), random.random(), random.random())
        draw_triangle(vertices, color)
    else:
        p0, p1, p2 = vertices
        p01 = get_midpoint(p0, p1)
        p12 = get_midpoint(p1, p2)
        p20 = get_midpoint(p2, p0)

        sierpinski((p0, p01, p20), level - 1)
        sierpinski((p01, p1, p12), level - 1)
        sierpinski((p20, p12, p2), level - 1)

def display():
    glClearColor(0.1, 0.1, 0.1, 1.0)
    glClear(GL_COLOR_BUFFER_BIT)

    initial_vertices = ((-0.9, -0.9), (0.9, -0.9), (0.0, 0.7))
    recursion_level = 5
    sierpinski(initial_vertices, recursion_level)

    glFlush()

if __name__ == "__main__":
    glutInit(sys.argv)
    glutInitWindowSize(600, 600)
    glutCreateWindow("Sierpinski Triangle")
    glutDisplayFunc(display)
    glMatrixMode(GL_PROJECTION)
    glLoadIdentity()
    gluOrtho2D(-1.0, 1.0, -1.0, 1.0)
    glMatrixMode(GL_MODELVIEW)
    glutMainLoop()