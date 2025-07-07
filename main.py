from image import RGB565
from machine import uart
from track import find_red
from track import statistic_red
import sensor
import time

flag=[0,0,0,0,0]
roi=[[1,2,3,4],[5,6,7,8],[9,10,11,12],[13,14,15,16],[17,18,19,20]]

sensor.reset()
sensor.set_pixformat(RGB565)
sensor.set_framesize(sensor.QVGA)
sensor.sensor.skip_frames(1000)#跳过不稳定部分
clock=time.clock()

while True:
    img=sensor.snapshot()


    #画区域
    blobs=find_red(img,[0,0,1000,1000])#roi值要改
    uart.write(blobs.w,blobs.h,blobs.cx,blobs.cy,blobs.rotation)
    #or
    for i in range (0,4):
        img.draw_rectangle(roi[i][0],roi[i][1],roi[i][1]-roi[i][0],roi[i][2]-roi[i][0])
        flag[i]=statistic_red(img,roi[i])
    uart.write(flag)
    #两者二择其一


    #number
    uart.write(blobs.w,blobs.h,blobs.cx,blobs.cy,blobs.rotation)
    #uart.write(number)