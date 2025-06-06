
import random
from random import *

from OpenGL.GL import *
from OpenGL.GLU import *

import math
from math import *

import numpy


class Point:
    def __init__(self, x, y, z):
        self.x = x
        self.y = y
        self.z = z

    def __add__(self, other):
        return Point(self.x + other.x, self.y + other.y, self.z + other.z)

    def __sub__(self, other):
        return Vector(self.x - other.x, self.y - other.y, self.z - other.z)

    def __str__(self):
        return f"x: {self.x}, y: {self.y}, z: {self.z}"
        
    def __mul__(self, other):
        return Point(self.x * other, self.y * other, self.z * other)

# Base line, used to draw other objects
class Line:
    def __init__(self, point_1, point_2):
        self.point_1 = point_1
        self.point_2 = point_2

class Vector:
    def __init__(self, x, y, z):
        self.x = x
        self.y = y
        self.z = z
    
    def __add__(self, other):
        return Vector(self.x + other.x, self.y + other.y, self.z + other.z)

    def __sub__(self, other):
        return Vector(self.x - other.x, self.y - other.y, self.z - other.z)

    def __mul__(self, scalar):
        return Vector(self.x * scalar, self.y * scalar, self.z * scalar)
    
    def __len__(self):
        return sqrt(self.x * self.x + self.y * self.y + self.z * self.z)
    
    def normalize(self):
        length = self.__len__()
        self.x /= length
        self.y /= length
        self.z /= length
    
    def length(self):
        return self.__len__()

    def dot(self, other):
        return self.x * other.x + self.y * other.y + self.z * other.z

    def cross(self, other):
        return Vector(self.y*other.z - self.z*other.y, self.z*other.x - self.x*other.z, self.x*other.y - self.y*other.x)

class Color:
    def __init__(self, r, g, b):
        self.r = r
        self.g = g
        self.b = b

class Material:
    def __init__(self, diffuse = None, specular = None, shininess = None, tex_diffuse = None, tex_specular = None):
        self.diffuse = Color(0.0, 0.0, 0.0) if diffuse == None else diffuse
        self.specular = Color(0.0, 0.0, 0.0) if specular == None else specular
        self.shininess = 1 if shininess == None else shininess
        self.tex_diffuse = tex_diffuse
        self.tex_specular = tex_specular


