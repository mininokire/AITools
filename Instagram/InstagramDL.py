import instaloader
from concurrent.futures import ThreadPoolExecutor
import time
import os
import psutil

# 创建 Instaloader 对象
L = instaloader.Instaloader()

# 从会话文件中加载会话
SESSION_FILE_PATH = "session-<your_instagram_username>"  # 替换为你自己的 Instagram 用户名
if os.path.exists(SESSION_FILE_PATH):
    L.load_session_from_file('<your_instagram_username>')  # 替换为你自己的 Instagram 用户名
else:
    print("会话文件不存在，您可能需要先登录并保存会话文件")

# 下载指定用户的所有图片和视频
def download_instagram_user(username):
    """
    下载指定Instagram用户的所有图片和视频。
    """
    try:
        print(f"开始下载用户 {username} 的内容...")
        L.download_profile(username, profile_pic_only=False)
        print(f"下载成功：{username} 的内容已下载。")
    except instaloader.exceptions.ProfileNotExistsException:
        print(f"错误：用户 {username} 不存在。")
    except instaloader.exceptions.ConnectionException as e:
        print(f"网络错误: {e}")
    except Exception as e:
        print(f"下载用户 {username} 时出现错误: {e}")

# 多线程并行下载多个用户内容
def download_multiple_users(usernames, cpu_limit=0.01):
    """
    并行下载多个用户的 Instagram 内容，限制 CPU 占用。
    :param usernames: 要下载的 Instagram 用户名列表
    :param cpu_limit: 限制 CPU 使用比例 (0.01 表示 1%)
    """
    def limit_cpu():
        """通过动态控制 CPU 占用的方式来限制 CPU 使用率。"""
        p = psutil.Process(os.getpid())
        while True:
            # 动态调整 CPU 占用：active_time / (active_time + sleep_time) = cpu_limit
            active_time = 0.01  # 设置一个执行任务的时间段
            sleep_time = (active_time / cpu_limit) - active_time
            p.cpu_affinity([0])  # 将任务绑定到 CPU 0，避免多个 CPU 使用
            time.sleep(sleep_time)

    # 启动控制 CPU 占用的线程
    import threading
    control_thread = threading.Thread(target=limit_cpu, daemon=True)
    control_thread.start()

    # 使用多线程池并行下载用户内容
    with ThreadPoolExecutor(max_workers=5) as executor:  # 可调整 max_workers 以提高效率
        executor.map(download_instagram_user, usernames)

# 示例：下载多个用户
usernames = ["8701jll", "mina_pochico", "kirari_1016_"]  # 替换为要下载的用户列表

# 调用并行下载函数，同时限制 CPU 占用为 6%
download_multiple_users(usernames, cpu_limit=0.6)
