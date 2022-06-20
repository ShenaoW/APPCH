# coding = 'utf-8
import os
import csv
import re

import requests
from bs4 import BeautifulSoup
from selenium import webdriver


# APP类用于存放 (name, category ,detail_page, privacy_link)
class APP:
    def __init__(self, name: str, package_name: str, soft_id: str, download_link: str, privacy_link: str):
        self.name = name
        self.package_name = package_name
        self.soft_id = soft_id
        self.download_link = download_link
        self.privacy_link = privacy_link


# 定义全局变量 WEBROOT为根目录
WEBROOT = "http://zhushou.360.cn/list/index/cid/1/order/newest/"


# 利用 requests库获取静态 html
def get_html_text(url):
    try:
        proxies = {"http": None, "https": None}

        headers = {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) '
                              'Chrome/102.0.5005.63 Safari/537.36 '
            }
        r = requests.get(url, timeout=30, headers=headers, proxies=proxies)
        r.raise_for_status()
        r.encoding = 'utf-8'
        return r.text
    except:
        return "There are some errors when get the original page!"


# 利用selenium库模拟请求获取动态页面,用于获取category下的所有app_detail_page
def html_parser(url):
    app_list = []

    try:
        browser.get(url)
        soup = BeautifulSoup(browser.page_source, features='lxml')
    except requests.HTTPError:
        return "There are some errors when get the download page!"

    tags = soup.find_all('a', sid=True, class_=re.compile('dbtn.*normal'))

    for tag in tags:
        href = tag['href']
        att = href.split('&')

        name = att[3][5:]
        soft_id = att[-3][7:]
        download_url = att[-1][4:]
        package_name = re.match('.*\.apk\?', download_url).group().split('/')[-1].split('_')[0]
        privacy_link = get_privacy_link(package_name)

        app = APP(name=name,
                  package_name=package_name,
                  soft_id=soft_id,
                  download_link=download_url,
                  privacy_link=privacy_link)
        print(app.name, app.package_name, app.soft_id, app.download_link, app.privacy_link)

        app_list.append(app)

    return app_list


def get_privacy_link(package_name: str):
    detail_page = 'https://app.mi.com/details?id=' + package_name + '&ref=search'

    # soup = BeautifulSoup(get_html_text(detail_page), 'html.parser')
    try:
        browser.get(detail_page)
        soup = BeautifulSoup(browser.page_source, features='lxml')
    except requests.HTTPError:
        return "There are some errors when get the download page!"

    tag = soup.find('a', {"style": "color: #707070;"})

    try:
        privacy_link = tag.get('href')
        return privacy_link

    except AttributeError:
        return None


def write_csv(app_list):
    path = os.getcwd() + "/applist.csv"
    file = open(path, 'w', newline='', encoding='ANSI')
    writer = csv.writer(file)

    for app in app_list:
        try:
            writer.writerow((app.name, app.package_name, app.soft_id, app.download_link, app.privacy_link))
        except UnicodeEncodeError:
            pass

    print("AppList has been written successfully!")

    file.close()


def spider_run():
    app_list = []

    for i in range(10, 50):
        page = WEBROOT + "?page=" + str(i)
        app_list.extend(html_parser(page))

    write_csv(app_list)


# 获取隐私政策内容
def get_privacy_text():
    # 从 csv读取 privacy link并获取 html写入 txt中
    path = os.getcwd() + "/applist.csv"
    file = open(path, 'r', encoding='ANSI')
    reader = csv.reader(file)
    for row in reader:
        package_name = row[1]
        privacy_link = row[4]
        if privacy_link != 'None':
            html_text = get_html_text(privacy_link)
            soup = BeautifulSoup(html_text, 'html.parser')
            privacy_text = soup.text
            write_policy_text(package_name, privacy_text)


# 将 privacy policy text写入单个 txt文件
def write_policy_text(package_name, privacy_text):
    root = os.getcwd() + "/privacy_policy/"
    if os.path.exists(root):
        pass
    else:
        os.makedirs(root)

    path = root + package_name + '.txt'
    if os.path.exists(path):
        print(path + "already exists!")
        state = 'success'
        return state
    else:
        # 尝试 gbk解码写入txt
        try:
            file = open(path, 'w', newline='', encoding='gbk')
            file.write(privacy_text)
            file.close()
            state = 'success'
        except UnicodeEncodeError:
            print("\nGBK Encoding Error happens in " + package_name)
            print("......Continue trying to decode with UTF8 ......")
            # 若 UnicodeEncodeError,则尝试 utf-8解码写入
            try:
                file = open(path, 'w', newline='', encoding='utf-8')
                file.write(privacy_text)
                file.close()
                print("Successfully decode with UTF8")
                state = 'success'
            except UnicodeEncodeError:
                # 若仍然 UnicodeEncodeError,则删除 txt文件,并在 app.state中写入 error
                state = 'error'
                os.path.exists(path)
                os.remove(path)
                print("UTF8 Encoding Error happens in " + package_name)
                print("......Automatically deletes the privacy policy txt ......")
        return state


if __name__ == "__main__":
    # 定义 selenium的 webdriver为 chromedriver并忽略系统代理
    option = webdriver.ChromeOptions()
    option.add_argument('headless')
    option.add_argument('--ignore-ssl-error')
    browser = webdriver.Chrome(options=option)

    spider_run()
    get_privacy_text()

    browser.close()
