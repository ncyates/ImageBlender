import cv2
from multiprocessing import Process, Queue
import os
import math
from os import listdir
from Tkinter import Tk
from tkFileDialog import askdirectory
import tkMessageBox
from random import shuffle
import time


start_time = time.time()

def blend(proc,q,fnListSlice,dstDir,zeroPad):
    remList = []
    alpha = .5
    count = 0
    while len(fnListSlice)>1:
        aname = fnListSlice.pop()
        bname = fnListSlice.pop()
        imga = cv2.imread(aname, 1)
        imgb = cv2.imread(bname, 1)
        imga = cv2.resize(imga, (2592, 1944))
        imgb = cv2.resize(imgb, (2592, 1944))
        outName = dstDir + '/' + 'merge_' + proc + '_' + str(count).zfill(zeroPad) + '.jpg'
        #print('merging ' + aname + ' and ' + bname + ' into ' + outName)
        imgc = cv2.addWeighted(imga, alpha, imgb, alpha, 0)
        del (imga)
        del (imgb)
        cv2.imwrite(outName, imgc)
        fnListSlice.insert(0, outName)
        remList.append(outName)#uncomment to enable file removal
        del(imgc)
        count += 1
    #fileNamesList.append(outName)
    q.put(outName)

    # To retain all merges, comment out below
    #for f in remList:
        #print(f)
    #for g in fileNamesList:
        #print(g)
    #remList.pop()
    #for r in remList:
        #os.remove(r)

if __name__ == "__main__":

    Tk().withdraw()

    srcDir = askdirectory()
    global dstDir
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



    global fileNamesList
    fileNamesList = [srcDir + '/' + str(f) for f in listdir(srcDir) if f.endswith('.JPG') or f.endswith('.jpg')]
    shuffle(fileNamesList)
    #leading zeros to pad file names for output ordering = ceiling of log base 10 of n+1
    global zeroPad
    zeroPad = int(math.ceil(math.log(len(fileNamesList) + 1, 10))) + 1
    #print(len(fileNamesList)/4)


    q = Queue()

    p1 = Process(target = blend, args = ('p1', q, fileNamesList[0:(len(fileNamesList)/4)],dstDir,zeroPad))
    p2 = Process(target = blend, args = ('p2', q, fileNamesList[len(fileNamesList) / 4:(len(fileNamesList) / 2)-1], dstDir, zeroPad))
    p3 = Process(target = blend, args = ('p3', q, fileNamesList[len(fileNamesList) / 2:3*(len(fileNamesList) / 4)-1], dstDir, zeroPad))
    p4 = Process(target = blend, args = ('p4', q, fileNamesList[3*(len(fileNamesList) / 4)-1:len(fileNamesList)], dstDir, zeroPad))

    p1.start()
    p2.start()
    p3.start()
    p4.start()

    p1.join()
    p2.join()
    p3.join()
    p4.join()

    count = 1
    while q.qsize() > 1:
        imga = cv2.imread(q.get(), 1)
        imgb = cv2.imread(q.get(), 1)
        imga = cv2.resize(imga, (2592, 1944))
        imgb = cv2.resize(imgb, (2592, 1944))
        if count == 3:
            outName = dstDir + '/' + 'FinalMerge.jpg'
        else:
            outName = dstDir + '/' + 'penultimate_' + str(count) + '.jpg'
        print('merging into ' + outName)
        imgc = cv2.addWeighted(imga, .5, imgb, .5, 0)
        cv2.imwrite(outName, imgc)
        q.put(outName)
        count +=1

        print("took %s seconds" % (time.time() - start_time))