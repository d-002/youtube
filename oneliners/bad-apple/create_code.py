from glob import glob
from os import unlink
from os.path import isdir, isfile, join
from sys import argv, stderr

import numpy as np
from PIL import Image

MARGIN = (240, 0)
GRID_HEIGHT = 20
CHAR_HEIGHT = 2.1  # ascii characters height with respect to width
DELAY_VALUE = 1 / (138*2/60)

if len(argv) != 4:
    print('Wrong number of arguments', file=stderr)
    exit(1)

frames_dir, template_file, target_file = argv[1:]

if not isdir(frames_dir):
    print('Provided frames directory is invalid or does not exist', file=stderr)
    exit(2)

if not isfile(template_file):
    print('Provided template file is invalid or does not exist', file=stderr)

print('Processing frames')

frames = glob(join(frames_dir, '*.png'))
frames.sort()
frames_data: list[str] = []
w, h = 0, 0  # for LSPs
for index, frame in enumerate(frames):
    # read and scale image down
    img = Image.open(frame)
    w, h = img.size
    img = img.crop((MARGIN[0], MARGIN[1], w - MARGIN[0], h - MARGIN[1]))
    w, h = img.size
    img = img.resize((round(GRID_HEIGHT * w / h * CHAR_HEIGHT), GRID_HEIGHT))
    w, h = img.size

    # read and compress data
    arr = np.asarray(img)[:, :, 0]
    frame_data = ''
    #prev_line_data = np.zeros(arr[0].shape, dtype=np.bool)
    for line in arr:
        bitsarr = np.array([char >= 128 for char in line], dtype=np.bool)
        # removed because did not end up saving space
        """
        # XOR: xor consecutive lines to have lots of False
        line_data = bitsarr ^ prev_line_data
        prev_line_data = line_data
        """
        line_data = bitsarr

        # RLE: use the printable ascii characters for the repetition count << 1,
        # plus the data bit
        max_count = (126 - 33 + 1) >> 1
        prev_bit = None
        count = 0
        total_count = 0
        for i in range(len(line_data) + 1):
            b = None if i == len(line_data) else line_data[i]
            if b == prev_bit and count < max_count - 1:
                count += 1
            else:
                if prev_bit is not None:
                    frame_data += chr(33 + (count << 1) + prev_bit)
                prev_bit = b
                total_count += count
                count = 1

    frames_data.append(frame_data)

    print(f'Progress: {round(index * 100 / len(frames))}%', end='\r')
print()

with open(template_file, encoding='utf-8') as f:
    template = f.read()
content = template.replace('BAD_APPLE_STRING', repr('\n'.join(frames_data)))
# w and h should be right
content = content.replace('W_VALUE', str(w))
content = content.replace('H_VALUE', str(h))
content = content.replace('DELAY_VALUE', f'{DELAY_VALUE:.5f}')
with open(target_file, 'w', encoding='utf-8') as f:
    f.write(content)
print('Done')
