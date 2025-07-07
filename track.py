from image import threshold
import sensor
import time,image

minL=11
maxL=22
minA=33
maxA=44
minB=55
maxB=66

red=(minL,maxL,minA,maxA,minB,maxB)#红色阈值

def find_red(img,roi):
    blobs=img.find_blobs([red],roi)
    img.draw_rectangle(blobs.x,blobs.y,blobs.w,blobs.h)
    return blobs

def statistic_red(img,roi):
    counter=0
    blobs=img.find_blobs([red],roi)
    if blobs: return 1
    else: return 0