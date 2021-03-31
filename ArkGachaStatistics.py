from selenium import webdriver
from selenium.common.exceptions import NoSuchElementException
import json
import time
import os
import argparse
import matplotlib.pyplot as plt
import pylab
rec = []
olddate = 0

parser = argparse.ArgumentParser(description='Arknights Gacha Statistics - 一个明日方舟抽卡统计工具', add_help= True)
parser.add_argument('-d', '--debug', action='store_true', help='输出调试信息.')
parser.add_argument('-e', '--export', action='store_true', help='直接从已有数据导出图片.')
parser.add_argument('-f', '--file', metavar='filename', default='log', help='设置记录的文件名(默认为log.json).')
parser.add_argument('-m', '--minimum-rarity', type=int, choices=range(3, 7), default=4, help='设置单角色统计最低星级(3~6的整数，默认为4).')
parser.add_argument('-r', '--reset', action='store_true', help='清除历史记录.')
parser.add_argument('-s', '--skip-fetch', action='store_true', help='跳过从官网更新抽卡数据.')
parser.add_argument('--skip-draw', action='store_true', help='跳过画图.')
args = parser.parse_args()

# 指定默认字体
pylab.rcParams['font.sans-serif'] = ['SimHei']
pylab.rcParams['axes.unicode_minus'] = False

def debug(m):
    if (args.debug):
        print('[Debug] %s' % m)

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
        next_page = browser.find_element_by_xpath('//*[@id="app"]/div/div/div[3]/div[2]/div[2]/div[2]/ul/li[last()]/a')
        if (next_page.get_attribute('aria-disabled') == 'true' or not loop):
            break
        i += 1
        next_page.click()
        time.sleep(3)
    browser.close()
    #写入log
    print('Dump json')
    rec.extend(reversed(new_rec))
    with open('logs/%s.json' % logfile, 'w', encoding='UTF-8') as f:
        f.write(json.dumps(rec, indent=2, separators=(',', ': '), ensure_ascii=False))
    print('Done')
    time.sleep(1)
    return None

def draw():
    print('Draw picture')
    # 统计数据
    total = len(rec)
    count = [0, 0, 0, 0] # 3~6星计数
    trend = [[0], [0], [0], [0]] # 3~6星趋势
    chars = {} # 角色计数
    trend25 = [] #25抽分布
    tmp = [0, 0, 0, 0]
    for i in rec:
        name, rarity = i['name'], i['rarity']
        count[rarity-3] += 1
        for j in range(4):
            trend[j].append(trend[j][-1]+1 if rarity-3 ==  j else trend[j][-1])
        if (rarity >= args.minimum_rarity):
            chars.setdefault(name, 0)
            chars[name] += 1
        tmp[rarity-3] += 1
        if (sum(tmp) == 25 or i == rec[-1]):
            trend25.append(tmp)
            tmp = [0, 0, 0, 0]
    chars = sorted(chars.items(), key=lambda d:d[1], reverse=True)
    debug(chars)
    debug(trend25)
    # 画图
    fig, axes = plt.subplots(
        2, 2,
        figsize = (16, 9),
        gridspec_kw = dict(height_ratios=[9, 7], width_ratios=[2, 1])
    )
    colors = ['lightgrey', 'cyan', 'yellow', 'orange']
    labels = ['3★', '4★', '5★', '6★']
    plt.suptitle('Arknight Gacha Statistics', bbox={'facecolor':'0.9', 'pad':5})
    # 稀有度分布（饼图）
    axes[0, 0].pie(
        count,
        colors = colors,
        labels = labels,
        explode = [0.02, 0.02, 0.08, 0.16],
        pctdistance = 0.7,
        autopct = lambda x: '%d / %1.2f%%' % (x*total/100, x),
        wedgeprops = dict(edgecolor='black', linewidth=1)
    )
    axes[0, 0].set_title('总计: %d抽' % total, y=-0.05)
    # 稀有度累计趋势（堆积式折线图）
    axes[0, 1].set_title('稀有度累计趋势')
    axes[0, 1].stackplot(
        range(total+1), # x轴
        trend[3], trend[2], trend[1], trend[0], # 折线数据
        labels = reversed(labels), # 倒序排列 -> 高稀有度在下
        colors = reversed(colors)
    )
    axes[0, 1].legend(loc=2)
    # 角色统计（柱状图）
    axes[1, 0].set_title('%d★以上角色统计' % args.minimum_rarity)
    axes[1, 0].bar(
        list(map(lambda l: l[0], [l for l in chars])),
        list(map(lambda l: l[1], [l for l in chars]))
    )
    debug(len(chars))
    for tick in axes[1, 0].get_xticklabels(): # 旋转标签
        tick.set_rotation(45)
        tick.set_fontsize(max(20-0.26*len(chars), 6)) # 字体大小：对测试数据做线性拟合，最小为6
    # 每25(暂定)抽稀有度分布（堆积式柱状图）
    axes[1, 1].set_title('每25抽稀有度分布')
    for i in range(4):
        axes[1, 1].bar(
            range(len(trend25)),
            list(map(lambda l: l[i], [l for l in trend25])),
            bottom = list(map(lambda l: sum(l[i+1:]), [l for l in trend25])),
            color = colors[i],
            tick_label = list(map(lambda x: str(x*25), range(len(trend25))))
        )
    # 保存&显示
    filename = '%s %s' % (logfile, rec[-1]['date'].replace(':', '-'))
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
    logfile = args.file.replace('.json', '')
    try:
        with open('logs/%s.json' % logfile, 'r', encoding='UTF-8') as f:
            rec = json.load(f)
            olddate = time.mktime(time.strptime(rec[-1]['date'], '%Y-%m-%d %H:%M:%S'))
    except FileNotFoundError:
        if(not os.path.exists('logs')):
            os.mkdir('logs')
        if (args.skip_fetch or args.export):
            print('错误：未找到指定的log文件，请检查-f参数，或不使用-s/-e')
            exit()
    if (args.reset):
        try:
            for root, dirs, files in os.walk('logs', topdown=False):
                for name in files:
                    debug('remove %s' % os.path.join(root, name))
                    os.remove(os.path.join(root, name))
        except:
            print('没有文件需要删除')
        exit()
    if (not (args.skip_fetch or args.export)):
        fetch()
    if (not args.skip_draw):
        draw()
    print('All Done, exiting...')