'''
Utility to create a video from a directory of images
'''
import os
import sys

import cv2
import Tkinter
import tkFileDialog
import tkMessageBox



Tkinter.Tk().withdraw()
sourceDir = tkFileDialog.askdirectory()
destDir = sourceDir + '/' + 'results'
try:
    os.mkdir(destDir)
except OSError as e:
    if e.errno == 17:
        if tkMessageBox.askokcancel('Folder already exists',
                                    'The output folder already exists, proceeding may overwrite the files it contains.'):
            pass
        else:
            print('Exiting ImageBlender')
            sys.exit(1)

fileNames = [sourceDir + '/' + str(f) for f in os.listdir(sourceDir) if f.endswith('.JPG') or f.endswith('.jpg')]
fileNames.reverse()
fourcc = cv2.VideoWriter_fourcc('D','I','V','X')
outname = destDir + '/video.avi'
vid = cv2.VideoWriter(outname,fourcc,30.0, (2592,1944))

while len(fileNames) > 0:
    imageName = fileNames.pop()
    imageA = cv2.imread(imageName,1)
    vid.write(imageA)
vid.release()