class MeshModel:
    def __init__(self):
        self.vertex_arrays = dict()
        # self.index_arrays = dict()
        self.mesh_materials = dict()
        self.materials = dict()
        self.vertex_counts = dict()
        self.vertex_buffer_ids = dict()

    def add_vertex(self, mesh_id, position, normal, uv):
        if mesh_id not in self.vertex_arrays:
            self.vertex_arrays[mesh_id] = []
            self.vertex_counts[mesh_id] = 0
        self.vertex_arrays[mesh_id] += [position.x, position.y, position.z, normal.x, normal.y, normal.z, uv.x, uv.y]
        self.vertex_counts[mesh_id] += 1

    def set_mesh_material(self, mesh_id, mat_id):
        self.mesh_materials[mesh_id] = mat_id

    def add_material(self, mat_id, mat):
        self.materials[mat_id] = mat
    
    def set_opengl_buffers(self):
        for mesh_id in self.mesh_materials.keys():
            self.vertex_buffer_ids[mesh_id] = glGenBuffers(1)
            glBindBuffer(GL_ARRAY_BUFFER, self.vertex_buffer_ids[mesh_id])
            glBufferData(GL_ARRAY_BUFFER, numpy.array(self.vertex_arrays[mesh_id], dtype='float32'), GL_STATIC_DRAW)
            glBindBuffer(GL_ARRAY_BUFFER, 0)

    def scale(self, factor):
        for mesh_id in self.vertex_arrays.keys():
            scaled_vertex_array = []
            for i in range(0, len(self.vertex_arrays[mesh_id]), 8):
                position = Point(self.vertex_arrays[mesh_id][i], self.vertex_arrays[mesh_id][i+1], self.vertex_arrays[mesh_id][i+2])
                scaled_position = position * factor
                normal = Vector(self.vertex_arrays[mesh_id][i+3], self.vertex_arrays[mesh_id][i+4], self.vertex_arrays[mesh_id][i+5])
                uv = Point(self.vertex_arrays[mesh_id][i+6], self.vertex_arrays[mesh_id][i+7], 0)
                scaled_vertex_array += [scaled_position.x, scaled_position.y, scaled_position.z, normal.x, normal.y, normal.z, uv.x, uv.y]
            self.vertex_arrays[mesh_id] = scaled_vertex_array

    def draw(self, shader):
        for mesh_id, mesh_material in self.mesh_materials.items():
            material = self.materials[mesh_material]
            shader.set_material_diffuse(Color(1.0, 1.0, 1.0))#(material.diffuse)
            shader.set_material_specular(material.specular)
            shader.set_material_shininess(material.shininess)
            shader.set_attribute_buffers_with_uv(self.vertex_buffer_ids[mesh_id])
            shader.set_using_tex(1.0)
            glActiveTexture(GL_TEXTURE0)
            glBindTexture(GL_TEXTURE_2D, material.tex_diffuse)
            shader.set_dif_tex(0)
            glDrawArrays(GL_TRIANGLES, 0, self.vertex_counts[mesh_id])
            glBindBuffer(GL_ARRAY_BUFFER, 0)
            shader.set_using_tex(0.0)


    def rotate(self, angle, axis):
        rotation_matrix = self._create_rotation_matrix(angle, axis)
        for key in self.vertex_arrays.keys():
            rotated_array = []
            for i in range(0, len(self.vertex_arrays[key]), 8):
                position = numpy.array([self.vertex_arrays[key][i], self.vertex_arrays[key][i+1], self.vertex_arrays[key][i+2], 1.0])
                rotated_position = rotation_matrix.dot(position)
                rotated_array.extend([
                    rotated_position[0],
                    rotated_position[1],
                    rotated_position[2],
                    self.vertex_arrays[key][i+3],
                    self.vertex_arrays[key][i+4],
                    self.vertex_arrays[key][i+5],
                    self.vertex_arrays[key][i+6],
                    self.vertex_arrays[key][i+7]
                ])
            self.vertex_arrays[key] = rotated_array

    def _create_rotation_matrix(self, angle, axis):
        c = cos(angle)
        s = sin(angle)
        x, y, z = axis
        return numpy.array([
            [c + (1 - c) * x * x, (1 - c) * x * y - s * z, (1 - c) * x * z + s * y, 0],
            [(1 - c) * y * x + s * z, c + (1 - c) * y * y, (1 - c) * y * z - s * x, 0],
            [(1 - c) * z * x - s * y, (1 - c) * z * y + s * x, c + (1 - c) * z * z, 0],
            [0, 0, 0, 1]
        ])

