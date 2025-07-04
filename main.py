from image import RGB565
from machine import uart
from track import find_red
import sensor
import time

sensor.reset()
sensor.set_pixformat(RGB565)
sensor.set_framesize(sensor.QVGA)
sensor.sensor.skip_frames(1000)#跳过不稳定部分
clock=time.clock()

while True:
    img=sensor.snapshot()
    blobs=find_red(img,roi=[0,0,1000,1000])#roi值要改
    #number
    uart.write(blobs.w,blobs.h,blobs.cx,blobs.cy,blobs.rotation)
    #uart.write(number)