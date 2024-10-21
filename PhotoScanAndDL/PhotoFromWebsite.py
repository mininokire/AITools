import requests
from bs4 import BeautifulSoup
from urllib.parse import urljoin
import os
import re
import concurrent.futures
from tqdm import tqdm
import psutil
import configparser

session = requests.Session()

# 根据网页内容生成恰当的文件夹名
def generate_folder_name(page_url):
    response = session.get(page_url)
    response.raise_for_status()
    soup = BeautifulSoup(response.content, "html.parser")
    title = soup.title.string if soup.title else page_url.split("/")[-1]
    return re.sub(r'[<>:"/\\|?*]', '_', title)

# 过滤掉文件名中的无效字符
def sanitize_filename(filename):
    return re.sub(r'[<>:"/\\|?*]', '_', filename)

def download_image(image_url, folder):
    retries = 3
    for _ in range(retries):
        try:
            response = session.get(image_url)
            if response.status_code == 200:
                content_type = response.headers.get("Content-Type")
                if content_type.startswith("image/jpeg") or content_type.startswith("image/jpg"):
                    extension = ".jpg"
                elif content_type.startswith("image/png"):
                    extension = ".png"
                elif content_type.startswith("image/gif"):
                    extension = ".gif"
                else:
                    extension = ""
                if extension:
                    image_name = sanitize_filename(image_url.split("/")[-1])
                    if not image_name.endswith(extension):
                        image_name += extension
                    image_path = os.path.join(folder, image_name)
                    with open(image_path, "wb") as file:
                        file.write(response.content)
                    # print(f"Downloaded: {image_path}")
                    return True
                else:
                    print(f"Unsupported image format for {image_url}")
                    return False
            else:
                print(f"Failed to download {image_url}. Status code: {response.status_code}")
                return False
        except Exception as e:
            print(f"Error downloading image {image_url}, retrying...: {type(e).__name__}: {e}")
    print(f"Failed to download {image_url} after {retries} retries.")
    return False

def scrape_images(page_url):
    try:
        response = session.get(page_url, timeout=5)
        response.raise_for_status()
        soup = BeautifulSoup(response.content, "html.parser")
        
        img_tags = soup.find_all("img")
        folder_name = generate_folder_name(page_url)

        # 从配置文件读取文件夹前缀
        config = configparser.ConfigParser()
        config.read('config.ini')
        folder_prefix = config['DEFAULT']['folder_prefix']
        output_folder = "folder\\" + folder_prefix + "\\" + folder_name
        if not os.path.exists(output_folder):
            os.makedirs(output_folder)

        total_images = len(img_tags)
        downloaded_images = 0

        # 从配置文件读取目标 CPU 使用率
        target_cpu_usage = float(config['DEFAULT']['target_cpu_usage'])

        # 获取 CPU 核心数
        num_cores = psutil.cpu_count(logical=True)
        # 根据核心数和期望的 CPU 占用率计算最大工作线程数
        max_workers = int(num_cores * target_cpu_usage)

        with concurrent.futures.ProcessPoolExecutor(max_workers=max_workers) as executor:
            futures = [executor.submit(download_image, urljoin(page_url, img.get("src")), output_folder) for img in img_tags if img.get("src")]
            with tqdm(total=total_images, desc=f"Downloading images for {page_url}") as pbar:
                for future in concurrent.futures.as_completed(futures):
                    try:
                        if future.result():
                            downloaded_images += 1
                            pbar.update(1)
                    except Exception as e:
                        print(f"Error processing image download: {e}")
    except requests.exceptions.RequestException as e:
        print(f"Error accessing the page: {e}")

if __name__ == "__main__":
    with open('links.txt', 'r') as file:
        links = [line.strip() for line in file.readlines()]
    unique_links = list(set(links))
    with concurrent.futures.ProcessPoolExecutor() as executor:
        futures = [executor.submit(scrape_images, link) for link in unique_links]
        for future in concurrent.futures.as_completed(futures):
            try:
                future.result()
            except Exception as e:
                print(f"Error processing page scrape: {e}")
