import cv2  # 导入 OpenCV 库，用于处理计算机视觉和视频流相关的功能。

# 设置 RTSP 视频流的路径（用户名、密码、IP 地址和视频流的 URL）。
video_path = 'rtsp://admin:123456@192.168.3.101/Streaming/Channels/1'

# 使用 cv2.VideoCapture 打开 RTSP 视频流，cap 是一个视频捕获对象。
cap = cv2.VideoCapture(video_path)

# 设置视频流缓冲区的大小，减少延迟，CAP_PROP_BUFFERSIZE 设置为 3 表示缓冲区大小为 3 帧。
cap.set(cv2.CAP_PROP_BUFFERSIZE, 3)

# 检查视频流是否成功打开并且继续读取帧。cap.isOpened() 返回 True 表示视频流打开成功。
while cap.isOpened():
    # 读取视频流中的一帧。返回值 success 表示读取是否成功，frame 为读取到的图像帧。
    success, frame = cap.read()

    # 如果成功读取到帧，则显示该帧。
    if success:
        # 使用 OpenCV 显示读取到的视频帧，"SHOW" 为窗口名称，frame 为图像数据。
        cv2.imshow("SHOW", frame)
        
        # 等待 1 毫秒，检测按键。如果按下 'q' 键，则退出循环。
        if cv2.waitKey(1) &amp; 0xFF == ord("q"):
            break  # 按下 'q' 键退出循环，关闭视频流。



import ffmpeg  # 导入 ffmpeg 库，用于处理视频流（如 RTSP 流）。
import numpy as np  # 导入 NumPy 库，用于处理数据（如视频帧的数组操作）。
import cv2  # 导入 OpenCV 库，用于处理计算机视觉相关的功能（如显示视频）。

# 设置摄像头的 RTSP 流地址（用户名、密码、IP 地址和视频流的 URL）。
camera = 'rtsp://admin:123456@192.168.3.101/Streaming/Channels/1'

# 使用 ffmpeg.probe 函数探测摄像头的视频流信息，返回一个包含流信息的字典。
probe = ffmpeg.probe(camera)

# 从探测结果中找到视频流（选择 codec_type 为 'video' 的流）。
video_stream = next((stream for stream in probe['streams'] if stream['codec_type'] == 'video'), None)

# 获取视频流的宽度和高度，并将其转换为整数类型。
width = int(video_stream['width'])
height = int(video_stream['height'])

# 使用 ffmpeg 创建一个异步运行的命令，将视频流传输到管道中，并指定格式、像素格式、帧率等。
out = (
    ffmpeg
        .input(camera, rtsp_transport='tcp')  # 设置输入源为摄像头 RTSP 流，并指定使用 TCP 协议。
        .output('pipe:', format='rawvideo', pix_fmt='bgr24', loglevel="quiet", r=25)  # 输出到管道，指定原始视频格式，像素格式为 BGR24，帧率为 25 帧每秒。
        .run_async(pipe_stdout=True)  # 异步运行 ffmpeg，并将标准输出连接到管道。
)

# 初始化空帧计数器，检测视频流是否断开。
cnt_empty = 0

# 无限循环，持续读取视频流并处理每一帧。
while True:
    # 从管道读取一帧数据，每帧的大小为 height * width * 3（3 为每个像素的 RGB 通道）。
    in_bytes = out.stdout.read(height * width * 3)

    # 如果没有读取到数据（即视频流结束或出现错误），则增加空帧计数器。
    if not in_bytes:
        cnt_empty += 1
        # 如果连续 10 次没有数据，则认为视频流已结束，跳出循环。
        if cnt_empty > 10:
            break

    # 如果有数据，重置空帧计数器。
    cnt_empty = 0

    # 将读取到的字节数据转换为 NumPy 数组，并重新塑形为图像帧（height, width, 3 表示高、宽、RGB 三通道）。
    frame = np.frombuffer(in_bytes, dtype=np.uint8).reshape(height, width, 3)

    # 使用 OpenCV 显示视频帧（此时 frame 是图像数据）。
    cv2.imshow('test', frame)

    # 等待按键，如果按下 'q' 键则退出循环。
    if cv2.waitKey(1) &amp; 0xFF == ord('q'):
        break

# 释放资源（在程序退出时关闭 OpenCV 的窗口等资源）。
cv2.destroyAllWindows()
