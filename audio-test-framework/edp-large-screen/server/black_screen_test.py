import logging
from logging import handlers
import sys
import cv2
from ultralytics import YOLO
import os
import time

current_working_dir = os.path.dirname(os.path.realpath(sys.argv[0]))
log_path = os.path.join(current_working_dir, 'logs')
image_path = os.path.join(log_path, 'image_path')

def get_logger(log_filename, level=logging.INFO, when='D', back_count=0):
    """
    :brief  日志记录
    :param log_filename: 日志名称
    :param level: 日志等级
    :param when: 间隔时间:
        S:秒
        M:分
        H:小时
        D:天
        W:每星期（interval==0时代表星期一）
        midnight: 每天凌晨
    :param back_count: 备份文件的个数，若超过该值，就会自动删除
    :return: logger
    """
    # 创建一个日志器。提供了应用程序接口
    logger = logging.getLogger(log_filename)
    # 设置日志输出的最低等级,低于当前等级则会被忽略
    logger.setLevel(level)
    # 创建日志输出路径
    log_path = os.path.join(LOG_ROOT, "logs")
    if not os.path.exists(log_path):
        os.mkdir(log_path)
    log_file_path = os.path.join(log_path, log_filename)
    # 创建格式器
    formatter = logging.Formatter('%(asctime)s - %(pathname)s[line:%(lineno)d] - %(levelname)s: %(message)s')
    # 创建处理器：ch为控制台处理器，fh为文件处理器
    ch = logging.StreamHandler()
    ch.setLevel(level)
    # 输出到文件
    fh = logging.handlers.TimedRotatingFileHandler(
        filename=log_file_path,
        when=when,
        backupCount=back_count,
        encoding='utf-8')
    fh.setLevel(level)
    # 设置日志输出格式
    fh.setFormatter(formatter)
    ch.setFormatter(formatter)
    # 将处理器，添加至日志器中
    logger.addHandler(fh)
    logger.addHandler(ch)

    return logger


dirname, filename = os.path.split(os.path.abspath(sys.argv[0]))
LOG_ROOT = dirname
logger = get_logger(f'black_test.log')

def save_image(dst):
    timestamp = time.strftime("%m%d%H%M%S", time.localtime())
    filename = f"screen_fail_{timestamp}.jpg"  # 设定文件名，num为帧编号
    save_path = os.path.join(image_path, filename)  # 'path_to_big_screen_directory' 替换为大屏的文件保存路径
    cv2.imwrite(save_path, dst)

def check_black():
    # 加载USB摄像头
    cap = cv2.VideoCapture(1, cv2.CAP_DSHOW)
    # Create output
    num = 0
    # 循环视频流
    while cap.isOpened():
        success, frame = cap.read()
        if success:
            # 对视频帧进行处理
            dst = cv2.resize(frame, [1920, 1080])
            results = model(dst)
            boxes = results[0].boxes
            num += 1
            if num % 10 != 0:
                continue
            if len(boxes) == 0:
                logger.info("未检测到云屏\n")
                save_image(dst)
                continue
            cls = boxes.cls[0]
            if cls == 0:
                save_image(dst)
                logger.info("测试出现黑屏\n")
            elif cls == 1:
                logger.info("未出现黑屏")
            real_num = int(num/10)
            logger.info(f"第{real_num}次测试\n")
        else:
            break
    # 释放VideoCapture对象并关闭显示窗口
    cap.release()
    cv2.destroyAllWindows()

if __name__ == '__main__':
    # 加载YOLO模型
    model = YOLO("model/best.pt")
    check_black()


