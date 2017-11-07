'''
prototype utility to grab frames from videos and write to images using openCV -- needs cleanup, refactor, remove hard-coding
'''

import os
import sys
import math
import multiprocessing

import cv2
import Tkinter
import tkMessageBox
import tkFileDialog


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
        if cv2.waitKey(1) == 27:
            video.release()
            break

if __name__ == "__main__":
    Tkinter.Tk().withdraw()  # we don't want a full GUI, so keep the root window from appearing
    global filename
    filename = tkFileDialog.askopenfilename()  # show an "Open" dialog box and return the path to the selected file
    global outDir
    outDir = tkFileDialog.askdirectory() + '/' + os.path.basename(filename).split('.')[0]
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

    numFrames = video.get(cv2.CAP_PROP_FRAME_COUNT)
    video.release()
    numCores = multiprocessing.cpu_count()
    framesChunks = []
    chunkLength = numFrames / numCores
    chunkStart = 0
    chunkEnd = chunkStart + chunkLength
    partialChunk = numFrames % numCores

    for i in range(numCores):
        framesChunks.append(multiprocessing.Process(target=getFrames, args=(filename, outDir, chunkStart, chunkEnd)))
        chunkStart = chunkEnd
        chunkEnd = chunkStart + chunkLength

    if partialChunk > 0:
        framesChunks.append(multiprocessing.Process(target=getFrames, args=(filename, outDir, chunkStart, numFrames)))

    for i in range(len(framesChunks)):
        framesChunks[i].start()

    for i in range(len(framesChunks)):
        framesChunks[i].join()