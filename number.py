#代码复制自BiliBili ：好家伙VCC
#仅用于学习

import sensor, image, time, os, ml, math, uos, gc
import numpy as np # 导入 ulab 模块的 numpy 以支持数组计算
# ------------------ 摄像头初始化配置 -------------------
sensor.reset() # 复位摄像头，使其进入默认状态
sensor.set_pixformat(sensor.RGB565) # 设置图像格式为 RGB565（每个像素 16 位，5-6-5 格式）
sensor.set_framesize(sensor.QVGA) # 设置帧尺寸为 QVGA（320x240 像素）
sensor.set_windowing((240, 240)) # 设置窗口大小为 240x240，确保 FOMO 兼容性
# **************** 摄像头镜像设置（根据物理安装方式调整）****************
sensor.set_vflip(True) # 垂直翻转（适用于摄像头倒装的情况）
sensor.set_hmirror(True) # 水平镜像（如果需要镜像翻转，则启用）
# ***********************************************************
sensor.skip_frames(time=2000) # 跳过 2 秒的帧，以确保摄像头稳定
# ------------------ 模型和标签初始化 -------------------
net = None # 初始化模型变量，稍后加载
labels = None # 初始化标签变量
min_confidence = 0.5 # 设定最小置信度阈值（0.5 即 50% 以上才认为是有效目标）
try:
    net = ml.Model("trained.tflite",
    load_to_fb=uos.stat('trained.tflite')[6] > (gc.mem_free() -(64*1024)))
# 加载 Edge Impulse 训练的 tflite 模型
# load_to_fb: 判断模型大小是否超出可用内存（留出 64KB 作为余量）
except Exception as e:
    raise Exception('模型加载失败: ' + str(e)) # 若加载失败，则抛出异常
try:
    with open("labels.txt", "r") as f:
        labels = [line.rstrip('\n') for line in f] # 读取标签文件，并去掉换行符
    print("Loaded Labels:", labels) # 打印加载的标签列表
except Exception as e:
    raise Exception('标签加载失败: ' + str(e)) # 若加载失败，则抛出异常
# ------------------ 可视化配置 -------------------
colors = [
(255, 0, 0), # 红
(0, 255, 0), # 绿
(255, 255, 0), # 黄
(0, 0, 255), # 蓝
(255, 0, 255), # 紫
(0, 255, 255), # 青
(255, 128, 0), # 橙
(128, 0, 255), # 紫红
(0, 128, 255), # 天蓝
(255, 255, 255) # 白
] # 预定义 10 种颜色用于不同类别的目标显示
# ------------------ 后处理函数 -------------------
def fomo_post_process(model, inputs, outputs):
    """
    处理 FOMO 模型的输出，将特征图转换为目标检测结果。
    """
    ob, oh, ow, oc = model.output_shape[0] # 获取输出特征图的形状（批量、行、列、通道数）
    x_scale = inputs[0].roi[2] / ow # 计算 x 方向的缩放比例
    y_scale = inputs[0].roi[3] / oh # 计算 y 方向的缩放比例
    scale = min(x_scale, y_scale) # 选择最小缩放比例，保证等比例缩放
    x_offset = ((inputs[0].roi[2] - (ow * scale)) / 2) + inputs[0].roi[0] # 计算x 方向偏移量
    y_offset = ((inputs[0].roi[3] - (ow * scale)) / 2) + inputs[0].roi[1] # 计算y 方向偏移量
    detection_lists = [[] for _ in range(oc)] # 初始化类别检测结果列表
    for channel in range(oc):
        channel_img = image.Image(outputs[0][0, :, :, channel] * 255) # 归一化后的特征图转换为灰度图
        blobs = channel_img.find_blobs(
        [(math.ceil(min_confidence * 255), 255)],
        x_stride=1, y_stride=1, area_threshold=1, pixels_threshold=1) # 在灰度图中查找高于置信度阈值的区域
        for blob in blobs:
            x, y, w, h = blob.rect() # 获取目标的边界框
            score = channel_img.get_statistics(
                thresholds=[(math.ceil(min_confidence * 255), 255)],
                roi=blob.rect()
            ).l_mean() / 255.0 # 计算该区域的平均亮度，作为置信度分数
            detection_lists[channel].append((
            int((x * scale) + x_offset),
            int((y * scale) + y_offset),
            int(w * scale),
            int(h * scale),
            score
        )) # 记录目标信息
    return detection_lists
# ------------------ 主循环 -------------------
clock = time.clock() # 创建时钟对象，用于计算 FPS
while True:
    clock.tick() # 记录帧开始时间
    img = sensor.snapshot() # 获取当前帧图像
    try:
        predictions = net.predict([img], callback=fomo_post_process) # 进行模型推理并调用后处理
    except Exception as e:
        print("Predict Error:", e) # 预测失败时打印错误信息
        continue
    total_detections = 0 # 本帧检测到的目标总数
    for class_id, detection_list in enumerate(predictions):
        if class_id == 0 or class_id >= len(labels) or class_id < 0:
            continue # 跳过背景类（class_id = 0）或无效类别索引
        if not detection_list:
            continue # 跳过没有检测到目标的类别
        class_name = labels[class_id] # 获取类别名称
        class_color = colors[(class_id-1) % len(colors)] # 选择对应颜色
        for x, y, w, h, score in detection_list:
            center_x = (x + w//2) # 计算中心点 x 坐标
            center_y = (y + h//2) # 计算中心点 y 坐标
            img.draw_circle(center_x,center_y,15,color=class_color,thickness=3) # 绘制中心点
            img.draw_rectangle(x, y, w, h, color=class_color, thickness=3) # 绘制边界框
            img.draw_string(x + 5, y + 5, "%s:%.2f" % (class_name, score),color=class_color, scale=5) # 绘制标签
            print("[Detect] Label:%s X:%d Y:%d Score:%.2f" % (class_name,center_x, center_y, score))
            total_detections += 1
    print("[Frame] FPS:%.1f Total:%d" % (clock.fps(), total_detections)) # 输出帧率和目标总数
    print("-" * 30) # 分隔符