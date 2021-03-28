from selenium import webdriver
from selenium.common.exceptions import NoSuchElementException
import json
import time
import os
import argparse
import matplotlib.pyplot as plt
l = []
olddate = 0

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
    nl = []
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
                nl.append({
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
    l.extend(reversed(nl))
    with open('logs/log.json', 'w', encoding='UTF-8') as f:
        f.write(json.dumps(l, indent=2, separators=(',', ': '), ensure_ascii=False))
    print('Done')
    time.sleep(3)

def draw():
    print('Draw picture')
    count = [0, 0, 0, 0]
    for i in l:
        count[i['rarity']-3] += 1
    fig = plt.figure()
    plt.pie(
        count,
        colors=['grey', 'blue', 'yellow', 'orange'],
        labels=['3★', '4★', '5★', '6★'],
        explode=[0.03, 0.04, 0.05, 0.06],
        pctdistance=0.8,
        autopct='%1.2f%%',
        wedgeprops=dict(edgecolor='black', linewidth=1)
    )
    plt.title('Arknight Gacha Statistics', bbox={'facecolor':'0.8', 'pad':5})
    fig.show()
    input('请按回车继续')
    fig.savefig('logs/%s.jpg' % l[-1]['date'].replace(':', '-'))

if (__name__ == '__main__'):
    try:
        with open('logs/log.json', 'r', encoding='UTF-8') as f:
            l = json.load(f)
            olddate = time.mktime(time.strptime(l[-1]['date'], '%Y-%m-%d %H:%M:%S'))
    except FileNotFoundError:
        if(not os.path.exists('logs')):
            os.mkdir('logs')
    fetch()
    draw()