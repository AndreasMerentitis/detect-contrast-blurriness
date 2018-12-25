#!/usr/bin/env python
# -*- coding: utf-8 -*-
import logging

import cv2
import numpy as np

from skimage.color import rgb2gray
from skimage.util.dtype import dtype_range, dtype_limits
from skimage._shared.utils import warn

import pdb



def fix_image_size(image, expected_pixels=2E6):
    ratio = float(expected_pixels) / float(image.shape[0] * image.shape[1])
    return cv2.resize(image, (0, 0), fx=ratio, fy=ratio)


def estimate_blur(image, threshold=100):
    if image.ndim == 3:
        image = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)

    blur_map = cv2.Laplacian(image, cv2.CV_64F)
    score = np.var(blur_map)
    return blur_map, score, bool(score < threshold)


def pretty_blur_map(blur_map, sigma=5):
    abs_image = np.log(np.abs(blur_map).astype(np.float32))
    cv2.blur(abs_image, (sigma, sigma))
    return cv2.medianBlur(abs_image, sigma)



def check_contrast(image, fraction_threshold=0.20, lower_percentile=1,
                    upper_percentile=99, method='linear'):
    """Detemine if an image is low contrast.
    Parameters
    ----------
    image : array-like
        The image under test.
    fraction_threshold : float, optional
        The low contrast fraction threshold. An image is considered low-
        contrast when its range of brightness spans less than this
        fraction of its data type's full range. [1]_
    lower_percentile : float, optional
        Disregard values below this percentile when computing image contrast.
    upper_percentile : float, optional
        Disregard values above this percentile when computing image contrast.
    method : str, optional
        The contrast determination method.  Right now the only available
        option is "linear".
    Returns
    -------
    out : bool
        True when the image is determined to be low contrast.
    References
    ----------
    .. [1] http://scikit-image.org/docs/dev/user_guide/data_types.html
    Examples
    --------
    >>> image = np.linspace(0, 0.04, 100)
    >>> is_low_contrast(image)
    True
    >>> image[-1] = 1
    >>> is_low_contrast(image)
    True
    >>> is_low_contrast(image, upper_percentile=100)
    False
    """

    image = np.asanyarray(image)
    if image.ndim == 3 and image.shape[2] in [3, 4]:
        image = rgb2gray(image)


    dlimits = dtype_limits(image, clip_negative=False)
    limits = np.percentile(image, [lower_percentile, upper_percentile])
    ratio = (limits[1] - limits[0]) / (dlimits[1] - dlimits[0])

    return ratio, ratio < fraction_threshold




