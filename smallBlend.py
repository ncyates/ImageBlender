'''
A version of the imageBlender without multiprocessing 
to use for directories with fewer than 2*(multiprocessing.cpu_count()) images
'''
#TODO: make a part of the multiprocessing version for simplicity
import os
import math
import random
import sys

import cv2
import Tkinter
import tkFileDialog
import tkMessageBox
import numpy as np



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
sampleImage = cv2.imread(fileNames[0], 1)
stdDim = sampleImage.shape  # standard dimensions based on one image. H x W
random.shuffle(fileNames)  # possibly gives better end result blend
numFiles = len(fileNames)
zeroPad = int(math.ceil(math.log(numFiles + 1, 10))) + 1  # of zeros to pad file names for output ordering

count = 0
while len(fileNames) > 1:
    fileNameA = fileNames.pop()
    fileNameB = fileNames.pop()
    imageA = cv2.imread(fileNameA, 1)
    imageB = cv2.imread(fileNameB, 1)
    if imageA.shape != stdDim:
        imageA.cv2.resize(imageA, (stdDim[1], stdDim[0]))
    if imageB.shape != stdDim:
        imageB.cv2.resize(imageB, (stdDim[1], stdDim[0]))
    blendName = destDir + '/' + 'blend_' + '_' + str(count).zfill(zeroPad) + '.jpg'
    blend = cv2.addWeighted(imageA, .5, imageB, .5, 0)
    cv2.imwrite(blendName, blend)
    fileNames.insert(0,blendName)
    count += 1

unbalanced = cv2.imread(blendName,1)
colorChannels = cv2.split(unbalanced)
normChannels = []
for channel in colorChannels:
    sortFlat = np.sort(channel.flatten())
    flatLen = len(sortFlat)
    lowThresh = sortFlat[int(math.floor(flatLen * .005))]
    highThresh = sortFlat[int(math.ceil(flatLen * .995))]
    maskLow = channel < lowThresh
    maskHigh = channel > highThresh
    channel = np.ma.array(channel, mask=maskLow, fill_value=lowThresh)
    channel = channel.filled()
    channel = np.ma.array(channel, mask=maskHigh, fill_value=highThresh)
    channel = channel.filled()
    cv2.normalize(channel, channel, 0, 255, cv2.NORM_MINMAX)
    normChannels.append(channel)
cv2.imwrite(destDir + '/' + '_Final_Balanced.jpg',cv2.merge(normChannels))
