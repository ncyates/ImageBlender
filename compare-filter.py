import multiprocessing
import os
import math
import time
import sys

import cv2
import skimage.measure
import Tkinter
import tkFileDialog
import tkMessageBox


def compareFilter(proc, chunk, acceptDir, rejectDir, stdDim):
    #TODO: test different image sizes / de-noising arguments to optimize performance / quality of similarity evaluation
    simThresh = .60
    optHeight = int(stdDim[0] * .25)
    optWidth = int(stdDim[1] * .25)
    while len(chunk) > 1:
        fileNameA = chunk.pop()
        fileNameB = chunk.pop()
        imageA = cv2.imread(fileNameA, 1)
        imageB = cv2.imread(fileNameB, 1)
        if imageA.shape != stdDim:
            imageA = cv2.resize(imageA, (stdDim[1], stdDim[0]))
        if imageB.shape != stdDim:
            imageB = cv2.resize(imageB, (stdDim[1], stdDim[0]))
        try:
            grayA = cv2.cvtColor(imageA, cv2.COLOR_BGR2GRAY)
            grayB = cv2.cvtColor(imageB, cv2.COLOR_BGR2GRAY)
            grayA = cv2.resize(grayA, (optWidth, optHeight))
            grayB = cv2.resize(grayB, (optWidth, optHeight))
            grayA = cv2.fastNlMeansDenoising(grayA, None, 6, 7, 21)
            grayB = cv2.fastNlMeansDenoising(grayB, None, 6, 7, 21)
            similarity = skimage.measure.compare_ssim(grayA,grayB)
            sys.stdout.write('\n' + proc + ' comparing ' + str(os.path.basename(fileNameA)) + ' & ' + str(os.path.basename(fileNameB)))
            sys.stdout.write('\n\tSimilarity is ' + str(similarity))
            # following code may not eliminate similar images if images are similar on end/start of consecutive chunks
            if similarity > simThresh:
                # writing to disk is for testing & verification purposes
                cv2.imwrite(rejectDir + '/' + os.path.basename(fileNameB), imageB)
                if len(chunk) > 0:
                    chunk.append(fileNameA)
                else:
                    cv2.imwrite(acceptDir + '/' + os.path.basename(fileNameA), imageA)
            else:
                cv2.imwrite(acceptDir + '/' + os.path.basename(fileNameA),imageA)
                if len(chunk) > 0:
                    chunk.append(fileNameB)
                else:
                    cv2.imwrite(acceptDir + '/' + os.path.basename(fileNameB),imageB)
        except ValueError:
            print('\tSKIPPING  ' + fileNameA + ' & ' + fileNameB + ' on ValueError')
            pass
        except cv2.error:
            print "Unexpected error:"
            pass


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
    #TODO: what about many different image dimensions? Possibly scan for all and set standard as most common dim

    numCores = multiprocessing.cpu_count()
    numFiles = len(fileNames)
    filesChunks = []
    chunkLength = numFiles / numCores
    zeroPad = int(math.ceil(math.log(chunkLength + 1, 10))) + 1  # of zeros to pad file names for output ordering
    chunkStart = 0
    chunkEnd = chunkStart + chunkLength
    partialChunk = numFiles % numCores

    for i in range(numCores):
        filesChunks.append(fileNames[chunkStart:chunkEnd])
        chunkStart = chunkEnd
        chunkEnd = chunkStart + chunkLength

    while partialChunk > 0:
        filesChunks[len(filesChunks) - 1].append(fileNames[(len(fileNames)) - partialChunk])
        partialChunk -= 1

    filteredFileNames = []
    compareProcesses = []
    acceptDir = destDir + '/' + 'accept'
    rejectDir = destDir + '/' + 'reject'
    try:
        os.mkdir(acceptDir)
        os.mkdir(rejectDir)
    except OSError as e:
        if e.errno == 17:
            if tkMessageBox.askokcancel('Folder already exists',
                                        'The output folder already exists, proceeding may overwrite the files it contains.'):
                pass
            else:
                print('Exiting ImageBlender')
                sys.exit(1)

    for i in range(len(filesChunks)):
        compareProcesses.append(multiprocessing.Process(target=compareFilter, args=(
        'p' + str(i), filesChunks[i], acceptDir, rejectDir, stdDim)))

    for i in range(len(compareProcesses)):
        compareProcesses[i].start()

    for i in range(len(compareProcesses)):
        compareProcesses[i].join()

    sys.stdout.write('\n\tFinished filtering in %s seconds' % (time.time() - start_time))