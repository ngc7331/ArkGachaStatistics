# Arknights Gacha Statistics
一个练手的明日方舟抽卡统计工具 - 基于python+selenium+chrome

## 基本思路
1. 用浏览器打开官网页面，手动登录+通过验证码
2. 获取官网抽卡统计表格，获得抽卡时间和角色名，通过分析class获得稀有度，以字典列表的形式存储
3. 检测下一页是否存在，存在则进入
4. 我好菜，轻喷qwq

## 使用方法
1. 安装Google Chrome浏览器(89.0.4389.90)，python3
   - 如果使用Chrome浏览器其他版本(浏览器访问[chrome://settings/help](chrome://settings/help)查看版本号)，请自行[下载对应版本的chromedriver](http://npm.taobao.org/mirrors/chromedriver/)替换本项目文件夹中的`chromedriver.exe`
   - 其他浏览器暂不支持，如果您能适配，欢迎PR
2. 运行`pip install -r requirements.txt`安装依赖
3. 运行`python ArkGachaStatistics.py`执行主程序
4. 输入账户名和密码登录后按回车继续

## Change log
- 2021-03-28 创建项目，实现获取数据以及绘制稀有度分布饼图

## TO-DO
- 增加argparse支持
  * -f 从官网更新数据
  * -d 画图
  * --clear 清除log
- 饼图中更详细的数据显示
  * 总抽数、不同稀有度数量显示
  * 精确到每个干员的分布饼图？
  * 欧气趋势折线图？
- ......