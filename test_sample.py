#!/usr/bin/env python
# -*- coding: utf-8 -*-

import argparse
import glob
import json
import logging
import os

import cv2
import matplotlib.pyplot as plt
import numpy as np

from blur_detection.detection import (check_contrast, estimate_blur,
                                      fix_image_size)


def find_images(input_dir):
    extensions = [".jpg", ".png", ".jpeg"]

    for root, dirs, files in os.walk(input_dir):
        for file in files:
            if os.path.splitext(file)[1].lower() in extensions:
                yield os.path.join(root, file)


def test_answer():
    full_file_name = 'few_images/' + '32947_0.png'
    
    input_image = cv2.imread(full_file_name)
    input_image = fix_image_size(input_image)
    blur_map, score, is_blurry = estimate_blur(input_image, threshold=5.0)
    contrast_ratio, is_low_contrast = check_contrast(input_image)
    assert score == 0.8788307786605958
    assert contrast_ratio == 0.27411588235294115






