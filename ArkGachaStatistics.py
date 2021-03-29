from selenium import webdriver
from selenium.common.exceptions import NoSuchElementException
import json
import time
import os
import argparse
import matplotlib.pyplot as plt
import matplotlib.animation as ani
import matplotlib.gridspec as gs
rec = []
olddate = 0

parser = argparse.ArgumentParser(description='Arknights Gacha Statistics - 一个明日方舟抽卡统计工具', add_help= True)
parser.add_argument('-r', '--reset', action='store_true', help='清除历史记录.')
parser.add_argument('-s', '--skip-fetch', action='store_true', help='跳过从官网更新抽卡数据.')
parser.add_argument('--skip-draw', action='store_true', help='跳过画图.')
parser.add_argument('-e', '--export', action='store_true', help='直接从已有数据导出图片.')
args = parser.parse_args()

def fetch():
    #初始化浏览器
    chrome_options = webdriver.ChromeOptions()
    chrome_options.add_experimental_option('excludeSwitches', ['enable-logging'])
    chrome_options.add_argument('--disable-gpu')
    chrome_options.add_argument('--no-sandbox')
    browser = webdriver.Chrome(executable_path='chromedriver.exe', options=chrome_options)

    uid = ''
    while not uid:
        browser.get('https://ak.hypergryph.com/user/inquiryGacha')
        try:
            uid = browser.find_element_by_xpath('//*[@id="app"]/div/div/div[3]/div[2]/div[2]/div[1]/span[2]').text
            valid = browser.find_element_by_xpath('//*[@id="app"]/div/div/div[3]/div[2]/div[2]/div[1]/span[1]').text == 'UID'
            if (not valid):
                raise NoSuchElementException
        except NoSuchElementException:
            input('未登录！请手动登录后按回车继续')
    print('UID: %s' % uid)
    time.sleep(3)
    i = 1
    new_rec = []
    loop = True
    while loop:
        print('------------\nPage: %d' % i)
        lines = browser.find_elements_by_xpath('//*[@id="app"]/div/div/div[3]/div[2]/div[2]/div[2]/div/table/tbody/tr')
        for line in lines:
            date, chars_l = line.find_elements_by_xpath('.//td')
            chars = chars_l.find_elements_by_xpath('.//li')
            if (time.mktime(time.strptime(date.text, '%Y-%m-%d %H:%M:%S')) <= olddate):
                loop = False
                break
            print(date.text, end=': ')
            for char in chars:
                char_class = char.get_attribute('class')
                if ('rarity-3' in char_class):
                    rarity = 4
                elif ('rarity-4' in char_class):
                    rarity = 5
                elif ('rarity-5' in char_class):
                    rarity = 6
                else:
                    rarity = 3
                print('%d★%s' % (rarity, char.text), end=' ')
                new_rec.append({
                    'date': date.text,
                    'name': char.text,
                    'rarity': rarity
                })
            print()
        next_page = browser.find_element_by_xpath('//*[@id="app"]/div/div/div[3]/div[2]/div[2]/div[2]/ul/li[7]/a')
        if (next_page.get_attribute('aria-disabled') == 'true' or not loop):
            break
        i += 1
        next_page.click()
        time.sleep(3)
    browser.close()
    #写入log
    print('Dump json')
    rec.extend(reversed(new_rec))
    with open('logs/log.json', 'w', encoding='UTF-8') as f:
        f.write(json.dumps(rec, indent=2, separators=(',', ': '), ensure_ascii=False))
    print('Done')
    time.sleep(1)
    return None

def draw():
    print('Draw picture')
    # 统计数据
    total = len(rec)
    count = [0, 0, 0, 0]
    trend = [[0], [0], [0], [0]]
    tmp = [0, 0, 0, 0]
    for i in rec:
        index = i['rarity']-3
        count[index] += 1
        for j in range(4):
            trend[j].append(trend[j][-1]+1 if index ==  j else trend[j][-1])
    # 画图
    fig, axes = plt.subplots(
        2, 2,
        figsize = (16, 9),
        gridspec_kw = dict(height_ratios=[9, 7], width_ratios=[2, 1])
    )
    colors = ['lightgrey', 'cyan', 'yellow', 'orange']
    labels = ['3★', '4★', '5★', '6★']
    plt.suptitle('Arknight Gacha Statistics', bbox={'facecolor':'0.9', 'pad':5})
    # 稀有度分布饼图
    axes[0, 0].pie(
        count,
        colors = colors,
        labels = labels,
        explode = [0.02, 0.02, 0.08, 0.16],
        pctdistance = 0.7,
        autopct = lambda x: '%d / %1.2f%%' % (x*total/100, x),
        wedgeprops = dict(edgecolor='black', linewidth=1)
    )
    axes[0, 0].set_title('total: %d' % total, y=-0.05)
    # 稀有度分布趋势堆积式折线图
    axes[0, 1].stackplot(
        range(total+1), # x轴
        trend[3], trend[2], trend[1], trend[0], # 折线数据
        labels = reversed(labels), # 倒序排列 -> 高稀有度在下
        colors = reversed(colors)
    )
    axes[0, 1].set_title('Rarity distribution trend')
    axes[0, 1].legend(loc=2)
    # 未完成: 5/6星角色出货统计（柱状图） and  每25(暂定)抽的出率统计（柱状图）
    axes[1, 0].set_title('High rarity character distribution (Unfinished)')
    axes[1, 1].set_title('Rarity distribution in every 25 draws (Unfinished)')
    # 保存&显示
    filename = rec[-1]['date'].replace(':', '-')
    if (args.export):
        fig.savefig('logs/%s.jpg' % filename)
        print('Saved to logs/%s.jpg' % filename)
        return None
    fig.show()
    ans = input('是否保存图片Y/n? ')
    if (ans.lower() == 'y' or not ans):
        fig.savefig('logs/%s.jpg' % filename)
        print('Saved to logs/%s.jpg' % filename)
    else:
        print('Not save')
    return None

if (__name__ == '__main__'):
    try:
        with open('logs/log.json', 'r', encoding='UTF-8') as f:
            rec = json.load(f)
            olddate = time.mktime(time.strptime(rec[-1]['date'], '%Y-%m-%d %H:%M:%S'))
    except FileNotFoundError:
        if(not os.path.exists('logs')):
            os.mkdir('logs')
    if (args.reset):
        try:
            for root, dirs, files in os.walk('logs', topdown=False):
                for name in files:
                    print('删除%s' % os.path.join(root, name))
                    os.remove(os.path.join(root, name))
        except:
            print('没有文件需要删除')
        exit()
    if (not (args.skip_fetch or args.export)):
        fetch()
    if (not args.skip_draw):
        draw()
    print('All Done, exiting...')