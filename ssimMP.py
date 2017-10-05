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

'''
def compareA(proc, goodQ, badQ, fnListSlice,dstDirSim,dstDirDif):
    #global testlistSim
    #global testlistDif
    imageWidth = int(2592 *.25)
    imageHeight = int(1944 * .25)
    #simLimit = .55
    simThresh = .60
    while len(fnListSlice) > 1:
        imageAPath = fnListSlice.pop()
        imageBPath = fnListSlice.pop()
        imageA = cv2.imread(imageAPath, 1)
        imageB = cv2.imread(imageBPath, 1)
        # sys.stdout.write('\n Processing ' + str(os.path.basename(imageAPath)) + ' & ' + str(os.path.basename(imageBPath)))
        try:
            # make grayscale images for faster de-noising and similarity comparisons, write color images out
            grayA = cv2.resize(imageA, (imageWidth, imageHeight))
            grayB = cv2.resize(imageB, (imageWidth, imageHeight))

            grayA = cv2.cvtColor(grayA, cv2.COLOR_BGR2GRAY)
            grayB = cv2.cvtColor(grayB, cv2.COLOR_BGR2GRAY)

            grayA = cv2.fastNlMeansDenoising(grayA, None, 6, 7, 21)
            grayB = cv2.fastNlMeansDenoising(grayB, None, 6, 7, 21)

            imageSimilarity = ssim(grayA, grayB)
            sys.stdout.write('\nProcess ' + proc + ' is processing ' + str(os.path.basename(imageAPath)) + ' & ' + str(os.path.basename(imageBPath)) + ' __ Similarity is ' + str(imageSimilarity))

            imageA = cv2.resize(imageA, (2592, 1944))
            imageB = cv2.resize(imageB, (2592, 1944))

            if imageSimilarity > simThresh:
                #sys.stdout.write('\n\t' + str(imageSimilarity) + '\nWriting ' + str(os.path.basename(imageAPath)) + 'to Dif')
                #outNameA = dstDirDif + '/' + proc + '_'+ os.path.basename(imageAPath)
                #outNameB = dstDirSim + '/' + proc + '_'+ os.path.basename(imageBPath)

                #cv2.imwrite(outNameA, imageA)

                # cv2.imwrite(outGrayA, grayA)
                # cv2.imwrite(outGrayB, grayB)
                badQ.put([os.path.basename(imageBPath)])
                cv2.imwrite(dstDirSim + '/' + proc + '_'+ os.path.basename(imageBPath), imageB)
                if(len(fnListSlice)>0):
                    fnListSlice.append(imageAPath)
                else:
                    goodQ.put([os.path.basename(imageAPath)])
                    cv2.imwrite(dstDirDif + '/' + proc + '_'+ os.path.basename(imageAPath),imageA)


            else:
                #outNameA = dstDirDif + '/' + proc + '_'+ os.path.basename(imageAPath)
                # testlistDif.append(outNameA)
                # outNameB = dstDirDif + '/' + proc + '_'+ os.path.basename(imageBPath)
                # testlistDif.append(outNameB)
                # cv2.imwrite(outNameA, imageA)
                # cv2.imwrite(outNameB, imageB)
                goodQ.put([os.path.basename(imageAPath)])
                cv2.imwrite(dstDirDif + '/' + proc + '_' + os.path.basename(imageAPath),imageA)
                if (len(fnListSlice) > 0):
                    fnListSlice.append(imageBPath)
                else:
                    goodQ.put([os.path.basename(imageBPath)])
                    cv2.imwrite(dstDirDif + '/' + proc + '_' + os.path.basename(imageBPath),imageB)
                #goodQ.put([os.path.basename(imageBPath)])

        # similar = ssim(imga,imgb,multichannel = True)
        except ValueError:
            print('\tSKIPPING  ' + imageAPath + ' & ' + imageBPath + ' on ValueError')
            pass
        except cv2.error:
            print "Unexpected error:"
            pass

'''


def compareFilter(proc, acceptQ, chunk, acceptDir, rejectDir, stdDim):
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
                #rejectQ.put(fileNameB)
                cv2.imwrite(rejectDir + '/' + os.path.basename(fileNameB), imageB)
                if len(chunk) > 0:
                    chunk.append(fileNameA)
                else:
                    #acceptQ.put([os.path.basename(fileNameA)])
                    cv2.imwrite(acceptDir + '/' + os.path.basename(fileNameA), imageA)
            else:
                #acceptQ.put([os.path.basename(fileNameA)])
                cv2.imwrite(acceptDir + '/' + os.path.basename(fileNameA),imageA)
                if len(chunk) > 0:
                    chunk.append(fileNameB)
                else:
                    #acceptQ.put([os.path.basename(fileNameB)])
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

    acceptQ = multiprocessing.Queue()
    rejectQ = multiprocessing.Queue()
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
        'p' + str(i), acceptQ, filesChunks[i], acceptDir, rejectDir, stdDim)))

    for i in range(len(compareProcesses)):
        compareProcesses[i].start()

    for i in range(len(compareProcesses)):
        compareProcesses[i].join()

    sys.stdout.write('\n\tFinished filtering in %s seconds' % (time.time() - start_time))

