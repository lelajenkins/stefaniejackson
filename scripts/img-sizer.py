#!/usr/bin/env python3

import argparse
import os
import shutil
import subprocess
import sys

DEFAULT_MAX_DIM = 1200
MAX_BYTES = 1_000_000
IMAGE_EXTS = {'.jpg', '.jpeg', '.png', '.gif', '.tiff', '.tif', '.webp', '.bmp'}


def find_imagemagick():
    for name in ('magick', 'convert'):
        path = shutil.which(name)
        if path:
            return path
    return None


def is_image_file(path):
    return os.path.splitext(path)[1].lower() in IMAGE_EXTS


def output_is_directory(path):
    if os.path.isdir(path):
        return True
    return path.endswith(os.sep) or path.endswith('/') or path.endswith('\\')


def normalize_output_path(input_path, output_path):
    if output_is_directory(output_path):
        os.makedirs(output_path, exist_ok=True)
        return os.path.join(output_path, os.path.basename(input_path))

    if os.path.splitext(output_path)[1]:
        return output_path

    os.makedirs(output_path, exist_ok=True)
    return os.path.join(output_path, os.path.basename(input_path))


def build_batch_output_path(input_file, output_dir, max_dim=DEFAULT_MAX_DIM):
    name, ext = os.path.splitext(os.path.basename(input_file))
    return os.path.join(output_dir, f'{name}_{max_dim}px{ext}')


def run_convert(magick, src, dst, quality, max_dim=DEFAULT_MAX_DIM):
    # keep embedded color profiles and convert to sRGB to avoid faded colors
    cmd = [magick, src, '-resize', f'{max_dim}x{max_dim}>', '-colorspace', 'sRGB']
    suffix = os.path.splitext(dst)[1].lower()
    if suffix in ('.jpg', '.jpeg', '.webp'):
        cmd += ['-quality', str(quality)]
    elif suffix == '.png':
        cmd += ['-quality', str(quality), '-define', 'png:compression-level=9']
    else:
        cmd += ['-quality', str(quality)]
    cmd.append(dst)
    subprocess.run(cmd, check=True)


def compress_to_size(magick, src, dst, max_dim=DEFAULT_MAX_DIM):
    suffix = os.path.splitext(dst)[1].lower()
    if suffix in ('.jpg', '.jpeg', '.webp'):
        quality = 88
        while quality >= 30:
            run_convert(magick, src, dst, quality, max_dim=max_dim)
            if os.path.getsize(dst) <= MAX_BYTES:
                return True
            quality -= 6
        return os.path.getsize(dst) <= MAX_BYTES

    if suffix == '.png':
        run_convert(magick, src, dst, 90, max_dim=max_dim)
        return os.path.getsize(dst) <= MAX_BYTES

    run_convert(magick, src, dst, 85, max_dim=max_dim)
    return os.path.getsize(dst) <= MAX_BYTES


def process_file(magick, src, dst, max_dim=DEFAULT_MAX_DIM):
    os.makedirs(os.path.dirname(dst), exist_ok=True)
    try:
        success = compress_to_size(magick, src, dst, max_dim=max_dim)
    except subprocess.CalledProcessError as exc:
        print(f'Failed to process {src}: {exc}', file=sys.stderr)
        return False

    if not success:
        print(f'Warning: {dst} still exceeds {MAX_BYTES} bytes', file=sys.stderr)
    else:
        size = os.path.getsize(dst)
        print(f'Wrote {dst} ({size} bytes)')
    return success


def main():
    parser = argparse.ArgumentParser(
        description='Resize images so the larger axis is at most 1200px and output stays under 1MB.'
    )
    parser.add_argument('-i', '--input', help='Input file or directory')
    parser.add_argument('-o', '--output', help='Output file or directory')
    parser.add_argument('-m', '--max-dim', type=int, default=DEFAULT_MAX_DIM,
                        help='Maximum dimension for the larger image axis (default: 1200)')

    args = parser.parse_args()

    if not args.input or not args.output:
        parser.print_usage()
        sys.exit(1)

    magick = find_imagemagick()
    if not magick:
        print('ImageMagick not found. Install it and make sure `magick` or `convert` is on PATH.', file=sys.stderr)
        sys.exit(1)

    src = os.path.abspath(args.input)
    dst = os.path.abspath(args.output)

    max_dim = args.max_dim

    if os.path.isdir(src):
        if os.path.isfile(dst):
            print('When input is a directory, output must be a directory.', file=sys.stderr)
            sys.exit(1)
        os.makedirs(dst, exist_ok=True)
        for entry in sorted(os.listdir(src)):
            inpath = os.path.join(src, entry)
            if not os.path.isfile(inpath) or not is_image_file(inpath):
                continue
            outpath = build_batch_output_path(inpath, dst, max_dim=max_dim)
            process_file(magick, inpath, outpath, max_dim=max_dim)
    elif os.path.isfile(src):
        if output_is_directory(dst):
            outpath = normalize_output_path(src, dst)
        else:
            outpath = normalize_output_path(src, dst)
        process_file(magick, src, outpath, max_dim=max_dim)
    else:
        print('Input path does not exist.', file=sys.stderr)
        sys.exit(1)


if __name__ == '__main__':
    main()
