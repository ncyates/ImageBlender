'''
prototype utility to grab frames from videos and write to images using openCV -- needs cleanup, refactor, remove hard-coding
'''
import cv2
import os
import sys
import math
import multiprocessing
import tkMessageBox
from os import listdir, mkdir
from Tkinter import Tk
from tkFileDialog import askopenfilename, askdirectory

#from timeit import default_timer as timer


def getFrames(filename, outDir, start, end):
    try:
        video = cv2.VideoCapture(filename)
    except:
        print('problem opening file')
        sys.exit(1)

    if not video.isOpened():
        print('file not opened')
        sys.exit(1)

    frameRate = int(math.ceil(video.get(cv2.CAP_PROP_FPS)))
    numFrames = video.get(cv2.CAP_PROP_FRAME_COUNT)
    success, image = video.read()  # get the first frame of the video
    video.set(cv2.CAP_PROP_POS_FRAMES,start)
    while success and video.get(cv2.CAP_PROP_POS_FRAMES) <= end:
        success, image = video.read()
        if int((video.get(cv2.CAP_PROP_POS_FRAMES)-1)) % frameRate == 0:
            outFilename = outDir + '/frame_' + str(int(video.get(cv2.CAP_PROP_POS_FRAMES))-1).zfill(6) + '.jpg'
            cv2.imwrite(outFilename, image)
        # exit if Escape is hit
        if cv2.waitKey(10) == 27:
            video.release()
            break


if __name__ == "__main__":
    Tk().withdraw()  # we don't want a full GUI, so keep the root window from appearing
    global filename
    filename = askopenfilename()  # show an "Open" dialog box and return the path to the selected file
    global outDir
    outDir = askdirectory() + '/' + os.path.basename(filename).split('.')[0]
    try:
        os.mkdir(outDir)
    except OSError as e:
        if e.errno == 17:
            if tkMessageBox.askokcancel('Folder already exists',
                                        'The output folder already exists, proceeding may overwrite the files it contains.'):
                pass
        else:
            print('Exiting FrameGrabber')
            sys.exit(1)

    try:
        video = cv2.VideoCapture(filename)
    except:
        print('problem opening file')
        sys.exit(1)

    if not video.isOpened():
        print('file not opened')
        sys.exit(1)

    #frameRate = int(math.ceil(video.get(cv2.CAP_PROP_FPS)))
    numFrames = video.get(cv2.CAP_PROP_FRAME_COUNT)
    video.release()


    p1 = multiprocessing.Process(target=getFrames, args=(filename, outDir, 0, numFrames/4))
    p2 = multiprocessing.Process(target=getFrames, args=(filename, outDir, numFrames/4, numFrames/2))
    p3 = multiprocessing.Process(target=getFrames, args=(filename, outDir, numFrames/2,(3*(numFrames/4))))
    p4 = multiprocessing.Process(target=getFrames, args=(filename, outDir, (3*(numFrames/4)),numFrames))

    p1.start()
    p2.start()
    p3.start()
    p4.start()

    p1.join()
    p2.join()
    p3.join()
    p4.join()


    #getFrames(0,numFrames/4)
    #getFrames(numFrames/4,numFrames/2)
    #getFrames(numFrames/2,(3*(numFrames/4)))
    #getFrames((3*(numFrames/4)),numFrames)
'''
success, image = video.read()  # get the first frame of the video
count = 0
#frame = image
while success:
    success, image = video.read()    
    if count % frameRate == 0:
        outfilename = outDir + '/frame_' + str(count).zfill(6) + '.jpg'
        cv2.imwrite(outfilename, image)
    # exit if Escape is hit
    if cv2.waitKey(10) == 27:
        video.release()
        break
    count += 1

'''