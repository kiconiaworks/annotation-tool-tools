from typing import List

from tqdm import tqdm
from PIL.Image import Image
from pdf2image import convert_from_path
import argparse
import os

if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('input_files', nargs='+')
    parser.add_argument('--output-dir', '-o')
    args = parser.parse_args()

    input_files = args.input_files

    for input_file in tqdm(input_files):
        images: List[Image] = convert_from_path(input_file)

        for i, image in enumerate(images):
            filepath, ext = os.path.splitext(input_file)
            if args.output_dir is not None:
                filepath = os.path.join(args.output_dir, os.path.basename(filepath))
            image.save(f"{filepath}_{i}.png")
