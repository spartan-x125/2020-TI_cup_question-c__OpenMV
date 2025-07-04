from image import threshold
import sensor
import time

red=(11,22,33,44,55,66)#红色阈值

def find_red(img,roi):
    blobs=img.find_blobs([red],roi)
    img.draw_rectangle(blobs.x,blobs.y,blobs.w,blobs.h)
    return blobs

def tracking(img):
    roi1=[1,2,3,4]
    roi2=[2,3,4,5]
    roi3=[3,4,5,6]
    img.find_blobs([red],roi1)