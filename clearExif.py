import sys
import os
import multiprocessing

import exifread
import Tkinter
import tkFileDialog
from PIL import Image, ImageFile


def strip(filename):
    ImageFile.LOAD_TRUNCATED_IMAGES = True
    file = open(filename, 'rb')
    tags = exifread.process_file(file)
    sys.stdout.write('\nEXIF Orientation: ' + str(tags.get('Image Orientation')))
    if tags.get('Image Orientation') != None:
        sys.stdout.write('\nEXIF orientation data found on ' + filename + ', stripping EXIF')
        image = Image.open(filename)
        data = list(image.getdata())
        imageNoEXIF = Image.new(image.mode, image.size)
        imageNoEXIF.putdata(data)
        imageNoEXIF.save(filename)


if __name__ == "__main__":
    ImageFile.LOAD_TRUNCATED_IMAGES = True
    Tkinter.Tk().withdraw()
    sourceDir = tkFileDialog.askdirectory()
    fileNames = [sourceDir + '/' + str(f) for f in os.listdir(sourceDir) if f.endswith('.JPG') or f.endswith('.jpg')]
    pool = multiprocessing.Pool()
    listEXIF = pool.map(strip,fileNames)