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


def blender(fileNameA, fileNameB, blendName, stdDim):
    imageA = cv2.imread(fileNameA, 1)
    imageB = cv2.imread(fileNameB, 1)
    if imageA.shape != stdDim:
        imageA.cv2.resize(imageA, (stdDim[1], stdDim[0]))
    if imageB.shape != stdDim:
        imageB.cv2.resize(imageB, (stdDim[1], stdDim[0]))
    blend = cv2.addWeighted(imageA, .5, imageB, .5, 0)
    return cv2.imwrite(blendName, blend)


def reducer(process, q, chunk, dstDir, zeroPad, stdDim):
    count = 0
    while len(chunk) > 1:
        fileNameA = chunk.pop()
        fileNameB = chunk.pop()
        blendName = dstDir + '/' + 'blend_' + process + '_' + str(count).zfill(zeroPad) + '.jpg'
        if blender(fileNameA,fileNameB,blendName,stdDim):
            chunk.insert(0, blendName)
        else:
            sys.stdout.write('Problem with blending ' + fileNameA + ' & ' + fileNameB)
        count += 1
    q.put(chunk[0])


if __name__ == "__main__":
    start_time = time.time()
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
    #TODO: what about many different image dimensions? Possibly scan for all and set standard as most common dim.
    random.shuffle(fileNames)  # possibly gives better end result blend
    reducingQ = multiprocessing.Queue()
    mpProcesses = []
    numFiles = len(fileNames)
    numCores = multiprocessing.cpu_count()
    chunkLength = numFiles / numCores
    chunkStart = 0
    chunkEnd = chunkStart + chunkLength
    partialChunk = numFiles % numCores
    filesChunks = []
    zeroPad = int(math.ceil(math.log(chunkLength + 1,10))) + 1  # of zeros to pad file names for output ordering
    for i in range(numCores):
        filesChunks.append(fileNames[chunkStart:chunkEnd])
        chunkStart = chunkEnd
        chunkEnd = chunkStart + chunkLength
    while partialChunk > 0:
        filesChunks[len(filesChunks) - 1].append(fileNames[(len(fileNames)) - partialChunk])
        partialChunk -=1
    for i in range(len(filesChunks)):
        mpProcesses.append(multiprocessing.Process(target=reducer, args=('p' + str(i), reducingQ, filesChunks[i], destDir, zeroPad, stdDim)))
    for i in range(len(mpProcesses)):
        mpProcesses[i].start()
    for i in range(len(mpProcesses)):
        mpProcesses[i].join()
    wrapCount = 1
    while reducingQ.qsize() > 1:
        wrapUpA = reducingQ.get()
        wrapUpB = reducingQ.get()
        if reducingQ.qsize() == 2:
            outName = destDir + '/' + '_Final.jpg'
        else:
            outName = destDir + '/' + '_wrapUp' + str(wrapCount) + '.jpg'
        if blender(wrapUpA, wrapUpB, outName, stdDim):
            reducingQ.put(outName)
        else:
            print('Problem blending ' + wrapUpA + ' & ' + wrapUpB)
        wrapCount += 1

    # for f in os.listdir(destDir): # Comment out to keep all merges on disk
    #     if str(os.path.basename(f)) != '_Final.jpg':
    #         os.remove(destDir + '/' + f)
    print("took %s seconds" % (time.time() - start_time))
