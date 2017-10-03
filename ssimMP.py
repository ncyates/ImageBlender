import cv2
import os
import math
from os import listdir
##from random import shuffle
from Tkinter import Tk
from tkFileDialog import askdirectory
import tkMessageBox
import time
from skimage.measure import compare_ssim as ssim
import multiprocessing
from multiprocessing import Process, Queue, Pool
import os
import sys

def compare(proc, goodQ, badQ, fnListSlice,dstDirSim,dstDirDif):
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








if __name__ == "__main__":

    start_time = time.time()

    Tk().withdraw()
    srcDir = askdirectory()


    # global dstDirSim
    # global dstDirDif
    dstDirSim = srcDir + '/' + 'resultsSim'
    dstDirDif = srcDir + '/' + 'resultsDif'

    try:
        os.mkdir(dstDirSim)
        os.mkdir(dstDirDif)
    except OSError as e:
        if e.errno == 17:
            if tkMessageBox.askokcancel('Folder already exists', 'The output folder already exists, proceeding may overwrite the files it contains.'):
                    pass
            else:
                print('Exiting ImageBlender')
                sys.exit(1)



    fileNamesList = [srcDir + '/' + str(f) for f in listdir(srcDir) if f.endswith('.JPG') or f.endswith('.jpg')]
    ##leading zeros to pad file names for output ordering = ceiling of log base 10 of n+1
    global zeroPad
    zeroPad = int(math.ceil(math.log(len(fileNamesList) + 1, 10))) + 1



    #q = Queue()
    procList = []
    numFiles = len(fileNamesList)
    numCores = multiprocessing.cpu_count()
    chunkLength = numFiles / numCores
    remFiles = numFiles % numCores
    chunkStart = 0
    chunkEnd = chunkStart + chunkLength
    segCount = 0
    goodQ = Queue()
    badQ = Queue()

    # make a list of evenly distributed lists of files, absorb overflow in last list
    chunkList = []
    for i in range(numCores):
        chunkList.append(fileNamesList[chunkStart:chunkEnd])
        chunkStart = chunkEnd
        chunkEnd = chunkStart + chunkLength
    while remFiles > 0:
        chunkList[len(chunkList)-1].append(fileNamesList[(len(fileNamesList))-remFiles])
        remFiles -=1

    '''
    # testing all files accounted for
        ccount = 0
        for chunk in chunkList:
            dcount = 0
            for c in chunk:
                print(str(os.path.basename(c)))
                ccount +=1
                dcount +=1
            print(dcount)
        print(ccount)
    '''


    # for chunk in chunkList:
    #     procList.append(Process(target = compare, args=(goodQ, badQ, chunk)))

    for i in range(len(chunkList)):
        procList.append(Process(target = compare, args=('p' + str(i), goodQ, badQ, chunkList[i],dstDirSim,dstDirDif)))

        #procList.append(Process(target=compare, args=('p' + str(i),fileNamesList[chunkStart:chunkEnd], dstDirSim,dstDirDif, zeroPad)))
        # chunkStart = chunkEnd
        # chunkEnd = chunkStart + chunkLength


    for i in range(len(procList)):
        procList[i].start()

    for i in range(len(procList)):
        procList[i].join()


    print('\ngood images which are different enough: ' + str(goodQ.qsize()))
    print('bad images which are not different enough: ' + str(badQ.qsize()))
    print("took %s seconds" % (time.time() - start_time))








'''
    for i in range(numCores):
        procList.append(Process(target=compare, args=('p' + str(i),fileNamesList[chunkStart:chunkEnd], dstDirSim,dstDirDif, zeroPad)))
        chunkStart = chunkEnd
        chunkEnd = chunkStart + chunkLength


    for i in range(numCores):
        procList[i].start()

    for i in range(numCores):
        procList[i].join()

    print("took %s seconds" % (time.time() - start_time) + '\n')
    for s in testlistSim:
        print(s)
    for d in testlistDif:
        print(d)

'''


'''    
    count = 0
    while len(fileNamesList)>1:
        imageAPath = fileNamesList.pop()
        imageBPath = fileNamesList.pop()
        print(str(imageAPath), str(imageBPath))
        imageA = cv2.imread(imageAPath, 1)
        imageB = cv2.imread(imageBPath, 1)
        try:
            # make grayscale images for faster de-noising and similarity comparisons, write color images out
            grayA = cv2.resize(imageA, (2592, 1944))
            grayB = cv2.resize(imageA, (2592, 1944))
    
            grayA = cv2.cvtColor(imageA, cv2.COLOR_BGR2GRAY)
            grayB = cv2.cvtColor(imageB, cv2.COLOR_BGR2GRAY)
    
            grayA = cv2.fastNlMeansDenoising(grayA,None,6,7,21)
            grayB = cv2.fastNlMeansDenoising(grayB, None, 6, 7, 21)
    
            imageSimilarity = ssim(grayA, grayB)
            print(imageSimilarity)
    
            imageA = cv2.resize(imageA, (2592, 1944))
            imageB = cv2.resize(imageB, (2592, 1944))
    
            if imageSimilarity > .55:
                print("\n\nSIMILAR")
    
                #outNameA = dstDirSim + '/' + str(count) + 'a.jpg'
                outNameB = dstDirSim + '/' + str(count) + 'b.jpg'
                #outGrayA = dstDirSim + '/' + str(count) + 'GRAYa.jpg'
                #outGrayB = dstDirSim + '/' + str(count) + 'GRAYb.jpg'
                #cv2.imwrite(outNameA, imageA)
                cv2.imwrite(outNameB, imageB)
                #cv2.imwrite(outGrayA, grayA)
                #cv2.imwrite(outGrayB, grayB)
                fileNamesList.append(imageAPath)
                count += 1
            else:
                outNameA = dstDirDif + '/' + str(count) + 'a.jpg'
                outNameB = dstDirDif + '/' + str(count) + 'b.jpg'
                cv2.imwrite(outNameA, imageA)
                cv2.imwrite(outNameB, imageB)
                count += 1
        #similar = ssim(imga,imgb,multichannel = True)
        except ValueError:
            print('\tSKIPPING  ' + imageAPath + ' & ' + imageBPath + 'on ValueError')
            pass
        except cv2.error:
            print "Unexpected error:"
            pass
    '''

# To retain all merges, comment out below
#remList.pop()
#for in remList:
#    os.remove(r)

