import cv2
import os
import math
from os import listdir
from random import shuffle
from Tkinter import Tk
from tkFileDialog import askdirectory
import tkMessageBox
import time

start_time = time.time()
Tk().withdraw()
srcDir = askdirectory()
dstDir = srcDir + '/' + 'results'

try:
    os.mkdir(dstDir)
except OSError as e:
    if e.errno == 17:
        if tkMessageBox.askokcancel('Folder already exists', 'The output folder already exists, proceeding may overwrite the files it contains.'):
                pass
        else:
            print('Exiting ImageBlender')
            sys.exit(1)


#fileNamesList = [f for f in listdir(srcDir) if f.endswith('.JPG') or f.endswith('.jpg')]
fileNamesList = [srcDir + '/' + str(f) for f in listdir(srcDir) if f.endswith('.JPG') or f.endswith('.jpg')]
#leading zeros to pad file names for output ordering = ceiling of log base 10 of n+1
zeroPad = int(math.ceil(math.log(len(fileNamesList) + 1, 10))) + 1


#remList = [] #uncomment to enable file removal

'''
for f in fileNamesList:
    #fname = srcDir + '/' + str(f)
    imgNames.append(srcDir + '/' + str(f))
    #images.append(cv2.imread(fname, 1))
#shuffle(imgNames)
'''
alpha = .5

count = 0
while len(fileNamesList)>1:
    aname = fileNamesList.pop()
    bname = fileNamesList.pop()
    imga = cv2.imread(aname,1)
    imgb = cv2.imread(bname, 1)
    # RESIZE TO MORRIS RESOLUTION
    imga = cv2.resize(imga, (2592, 1944))
    imgb = cv2.resize(imgb, (2592, 1944))
    #RESIZE to arbitrary desktop resolution (stretch / skew etc.)
    #imga = cv2.resize(imga, (1920,1080))
    #imgb = cv2.resize(imgb, (1920,1080))
    #imga = cv2.resize(imga, (800, 1000))
    #imgb = cv2.resize(imgb, (800, 1000))
    outName = dstDir + '/' + 'merge_' + str(count).zfill(zeroPad) + '.jpg'
    #print ('merging ' + aname + ' and ' + bname + ' into ' + fname)
    imgc = cv2.addWeighted(imga, alpha, imgb, alpha, 0)
    del(imga)
    del(imgb)

    cv2.imwrite(outName,imgc)
    fileNamesList.insert(0, outName)
    #remList.append(outName)#uncomment to enable file removal
    #del(imgc)#uncomment to enable file removal
    count+=1

# To retain all merges, comment out below
#remList.pop()
#for in remList:
#    os.remove(r)
print("took %s seconds" % (time.time() - start_time))