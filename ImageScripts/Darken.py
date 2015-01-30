#!/usr/bin/env python

import sys
from PIL import Image

def main():
    image = Image.open(sys.argv[1])
    gray = image.convert('L')
    bw = gray.point(lambda x: 0 if x<127 else 255, '1')
    bw.save(sys.argv[2])

if __name__ == "__main__":
    main()
