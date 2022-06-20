# coding = 'utf-8
import os
import csv
import requests
from bs4 import BeautifulSoup
from selenium import webdriver


# APP类用于存放 (name, category ,detail_page, privacy_link)
class APP:
    def __init__(self, name: str, category: str, detail_page: str, privacy_link: str):
        self.name = name
        self.category = category
        self.detail_page = detail_page
        self.privacy_link = privacy_link
        self.state = 'success'


# 定义全局变量 WEBROOT为根目录
WEBROOT = "https://app.mi.com/category/"
APP_LIST = []

# 定义 selenium的 webdriver为 chromedriver并忽略系统代理
option = webdriver.ChromeOptions()
option.add_argument('headless')
option.add_argument('--ignore-ssl-error')
browser = webdriver.Chrome(options=option)


# 利用 requests库获取静态 html
def get_html_text(url):
    try:
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 6.1; Win64; x64) AppleWebKit/537.36 (XHTML, like Gecko) '
                          'Chrome/58.0.3029.110 Safari/537.36 '
        }
        r = requests.get(url, timeout=30, headers=headers)
        r.raise_for_status()
        r.encoding = 'utf-8'
        return r.text
    except:
        return "There are some errors when get the original page!"


# 利用selenium库模拟请求获取动态页面,用于获取category下的所有app_detail_page
def get_detail_page(url):
    app_tuple_list = []
    try:
        browser.get(url)
        soup = BeautifulSoup(browser.page_source, features='lxml')
    except requests.HTTPError:
        return "There are some errors when get the download page!"
    all_app_tag = soup.find('ul', {"class": "applist", "id": "all-applist"})
    app_tag = all_app_tag.next
    app_tag_list = []
    while app_tag:
        app_tag_list.append(app_tag)
        app_tag = app_tag.nextSibling
    for app_tag in app_tag_list:
        name = app_tag.text[:-4]
        category = app_tag.text[-4:]
        detail_page = app_tag.next.attrs['href']
        app_tuple = (name, category, detail_page)
        app_tuple_list.append(app_tuple)
    return app_tuple_list


# 从 category获取 detail_page,再到 detail_page中获取 privacy_policy_link
def get_privacy_link(url):
    app_tuple_list = get_detail_page(url)
    for app_tuple in app_tuple_list:
        name = app_tuple[0]
        category = app_tuple[1]
        detail_page = app_tuple[2]
        soup = BeautifulSoup(get_html_text("https://app.mi.com/" + detail_page), 'html.parser')
        # print(soup)
        tag = soup.find('a', {"style": "color: #707070;"})
        try:
            privacy_link = tag.get('href')
            temp = APP(name, category, detail_page, privacy_link)
            APP_LIST.append(temp)
            print("Successfully append: ({}, {}, {}, {})".format(name, category, detail_page, privacy_link))
        except AttributeError:
            pass
    return None


# 将所有APP_LIST中的 (name, category ,detail_page, privacy_link)对写入csv
def write_csv():
    path = os.getcwd() + "/app_list/" + APP_LIST[0].category + ".csv"
    file = open(path, 'w', newline='', encoding='gbk')
    writer = csv.writer(file)
    writer.writerow(('ApplicationName', 'Category', 'DetailPage', 'PrivacyPolicyLink'))
    for app in APP_LIST:
        writer.writerow((app.name, app.category, app.detail_page, app.privacy_link))
    print("AppList has been written successfully!")
    file.close()


def app_spider_run():
    # 获取小米应用市场中 14类 APP的 detail page和 privacy policy url并写入csv
    for i in range(1, 15):  # https://app.mi.com/category/{1~29}#page={0~2}
        APP_LIST = []
        for j in range(3):
            get_privacy_link(WEBROOT + str(i) + '#page=' + str(j))
        write_csv()


def get_privacy_text():
    # 从 csv读取 privacy link并获取 html写入 txt中
    csv_root = os.getcwd() + "/app_list"
    for root, dirs, files in os.walk(csv_root, topdown=False):
        for name in files:
            path = os.path.join(root, name)
            file = open(path, 'r', encoding='gbk')
            reader = csv.reader(file)
            for row in reader:
                if row[0] == 'ApplicationName':  # 过滤表头
                    pass
                else:
                    name = row[0]
                    category = row[1]
                    package = row[2][12:]
                    privacy_link = row[3]
                    html_text = get_html_text(privacy_link)
                    soup = BeautifulSoup(html_text, 'html.parser')
                    policy = soup.text
                    state = write_txt(category, package, policy)
                    write_state_csv(name, category, package, privacy_link, state)


# 将 privacy policy text写入单个 txt文件
def write_txt(category, package_name, privacy_text):
    root = os.getcwd() + "/privacy_policy/" + category + "/"
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


def write_state_csv(name, category, package, privacy_link, state):
    path = os.getcwd() + "/privacy_policy/" + category + "/" + category + ".csv"
    file = open(path, 'a', newline='', encoding='gbk')
    writer = csv.writer(file)
    if os.path.getsize(path) == 0:
        writer.writerow(('ApplicationName', 'Category', 'DetailPage', 'PrivacyPolicyLink', 'State'))
    writer.writerow((name, category, package, privacy_link, state))
    print("Privacy Policy State has been successfully written!")
    file.close()


if __name__ == '__main__':

    app_spider_run()

    # Result example
    # Successfully append: (怡禾, 医疗健康, / details?id=com.yaeherhealth.app, https: // www.yaeyatech.com / private-protocol.html)
    # Successfully append: (小鹿中医 - 养生调理, 医疗健康, / details?id=com.xiaolu.patient, https: // s.xiaoluyy.com / xiaoluyyapp / agreement / legal.html)
    # Successfully append: (上海助医, 医疗健康, / details?id=com.lihuan.zhuyi, https: // shzy.91985.com / zhuyistaticpage / privacy.html)
    # Successfully append: (基因宝, 医疗健康, / details?id=com.laso.lasogene, https: // static.genebox.cn / static / privacy.html)

    get_privacy_text()

    # Result example
    # if policy.txt already exists
        # C:\Users\Rainbow\Desktop\Privacy Policy Violations\Coding\Spider_for_Miapp/privacy_policy/体育运动/com.magic.ball.sport.txtalready exists!
        # Privacy Policy State has been successfully written!
        # C:\Users\Rainbow\Desktop\Privacy Policy Violations\Coding\Spider_for_Miapp/privacy_policy/体育运动/com.ttzcy.caiyun.txtalready exists!
        # Privacy Policy State has been successfully written!
    # if policy.txt not exists (only error messages are displayed)
        # GBK Encoding Error happens in com.gooooal.app.events
        # ......Continue trying to decode with UTF8 ......
        # Successfully decode with UTF8
        # GBK Encoding Error happens in a.com.happy.step
        # ......Continue trying to decode with UTF8 ......
        # Successfully decode with UTF8









