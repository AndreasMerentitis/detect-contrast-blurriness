#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os
import glob
import json
import argparse
import logging

import cv2
import numpy as np

#from skimage.exposure import is_low_contrast

from blur_detection.detection import estimate_blur
from blur_detection.detection import fix_image_size
from blur_detection.detection import check_contrast

import pdb


def find_images(input_dir):
    extensions = [".jpg", ".png", ".jpeg"]

    for root, dirs, files in os.walk(input_dir):
        for file in files:
            if os.path.splitext(file)[1].lower() in extensions:
                yield os.path.join(root, file)


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='run blur detection on a single image')
    parser.add_argument('-i', '--input_dir', dest="input_dir", type=str, required=True, help="directory of images")
    parser.add_argument('-s', '--save_path', dest='save_path', type=str, required=True, help="path to save output")
    # parameters
    parser.add_argument("-t", "--threshold", dest='threshold', type=float, default=5.0, help="blurry threshold")
    parser.add_argument("-f", "--fix_size", dest="fix_size", help="fix the image size", action="store_true")
    # options
    parser.add_argument("-v", "--verbose", dest='verbose', help='set logging level to debug', action="store_true")
    parser.add_argument("-d", "--display", dest='display', help='display images', action="store_true")

    args = parser.parse_args()

    if args.verbose:
        logging.basicConfig(level=logging.DEBUG)
    else:
        logging.basicConfig(level=logging.INFO)

    results = []

    for input_path in find_images(args.input_dir):
        try:
            logging.info("processing {0}".format(input_path))
            input_image = cv2.imread(input_path)

            if args.fix_size:
                input_image = fix_image_size(input_image)

            blur_map, score, is_blurry = estimate_blur(input_image, threshold=args.threshold)

            contrast_ratio, is_low_contrast = check_contrast(input_image)
            is_low_contrast = bool(is_low_contrast)

            logging.info("input_path: {0}, clearness_score: {1}, blurry: {2}, contrast_score: {3}, low_contrast: {4}".format(input_path, score, is_blurry, contrast_ratio, is_low_contrast))
            results.append({"input_path": input_path, "clearness_score": score, "blurry": is_blurry, "contrast_score": contrast_ratio, "low_contrast": is_low_contrast})

            if args.display:
                cv2.imshow("input", input_image)
                cv2.imshow("result", pretty_blur_map(blur_map))
                cv2.waitKey(0)
        except Exception as e:
            print(e)
            pass

    logging.info("writing results to {0}".format(args.save_path))

    assert os.path.splitext(args.save_path)[1] == ".json"

    with open(args.save_path, 'w') as outfile:
        data = {"input_dir": args.input_dir, "threshold": args.threshold, "results": results}
        json.dump(data, outfile, sort_keys=True, indent=4)
        outfile.write("\n")



