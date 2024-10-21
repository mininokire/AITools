import requests
from bs4 import BeautifulSoup

def find_all_links(url):
    try:
        response = requests.get(url)
        response.raise_for_status()
        soup = BeautifulSoup(response.content, 'html.parser')
        links = [link.get('href') for link in soup.find_all('a') if link.get('href') is not None]
        return links
    except requests.exceptions.RequestException as e:
        print(f"Error accessing the page: {e}")
        return []

# 获取用户输入的多个网址，以空格分隔
urls = input("请输入要查找链接的网址（多个网址以空格分隔）：").split()
all_links = []

for url in urls:
    links = find_all_links(url)
    all_links.extend(links)

# 对链接进行排序
sorted_links = sorted(all_links)

# 将链接保存到 txt 文件中，覆盖已有文件
with open('linksTemp.txt', 'w') as file:
    for link in sorted_links:
        file.write(link + '\n')

print("链接已保存到 linksTemp.txt 文件中，如有重复保存会进行覆盖。")