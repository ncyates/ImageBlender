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

start_time = time.time()


#def compare():
#    print("hi")



#if __name__ == "__main__":


Tk().withdraw()
srcDir = askdirectory()
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
zeroPad = int(math.ceil(math.log(len(fileNamesList) + 1, 10))) + 1


#remList = [] #uncomment to enable file removal


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

print("took %s seconds" % (time.time() - start_time))
# To retain all merges, comment out below
#remList.pop()
#for in remList:
#    os.remove(r)

