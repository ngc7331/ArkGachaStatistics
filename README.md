# Arknights Gacha Statistics
一个练手用的明日方舟抽卡统计工具 - 基于python+selenium+chrome

## 基本思路
1. 用浏览器打开官网页面，手动登录+通过验证码
2. 获取官网抽卡统计表格，获得抽卡时间和角色名，通过分析class获得稀有度，以字典列表的形式存储
3. 检测下一页是否存在，存在则进入
4. 我好菜，轻喷qwq

## 使用方法
1. 安装Google Chrome浏览器(89.0.4389.90)，python3
   - 如果使用Chrome浏览器其他版本(浏览器访问[chrome://settings/help](chrome://settings/help)查看版本号)，请自行[下载对应版本的chromedriver](http://npm.taobao.org/mirrors/chromedriver/)替换本项目文件夹中的`chromedriver.exe`
   - 其他浏览器暂不支持，如果您能适配，欢迎PR
2. 运行`pip install -r requirements.txt`安装依赖。
3. 运行`python ArkGachaStatistics.py`执行主程序。~~似乎直接双击即可正常运行？~~ 可选参数：
```
  usage: ArkGachaStatistics.py [-h] [-r] [-s] [--skip-draw] [-e]
    -h, --help        show this help message and exit
    -r, --reset       清除历史记录.
    -s, --skip-fetch  跳过从官网更新抽卡数据.
    --skip-draw       跳过画图.
    -e, --export      直接从已有数据导出图片.
```
4. 输入账户名和密码登录后按回车继续

## Change log
- 2021-03-29 实现绘制稀有度分布堆叠折线图，实现argparse解析参数
- 2021-03-28 创建项目，实现获取数据以及绘制稀有度分布饼图

## TO-DO
- 精确到每个干员的分布饼图？
- 欧气趋势柱状图？（每25抽(暂定)的稀有度分布）
- ......