# Cube with vertex array, loaded in the GL array buffer, this is used in all brick shaped objects in the game
class Cube:
    def __init__(self):
        vertex_array = [
            -0.5, -0.5, -0.5, 0.0, 0.0, -1.0, 2/3, 0.0,
            -0.5, 0.5, -0.5, 0.0, 0.0, -1.0, 2/3, 1/3,
            0.5, -0.5, -0.5, 0.0, 0.0, -1.0, 1.0, 0.0,
            0.5, 0.5, -0.5, 0.0, 0.0, -1.0, 1.0, 1/3,
            #// right
            0.5, -0.5, -0.5, 1.0, 0.0, 0.0, 2/3, 1/3,
            0.5, 0.5, -0.5, 1.0, 0.0, 0.0, 2/3, 2/3,
            0.5, -0.5, 0.5, 1.0, 0.0, 0.0, 1.0, 1/3,
            0.5, 0.5, 0.5, 1.0, 0.0, 0.0, 1.0, 2/3,
            #// ront
            0.5, -0.5, 0.5, 0.0, 0.0, 1.0, 1/3, 1/3,
            0.5, 0.5, 0.5, 0.0, 0.0, 1.0, 1/3, 2/3,
            -0.5, -0.5, 0.5, 0.0, 0.0, 1.0, 2/3, 1/3,
            -0.5, 0.5, 0.5, 0.0, 0.0, 1.0, 2/3, 2/3,
            #// let
            -0.5, -0.5, 0.5, -1.0, 0.0, 0.0, 1/3, 1/3,
            -0.5, 0.5, 0.5, -1.0, 0.0, 0.0, 1/3, 2/3,
            -0.5, -0.5, -0.5, -1.0, 0.0, 0.0, 0.0, 1/3,
            -0.5, 0.5, -0.5, -1.0, 0.0, 0.0, 0.0, 2/3,
            #// top
            -0.5, 0.5, -0.5, 0.0, 1.0, 0.0, 1/3, 2/3,
            -0.5, 0.5, 0.5, 0.0, 1.0, 0.0, 1/3, 1.0,
            0.5, 0.5, -0.5, 0.0, 1.0, 0.0, 2/3, 2/3,
            0.5, 0.5, 0.5, 0.0, 1.0, 0.0, 2/3, 1.0,
            #// bottom
            -0.5, -0.5, -0.5, 0.0, -1.0, 0.0, 1/3, 0.0,
            -0.5, -0.5, 0.5, 0.0, -1.0, 0.0, 1/3, 1/3,
            0.5, -0.5, -0.5, 0.0, -1.0, 0.0, 2/3, 0.0,
            0.5, -0.5, 0.5, 0.0, -1.0, 0.0, 2/3, 1/3]

        self.vertex_buffer_id = glGenBuffers(1)
        glBindBuffer(GL_ARRAY_BUFFER, self.vertex_buffer_id)
        glBufferData(GL_ARRAY_BUFFER, numpy.array(vertex_array, dtype='float32'), GL_STATIC_DRAW)
        glBindBuffer(GL_ARRAY_BUFFER, 0)
        vertex_array = None

    def draw(self, shader):
        shader.set_attribute_buffers_with_uv(self.vertex_buffer_id)
        glDrawArrays(GL_TRIANGLE_STRIP, 0, 4)
        glDrawArrays(GL_TRIANGLE_STRIP, 4, 4)
        glDrawArrays(GL_TRIANGLE_STRIP, 8, 4)
        glDrawArrays(GL_TRIANGLE_STRIP, 12, 4)
        glDrawArrays(GL_TRIANGLE_STRIP, 16, 4)
        glDrawArrays(GL_TRIANGLE_STRIP, 20, 4)
        glBindBuffer(GL_ARRAY_BUFFER, 0)

# Creates a spherical object, vertex array loaded in the GL array buffer
class Sphere:
    def __init__(self, stacks = 12, slices = 24):
        vertex_array = []
        self.slices = slices
        stack_interval = pi / stacks
        slice_interval = 2.0 * pi / slices
        self.vertex_count = 0

        for stack_count in range(stacks):
            stack_angle = stack_count * stack_interval
            for slice_count in range(slices + 1):
                slice_angle = slice_count * slice_interval
                for _ in range(2):
                    vertex_array.append(sin(stack_angle) * cos(slice_angle))
                    vertex_array.append(cos(stack_angle))
                    vertex_array.append(sin(stack_angle) * sin(slice_angle))

                vertex_array.append(slice_count / slices)
                vertex_array.append(stack_count / stacks)
                
                for _ in range(2):
                    vertex_array.append(sin(stack_angle + stack_interval) * cos(slice_angle))
                    vertex_array.append(cos(stack_angle + stack_interval))
                    vertex_array.append(sin(stack_angle + stack_interval) * sin(slice_angle))

                vertex_array.append(slice_count / slices)
                vertex_array.append((stack_count + 1) / stacks)

                self.vertex_count += 2
        
        self.vertex_buffer_id = glGenBuffers(1)
        glBindBuffer(GL_ARRAY_BUFFER, self.vertex_buffer_id)
        glBufferData(GL_ARRAY_BUFFER, numpy.array(vertex_array, dtype='float32'), GL_STATIC_DRAW)
        glBindBuffer(GL_ARRAY_BUFFER, 0)
        vertex_array = None

    def draw(self, shader):
        shader.set_attribute_buffers_with_uv(self.vertex_buffer_id)
        for i in range(0, self.vertex_count, (self.slices + 1) * 2):
            glDrawArrays(GL_TRIANGLE_STRIP, i, (self.slices + 1) * 2)
        glBindBuffer(GL_ARRAY_BUFFER, 0)