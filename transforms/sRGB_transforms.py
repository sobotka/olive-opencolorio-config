#!/usr/bin/env python
# -*- coding: utf-8 -*-

import PyOpenColorIO
import numpy
import colour
import os
from colour import (
    io,
    adaptation,
    models
)
from common.utilities import *


def make_transforms(transform_path, config):

    # The canonized sRGB transform
    # Due to the nature of the GPU issues in OpenColorIO v1.1.1, this
    # 1D LUT oversamples the sRGB transfer function range to have
    # correct results via the GPU.
    #
    # It also adds a faster inverse transform instead of a lookup for
    # output processing speed. It must be larger as a result, due to
    # quantisation issues in the linear domain.

    sRGB_domain = numpy.array([-0.125, 3.0])
    sRGB_tf_to_linear_LUT = colour.LUT1D(
        table=models.sRGB_COLOURSPACE.cctf_decoding(
            colour.LUT1D.linear_table(
                1024, sRGB_domain)),
        name="sRGB to Linear",
        domain=sRGB_domain,
        comments=["sRGB CCTF to Display Linear"])
    sRGB_linear_to_tf_LUT_variant = colour.LUT1D(
        table=models.sRGB_COLOURSPACE.cctf_encoding(
            colour.LUT1D.linear_table(
                8192, sRGB_domain)),
        name="Linear to sRGB",
        domain=sRGB_domain,
        comments=["sRGB Display Linear to CCTF"])

    path = os.path.join(
        transform_path,
        "sRGB_CCTF_to_Linear.spi1d"
    )
    create_directory(path)
    io.write_LUT(
        LUT=sRGB_tf_to_linear_LUT,
        path=path,
        decimals=10)

    path = os.path.join(
        transform_path,
        "sRGB_Linear_to_CCTF.spi1d"
    )
    create_directory(path)
    io.write_LUT(
        LUT=sRGB_linear_to_tf_LUT_variant,
        path=path,
        decimals=10)

    # Define the sRGB specification
    colourspace = PyOpenColorIO.ColorSpace(
        family="Colourspace",
        name="sRGB Colourspace")
    colourspace.setDescription("sRGB IEC 61966-2-1 Colourspace")
    colourspace.setBitDepth(PyOpenColorIO.Constants.BIT_DEPTH_F32)
    colourspace.setAllocationVars([0.0, 1.0])
    colourspace.setAllocation(PyOpenColorIO.Constants.ALLOCATION_UNIFORM)
    transform_to = PyOpenColorIO.FileTransform(
            "sRGB_CCTF_to_Linear.spi1d",
            interpolation=PyOpenColorIO.Constants.INTERP_NEAREST)

    transform_from = PyOpenColorIO.FileTransform(
            "sRGB_Linear_to_CCTF.spi1d",
            interpolation=PyOpenColorIO.Constants.INTERP_NEAREST)

    colourspace.setTransform(
        transform_to, PyOpenColorIO.Constants.COLORSPACE_DIR_TO_REFERENCE)
    colourspace.setTransform(
        transform_from, PyOpenColorIO.Constants.COLORSPACE_DIR_FROM_REFERENCE)

    config.addColorSpace(colourspace)

    # Define the commodity sRGB transform
    colourspace = PyOpenColorIO.ColorSpace(
        family="Colourspace",
        name="BT.709 2.2 CCTF Colourspace")
    colourspace.setDescription("Commodity Display BT.709 2.2 CCTF Colourspace")
    colourspace.setBitDepth(PyOpenColorIO.Constants.BIT_DEPTH_F32)
    colourspace.setAllocationVars([0.0, 1.0])
    colourspace.setAllocation(PyOpenColorIO.Constants.ALLOCATION_UNIFORM)
    transform_to = PyOpenColorIO.ExponentTransform([2.2, 2.2, 2.2, 1.0])

    transform_from = PyOpenColorIO.ExponentTransform([2.2, 2.2, 2.2, 1.0])
    transform_from.setDirection(
        PyOpenColorIO.Constants.TRANSFORM_DIR_INVERSE)

    colourspace.setTransform(
        transform_to, PyOpenColorIO.Constants.COLORSPACE_DIR_TO_REFERENCE)
    colourspace.setTransform(
        transform_from, PyOpenColorIO.Constants.COLORSPACE_DIR_FROM_REFERENCE)

    config.addColorSpace(colourspace)
