# !/usr/bin/env python
# -*- coding: utf-8 -*-

"""
RGB Colourspace Visuals
=======================

Defines the *RGB Colourspace Visuals*:

-   :def:`RGB_colourspace_volume_visual`
-   :def:`RGB_colourspace_triangle_visual`
"""

from __future__ import division, unicode_literals

import numpy as np
from vispy.geometry.generation import create_box
from vispy.scene.visuals import Node, Line
from colour import RGB_to_XYZ, xy_to_XYZ
from colour.plotting import get_RGB_colourspace
from colour.plotting.volume import XYZ_to_reference_colourspace

from colour_analysis.constants import DEFAULT_PLOTTING_ILLUMINANT
from colour_analysis.utilities import CHROMATICITY_DIAGRAM_TRANSFORMATIONS
from colour_analysis.visuals import Box

__author__ = 'Colour Developers'
__copyright__ = 'Copyright (C) 2013 - 2015 - Colour Developers'
__license__ = 'New BSD License - http://opensource.org/licenses/BSD-3-Clause'
__maintainer__ = 'Colour Developers'
__email__ = 'colour-science@googlegroups.com'
__status__ = 'Production'

__all__ = ['RGB_identity_cube',
           'RGB_colourspace_volume_visual',
           'RGB_colourspace_triangle_visual']


def RGB_identity_cube(width_segments=16,
                      height_segments=16,
                      depth_segments=16,
                      planes=None,
                      uniform_colour=None,
                      uniform_opacity=1.0,
                      vertex_colours=True,
                      wireframe=False,
                      *args,
                      **kwargs):
    """
    Creates a *RGB* identity cube base on
    :class:`colour_analysis.visuals.Box` class.

    Parameters
    ----------
    width : numeric, optional
        Box width.
    height : numeric, optional
        Box height.
    depth : numeric, optional
        Box depth.
    width_segments : int, optional
        Box segments count along the width.
    height_segments : int, optional
        Box segments count along the height.
    depth_segments : int, optional
        Box segments count along the depth.
    planes: array_like, optional
        Any combination of ``{'-x', '+x', '-y', '+y', '-z', '+z'}``

        Included planes in the box construction.
    uniform_colour : array_like, optional
        Uniform mesh colour.
    uniform_opacity : numeric, optional
        Uniform mesh opacity.
    vertex_colour : array_like, optional
        Per vertex varying colour.
    wireframe : bool, optional
        Use wireframe display.
    \*args : list, optional
        Arguments passed to :class:`colour_analysis.visuals.Box` class
        constructor.
    \**kwargs : dict, optional
        Keywords arguments passed to :class:`colour_analysis.visuals.Box` class
        constructor.
    """

    vertices, _faces, _outline = create_box(width_segments=width_segments,
                                            height_segments=height_segments,
                                            depth_segments=depth_segments,
                                            planes=planes)

    vertex_colours = vertices['color'] if vertex_colours else None

    RGB_box = Box(width_segments=width_segments,
                  height_segments=height_segments,
                  depth_segments=depth_segments,
                  planes=planes,
                  uniform_colour=uniform_colour,
                  uniform_opacity=uniform_opacity,
                  vertex_colours=vertex_colours,
                  wireframe=wireframe,
                  wireframe_offset=(1, 1),
                  *args,
                  **kwargs)

    vertices = RGB_box.mesh_data.get_vertices()
    vertices += 0.5
    RGB_box.mesh_data.set_vertices(vertices)

    return RGB_box


