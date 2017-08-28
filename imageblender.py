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
#from PIL import Image,ImageEnhance


start_time = time.time()


def blend(proc, q, fnListSlice, dstDir, zeroPad):
    #print("length is " + str(len(fnListSlice)))
    remList = []
    alpha = .5
    count = 0
    while len(fnListSlice) > 1:
        aname = fnListSlice.pop()
        bname = fnListSlice.pop()
        imga = cv2.imread(aname, 1)
        imgb = cv2.imread(bname, 1)
        imga = cv2.resize(imga, (2592, 1944))
        imgb = cv2.resize(imgb, (2592, 1944))
        outName = dstDir + '/' + 'merge_' + proc + '_' + str(count).zfill(zeroPad) + '.jpg'
        # print('merging ' + aname + ' and ' + bname + ' into ' + outName)
        imgc = cv2.addWeighted(imga, alpha, imgb, alpha, 0)
        del (imga)
        del (imgb)
        cv2.imwrite(outName, imgc)
        fnListSlice.insert(0, outName)
        remList.append(outName)  # uncomment to enable file removal
        del (imgc)
        count += 1
    # fileNamesList.append(outName)
    q.put(outName)

    # To retain all merges, comment out below
    # for f in remList:
    # print(f)
    # for g in fileNamesList:
    # print(g)
    # remList.pop()
    # for r in remList:
    # os.remove(r)


if __name__ == "__main__":

    Tk().withdraw()

    srcDir = askdirectory()
    global dstDir
    dstDir = srcDir + '/' + 'results'
    collectAll = 'C:/_pythonDev/blending/finishedBlends/' + srcDir.split('/')[-1] + '.jpg'
    #print(collectAll)

    #folders = filter(os.path.isdir, [os.path.join(srcDir, f) for f in os.listdir(srcDir)])
    #for f in folders:
#        print(f)

    try:
        os.mkdir(dstDir)
    except OSError as e:
        if e.errno == 17:
            if tkMessageBox.askokcancel('Folder already exists',
                                        'The output folder already exists, proceeding may overwrite the files it contains.'):
                pass
            else:
                print('Exiting ImageBlender')
                sys.exit(1)

    global fileNamesList
    fileNamesList = [srcDir + '/' + str(f) for f in listdir(srcDir) if f.endswith('.JPG') or f.endswith('.jpg')]
    shuffle(fileNamesList)
    # leading zeros to pad file names for output ordering = ceiling of log base 10 of n+1
    global zeroPad
    zeroPad = int(math.ceil(math.log(len(fileNamesList) + 1, 10))) + 1
    # print(len(fileNamesList)/4)


    q = Queue()

    n = len(fileNamesList)
    mark1 = n / 8
    mark2 = n / 4
    mark3 = 3*mark1
    mark4 = n / 2
    mark5 = 5*mark1
    mark6 = 3*mark2
    mark7 = 7*mark1

    p1 = Process(target=blend, args=('p1', q, fileNamesList[0:mark1], dstDir, zeroPad))
    p2 = Process(target=blend, args=('p2', q, fileNamesList[mark1:mark2], dstDir, zeroPad))
    p3 = Process(target=blend, args=('p3', q, fileNamesList[mark2:mark3], dstDir, zeroPad))
    p4 = Process(target=blend, args=('p4', q, fileNamesList[mark3:mark4], dstDir, zeroPad))
    p5 = Process(target=blend, args=('p5', q, fileNamesList[mark4:mark5], dstDir, zeroPad))
    p6 = Process(target=blend, args=('p6', q, fileNamesList[mark5:mark6], dstDir, zeroPad))
    p7 = Process(target=blend, args=('p7', q, fileNamesList[mark6:mark7], dstDir, zeroPad))
    p8 = Process(target=blend, args=('p8', q, fileNamesList[mark7:n], dstDir, zeroPad))

    p1.start()
    p2.start()
    p3.start()
    p4.start()
    p5.start()
    p6.start()
    p7.start()
    p8.start()

    p1.join()
    p2.join()
    p3.join()
    p4.join()
    p5.join()
    p6.join()
    p7.join()
    p8.join()


    count = 1
    while q.qsize() > 1:
        imga = cv2.imread(q.get(), 1)
        imgb = cv2.imread(q.get(), 1)
        imga = cv2.resize(imga, (2592, 1944))
        imgb = cv2.resize(imgb, (2592, 1944))
        if count == 7:
            outName = dstDir + '/' + 'FinalMerge.jpg'
        else:
            outName = dstDir + '/' + 'penultimate_' + str(count) + '.jpg'
        #print('merging into ' + outName)
        imgc = cv2.addWeighted(imga, .5, imgb, .5, 0)
        cv2.imwrite(outName, imgc)
        q.put(outName)
        count += 1
    cv2.imwrite(collectAll,imgc)
    #print("took %s seconds" % (time.time() - start_time))
'''
    img_yuv = cv2.imread(q.get())
    img_yuv = cv2.cvtColor(imgc, cv2.COLOR_BGR2YUV)

    # equalize the histogram of the Y channel
    img_yuv[:, :, 0] = cv2.equalizeHist(img_yuv[:, :, 0])
    #clahe = cv2.createCLAHE(clipLimit=2.0, tileGridSize=(8, 8))
    #img_yuv[:, :, 0] = clahe.apply(img_yuv[:, :, 0])


    # convert the YUV image back to RGB format
    img_output = cv2.cvtColor(img_yuv, cv2.COLOR_YUV2BGR)

    ccname = dstDir + '/' + 'FinalMergeEH.jpg'
    #ccname = dstDir + '/' + 'FinalMergeClahe.jpg'
    enhName = dstDir + '/' + 'FinalMergeClahe+ColorEn'
    enhName = dstDir + '/' + 'FinalMergeEH+ColorEn'


    cv2.imwrite(ccname, img_output)
    imgEnh = Image.open(ccname)
    enhancer = ImageEnhance.Color(imgEnh)
    enhancer.enhance(1.00).save(enhName + '100.jpg')
    enhancer.enhance(1.25).save(enhName + '125.jpg')
    enhancer.enhance(1.50).save(enhName + '150.jpg')
    enhancer.enhance(1.75).save(enhName + '175.jpg')
    enhancer.enhance(2.00).save(enhName + '200.jpg')
'''


'''
    p1 = Process(target=blend, args=('p1', q, fileNamesList[0:(len(fileNamesList) / 4)], dstDir, zeroPad))
    p2 = Process(target=blend,
                 args=('p2', q, fileNamesList[(len(fileNamesList) / 4): (len(fileNamesList) / 2)], dstDir, zeroPad))
    p3 = Process(target=blend,
                 args=('p3', q, fileNamesList[(len(fileNamesList) / 2): 3 * (len(fileNamesList) / 4)], dstDir, zeroPad))
    p4 = Process(target=blend,
                 args=('p4', q, fileNamesList[(3 * (len(fileNamesList) / 4)):len(fileNamesList)], dstDir, zeroPad))
'''