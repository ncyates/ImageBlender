import multiprocessing
import os
import math
import random
import time
import sys

import cv2
import Tkinter
import tkFileDialog
import tkMessageBox


def blender(fileNameA, fileNameB, mergeName):
    imageA = cv2.imread(fileNameA, 1)
    imageB = cv2.imread(fileNameB, 1)
    imageA = cv2.resize(imageA, (2592, 1944))
    imageB = cv2.resize(imageB, (2592, 1944))
    imgc = cv2.addWeighted(imageA, .5, imageB, .5, 0)
    cv2.imwrite(mergeName, imgc)


def reducingMerge(process, q, chunk, dstDir, zeroPad):
    count = 0
    while len(chunk) > 1:
        a = chunk.pop()
        b = chunk.pop()
        outName = dstDir + '/' + 'merge_' + process + '_' + str(count).zfill(zeroPad) + '.jpg'
        blender(a,b,outName)
        chunk.insert(0, outName)
        count += 1
    q.put(outName)


if __name__ == "__main__":
    #start_time = time.time()
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
    filenames = [sourceDir + '/' + str(f) for f in os.listdir(sourceDir) if f.endswith('.JPG') or f.endswith('.jpg')]
    random.shuffle(filenames) # possibly gives better end result blend
    zeroPad = int(math.ceil(math.log(len(filenames) + 1, 10))) + 1 # leading zeros to pad file names for output ordering = ceiling of log base 10 of n+1
    reducingQ = multiprocessing.Queue()
    mpProcesses = []
    numFiles = len(filenames)
    numCores = multiprocessing.cpu_count()
    chunkLength = numFiles / numCores
    chunkStart = 0
    chunkEnd = chunkStart + chunkLength
    partialChunk = numFiles % numCores
    filesChunks = []
    for i in range(numCores):
        filesChunks.append(filenames[chunkStart:chunkEnd])
        chunkStart = chunkEnd
        chunkEnd = chunkStart + chunkLength
    while partialChunk > 0:
        filesChunks[len(filesChunks) - 1].append(filenames[(len(filenames)) - partialChunk])
        partialChunk -=1
    for i in range(len(filesChunks)):
        mpProcesses.append(multiprocessing.Process(target=reducingMerge, args=('p' + str(i), reducingQ, filesChunks[i], destDir, zeroPad)))
    for i in range(len(mpProcesses)):
        mpProcesses[i].start()
    for i in range(len(mpProcesses)):
        mpProcesses[i].join()
    wrapCount = 1
    while reducingQ.qsize() > 1:
        a = reducingQ.get()
        b = reducingQ.get()
        if reducingQ.qsize() == 2:
            outName = destDir + '/' + 'FinalMerge.jpg'
        else:
            outName = destDir + '/' + 'wrap' + str(wrapCount) + '.jpg'
        blender(a, b, outName)
        reducingQ.put(outName)
        wrapCount += 1

    for f in os.listdir(destDir): # Comment out to keep all merges on disk
        if str(os.path.basename(f)) != 'FinalMerge.jpg':
            os.remove(destDir + '/' + f)
    #print("took %s seconds" % (time.time() - start_time))