def RGB_colourspace_volume_visual(colourspace='Rec. 709',
                                  reference_colourspace='CIE xyY',
                                  segments=16,
                                  uniform_colour=None,
                                  uniform_opacity=0.5,
                                  wireframe=True,
                                  wireframe_colour=None,
                                  wireframe_opacity=1.0,
                                  parent=None):
    """
    Returns a :class:`vispy.scene.visuals.Node` class instance with one or two
    :class:`colour_analysis.visuals.Box` class instance children representing
    a *RGB* colourspace volume visual.

    Parameters
    ----------
    colourspace : unicode, optional
        {'Rec. 709', 'ACES2065-1', 'ACEScc', 'ACEScg', 'ACESproxy',
        'ALEXA Wide Gamut RGB', 'Adobe RGB 1998', 'Adobe Wide Gamut RGB',
        'Apple RGB', 'Best RGB', 'Beta RGB', 'CIE RGB', 'Cinema Gamut',
        'ColorMatch RGB', 'DCI-P3', 'DCI-P3+', 'DRAGONcolor', 'DRAGONcolor2',
        'Don RGB 4', 'ECI RGB v2', 'Ekta Space PS 5', 'Max RGB', 'NTSC RGB',
        'Pal/Secam RGB', 'ProPhoto RGB', 'REDcolor', 'REDcolor2', 'REDcolor3',
        'REDcolor4', 'Rec. 2020', 'Russell RGB', 'S-Gamut', 'S-Gamut3',
        'S-Gamut3.Cine', 'SMPTE-C RGB', 'V-Gamut', 'Xtreme RGB', 'aces',
        'adobe1998', 'prophoto', 'sRGB'}

        :class:`colour.RGB_Colourspace` class instance name defining the *RGB*
        colourspace volume to draw.
    segments : int, optional
        Box segments.
    uniform_colour : array_like, optional
        Uniform mesh colour.
    uniform_opacity : numeric, optional
        Uniform mesh opacity.
    vertex_colour : array_like, optional
        Per vertex varying colour.
    wireframe : bool, optional
        Use wireframe display.
        Uniform mesh opacity.
    wireframe_colour : array_like, optional
        Wireframe mesh colour.
    wireframe_opacity : numeric, optional
        Wireframe mesh opacity.
    parent : Node, optional
        Parent of the *RGB* colourspace volume visual in the `SceneGraph`.
    """

    node = Node(parent)

    colourspace = get_RGB_colourspace(colourspace)

    RGB_cube_f = RGB_identity_cube(
        width_segments=segments,
        height_segments=segments,
        depth_segments=segments,
        uniform_colour=uniform_colour,
        uniform_opacity=uniform_opacity,
        vertex_colours=not uniform_colour,
        parent=node)

    vertices = RGB_cube_f.mesh_data.get_vertices()
    XYZ = RGB_to_XYZ(
        vertices,
        colourspace.whitepoint,
        colourspace.whitepoint,
        colourspace.RGB_to_XYZ_matrix)
    value = XYZ_to_reference_colourspace(XYZ,
                                         colourspace.whitepoint,
                                         reference_colourspace)
    value[np.isnan(value)] = 0

    RGB_cube_f.mesh_data.set_vertices(value)

    if wireframe:
        RGB_cube_w = RGB_identity_cube(
            width_segments=segments,
            height_segments=segments,
            depth_segments=segments,
            uniform_colour=wireframe_colour,
            uniform_opacity=wireframe_opacity,
            vertex_colours=not wireframe_colour,
            wireframe=True,
            parent=node)
        RGB_cube_w.mesh_data.set_vertices(value)

    return node


def RGB_colourspace_triangle_visual(colourspace='Rec. 709',
                                    diagram='CIE 1931',
                                    uniform_colour=None,
                                    uniform_opacity=1.0,
                                    width=4.0,
                                    parent=None):
    """
    Returns a :class:`vispy.scene.visuals.Line` class instance representing
    a *RGB* colourspace triangle visual.

    Parameters
    ----------
    colourspace : unicode, optional
        See :def:`RGB_colourspace_volume_visual` argument for possible values.

        :class:`colour.RGB_Colourspace` class instance name defining the *RGB*
        colourspace triangle to draw.
    diagram : unicode, optional
        {'CIE 1931', 'CIE 1960 UCS', 'CIE 1976 UCS'}

        Chromaticity diagram to use.
    uniform_colour : array_like, optional
        Uniform triangle colour.
    uniform_opacity : numeric, optional
        Uniform mesh opacity.
    vertex_colour : array_like, optional
        Per vertex varying colour.
    wireframe : bool, optional
        Use wireframe display.
        Uniform mesh opacity.
    wireframe_colour : array_like, optional
        Wireframe mesh colour.
    wireframe_opacity : numeric, optional
        Wireframe mesh opacity.
    parent : Node, optional
        Parent of the *RGB* colourspace volume visual in the `SceneGraph`.
    """

    if uniform_colour is None:
        uniform_colour = (0.8, 0.8, 0.8)

    colourspace = get_RGB_colourspace(colourspace)

    illuminant = DEFAULT_PLOTTING_ILLUMINANT

    XYZ_to_ij = CHROMATICITY_DIAGRAM_TRANSFORMATIONS[diagram]['XYZ_to_ij']

    ij = XYZ_to_ij(xy_to_XYZ(colourspace.primaries), illuminant)
    # TODO: Remove following hack dealing with 'agg' method issues.
    ij = np.vstack((ij[-1, ...], ij, ij[0, ...]))

    ij[np.isnan(ij)] = 0

    RGB = np.hstack((uniform_colour, uniform_opacity)),

    line = Line(ij,
                RGB,
                width=width,
                method='agg',
                parent=parent)

    return line
