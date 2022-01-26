import os
import json
import wget
import zipfile
import requests
from selenium import webdriver
from selenium.common.exceptions import *
import msedge.selenium_tools
try:
    from modules.Logger import getLogger, Logger
except ImportError:
    pass

CHROMEDRIVER_URL = 'http://chromedriver.storage.googleapis.com/'
EDGEDRIVER_URL = 'https://msedgedriver.azureedge.net/'
FIREFOXDRIVER_API_URL = 'https://api.github.com/repos/mozilla/geckodriver/releases'
FIREFOXDRIVER_DOWNLOAD_URL = 'https://github.com/mozilla/geckodriver/releases/download/'

VALID_TYPE = {
    'chrome': ['win64', 'win32', 'linux64', 'mac64', 'mac_m1'],
    'edge': ['win64', 'win32', 'arm64'],
    'firefox': ['win64', 'win32', 'linux64', 'linux32', 'macos', 'macos-aarch64']
}

def copy(source, target) -> None:
    with open(source, 'rb') as fs:
        with open(target, 'wb') as ft:
            ft.write(fs.read())
    return None

class Driver():
    def __init__(self, logger:str='root', driver_path:str='/usr/bin', arch:str='linux64') -> None:
        self._logger = Logger(logger, False)
        self._drivers = []
        self._driver_path = driver_path
        self._arch = arch
        self._suffix = '.exe' if arch.startswith('win') else ''

    def getDrivers(self) -> list:
        return self._drivers

    def createDriver(self, tp:str = 'chrome', headless:bool = True, retry:int = 0) -> webdriver.Chrome:
        def createChrome() -> webdriver.Chrome:
            options = webdriver.ChromeOptions()
            options.add_experimental_option('excludeSwitches', ['enable-logging'])
            options.add_argument('--disable-gpu')
            options.add_argument('--no-sandbox')
            if (headless):
                options.add_argument('--headless')
            try:
                newdriver = webdriver.Chrome(
                    options = options,
                    executable_path = os.path.join(self._driver_path, 'chromedriver%s' % self._suffix)
                )
            except Exception as e:
                if ("executable needs to be in PATH." in e.__str__()):
                    self._logger.info('ChromeDriver Not Found, trying to install...')
                    if (not self.installDriver(tp)):
                        self._logger.error('Install failed, abort...')
                        return None
                    return self.createDriver(tp, headless, retry+1)
                elif ('Current browser version is' in e.__str__()):
                    self._logger.info('Outdated ChromeDriver, trying to update...')
                    version = e.__str__()
                    version = version[version.find('Current browser version is ')+27:version.find(' with binary path')].split('.')
                    if (not self.installDriver(tp, version[0])):
                        self._logger.error('Install failed, abort...')
                        return None
                    return self.createDriver(tp, headless, retry+1)
                self._logger.error('Unknown error: %s' % e)
            else:
                return newdriver
        def createEdge() -> msedge.selenium_tools.Edge:
            options = msedge.selenium_tools.EdgeOptions()
            options.use_chromium = True
            options.add_experimental_option('excludeSwitches', ['enable-logging'])
            options.add_argument('--disable-gpu')
            options.add_argument('--no-sandbox')
            if (headless):
                options.add_argument('--headless')
            try:
                newdriver = msedge.selenium_tools.Edge(
                    options = options,
                    executable_path = os.path.join(self._driver_path, 'msedgedriver%s' % self._suffix)
                )
            except Exception as e:
                if ("executable needs to be in PATH." in e.__str__()):
                    self._logger.info('EdgeDriver Not Found, trying to install...')
                    if (not self.installDriver(tp)):
                        self._logger.error('Install failed, abort...')
                        return None
                    return self.createDriver(tp, headless, retry+1)
                self._logger.error('Unknown error: %s' % e)
            else:
                return newdriver
        def createFirefox() -> webdriver.Firefox:
            options = webdriver.FirefoxOptions()
            options.add_argument('--disable-gpu')
            options.add_argument('--no-sandbox')
            if (headless):
                options.add_argument('--headless')
            try:
                newdriver = webdriver.Firefox(
                    options = options,
                    executable_path = os.path.join(self._driver_path, 'chromedriver%s' % self._suffix)
                )
            except Exception as e:
                self._logger.error('Unknown error: %s' % e)
            else:
                return newdriver

        if (retry >= 3):
            self._logger.error('Failed 3 times, abort...')
            return None

        if (tp not in VALID_TYPE.keys()):
            self._logger.error('Driver type error: %s is not supported.' % tp)
            return None
        if (self._arch not in VALID_TYPE[tp]):
            self._logger.error('%s does not support your arch: %s' % (tp, self._arch))
            return None

        newdriver = {
            'chrome': createChrome,
            'edge': createEdge,
            'firefox': createFirefox
        }[tp]()
        if (newdriver is not None):
            self._logger.info('Driver created.')
            self._drivers.append(newdriver)
            return newdriver
        else:
            self._logger.error('Create driver failed.')
        return None

    def installDriver(self, tp:str = 'chrome', version:str = '', retry:int = 0) -> bool:
        '''
        安装webdriver
        Parameters:
            tp - webdriver类型, chrome / edge / firefox
            version - webdriver版本，不指定或latest则自动检测最新版
            retry - 内部使用
        Returns:
            True when success
            False when failed
        '''
        def installChrome(version) -> bool:
            '''安装chromedriver'''
            arch = 'win32' if self._arch == 'win64' else self._arch
            # 获取真实版本号
            if (not version or version == 'latest'):
                r = requests.get('%sLATEST_RELEASE' % CHROMEDRIVER_URL)
            else:
                r = requests.get('%sLATEST_RELEASE_%s' % (CHROMEDRIVER_URL, version))
            version = r.content.decode()
            # 下载 & 解压
            url = '%s%s/chromedriver_%s.zip' % (CHROMEDRIVER_URL, version, arch)
            self._logger.info('Downloading driver: version %s for %s' % (version, arch))
            self._logger.debug('...from %s, to chromedriver.zip' % url)
            wget.download(url, out='chromedriver.zip')
            print()
            zipfile.ZipFile('chromedriver.zip').extractall()
            # 安装 & 授权
            driver_exec = os.path.join(self._driver_path, 'chromedriver%s' % self._suffix)
            self._logger.info('Installing')
            self._logger.debug('...to %s' % driver_exec)
            copy('chromedriver%s' % self._suffix, driver_exec)
            os.chmod(driver_exec, 0o755)
            # 删除临时文件
            self._logger.info('Remove temp files')
            os.unlink('chromedriver.zip')
            os.unlink('chromedriver%s' % self._suffix)
            return True

        def installEdge(version) -> bool:
            '''安装msedgedriver'''
            # 获取真实版本号
            if (not version or version == 'latest'):
                r = requests.get('%sLATEST_STABLE' % EDGEDRIVER_URL)
            else:
                r = requests.get('%sLATEST_RELEASE_%s' % (EDGEDRIVER_URL, version))
            version = r.content.decode(encoding="UTF-16").strip()
            # 下载 & 解压
            url = '%s%s/edgedriver_%s.zip' % (EDGEDRIVER_URL, version, self._arch)
            self._logger.info('Downloading driver: version %s for %s' % (version, self._arch))
            self._logger.debug('...from %s, to edgedriver.zip' % url)
            wget.download(url, out='edgedriver.zip')
            print()
            zipfile.ZipFile('edgedriver.zip').extractall()
            # 安装 & 授权
            driver_exec = os.path.join(self._driver_path, 'msedgedriver%s' % self._suffix)
            self._logger.info('Installing')
            self._logger.debug('...to %s' % driver_exec)
            copy('msedgedriver%s' % self._suffix, driver_exec)
            os.chmod(driver_exec, 0o755)
            # 删除临时文件
            self._logger.info('Remove temp files')
            os.unlink('edgedriver.zip')
            os.unlink('msedgedriver%s' % self._suffix)
            return True

        def installFirefox(version) -> bool:
            '''安装deckodriver'''
            # 记录压缩包后缀
            zipsuffix = '.zip' if self._arch.startswith('win') else '.tar.gz'
            # 获取可用版本列表
            self._logger.info('Get version list from Github')
            r = requests.get(FIREFOXDRIVER_API_URL)
            version_list = [item['name'] for item in json.loads(r.content.decode())]
            if (not version or version == 'latest'):
                version = version_list[0]
            elif (version not in version_list):
                self._logger.error('Install failed: version %s not found' % version)
                self._logger.debug('version_list = %s' % version_list)
                return False
            # 下载
            url = '%sv%s/geckodriver-v%s-%s%s' % (FIREFOXDRIVER_DOWNLOAD_URL, version, version, self._arch, zipsuffix)
            self._logger.info('Downloading driver: version %s for %s' % (version, self._arch))
            self._logger.debug('...from %s, to geckodriver%s' % (url, zipsuffix))
            wget.download(url, out='geckodriver%s' % zipsuffix)
            print()
            # 解压
            if (self._arch.startswith('win')):
                zipfile.ZipFile('geckodriver%s' % zipsuffix).extractall()
            else:
                os.popen('tar -xvf geckodriver%s' % zipsuffix)
            # 安装 & 授权
            driver_exec = os.path.join(self._driver_path, 'geckodriver%s' % self._suffix)
            self._logger.info('Installing')
            self._logger.debug('...to %s' % driver_exec)
            copy('geckodriver%s' % self._suffix, driver_exec)
            os.chmod(driver_exec, 0o755)
            # 删除临时文件
            self._logger.info('Remove temp files')
            os.unlink('geckodriver%s' % zipsuffix)
            os.unlink('geckodriver%s' % self._suffix)
            return True

        if (retry >= 2):
            self._logger.error('Failed, abort...')
            return False

        # 目标路径不存在，但其上级目录有写权限 -> 创建文件夹
        if (not os.path.exists(self._driver_path)\
            and os.access(os.path.abspath(os.path.join(self._driver_path, "..")), os.W_OK)):
            os.mkdir(self._driver_path)
        # 无写权限 -> 尝试更换路径为'./selenium'
        elif (not os.access(self._driver_path, os.W_OK)):
            self._logger.error('Install failed: no write permission in %s' % self._driver_path)
            self._logger.warning('install in ./selenium')
            self._driver_path = './selenium'
            return self.installDriver(tp, version, retry+1)
        if (tp not in VALID_TYPE.keys()):
            self._logger.error('Driver type error: %s is not supported.' % tp)
            return False
        if (self._arch not in VALID_TYPE[tp]):
            self._logger.error('%s does not support your arch: %s' % (tp, self._arch))
            return None

        return {
            'chrome': installChrome,
            'edge': installEdge,
            'firefox': installFirefox
        }[tp](version)


'''
if __name__ == '__main__':
    from Logger import getLogger, Logger
    driver = Driver()
    driver.installDriver('firefox')
'''