import logging
from logger import init_logger
import re
from Configuration.auto_configuration import Settings
import subprocess
import time
from appium import webdriver
from appium.webdriver.common.touch_action import TouchAction


LOGGER = logging.getLogger(__name__)
# LOGGER.setLevel(logging.DEBUG)
LOGGER.setLevel(logging.INFO)


class AndroidManager:
    def __init__(self):
        LOGGER.info(f'AndroidManager object has been created')
        self.udid_reply_msg = ''
        self.udid = ''
        self.model_reply_msg = ''
        self.device_model = ''
        self.platform_reply_msg = ''
        self.platform_version = ''
        self.desired_caps = dict()
        self.wifi_enable_reply_msg = ''
        self.wifi_disable_reply_msg = ''
        self.driver = ''

    def get_device_udid(self):
        """
        This method extract the device UDID by running the next 'adb' command:
        adb devices

        Args:
            NA

        Returns:
            int:    udid

        Raises:
            NA
        """

        args = ['adb', 'devices']
        try:
            self.udid_reply_msg = subprocess.check_output(args, stdin=None, stderr=None, shell=False, universal_newlines=False)
            LOGGER.debug(f'{self.udid_reply_msg}')
            pattern = re.search('attached\r\n(.+?)\tdevice', self.udid_reply_msg.decode("utf-8"))

            if pattern:
                LOGGER.info(f'Device UDID is: {pattern.group(1)}')
                self.udid = pattern.group(1)
                return self.udid
        except:
            LOGGER.error(f'Got exception while trying to run "adb devices" command. Got next reply: {self.udid_reply_msg()}')

    def get_device_model(self):
        """
        This method extract the DEVICE MODEL by running the next 'adb' command:
        adb devices -l

        Args:
            NA

        Returns:
            int:    device model

        Raises:
            NA
        """

        args = ['adb', 'devices', '-l']
        try:
            self.model_reply_msg = subprocess.check_output(args, stdin=None, stderr=None, shell=False, universal_newlines=False)
            LOGGER.debug(f'{self.model_reply_msg}')
            # Extract the DEVICE MODEL from reply:
            pattern = re.search('model:(.+?)device:', self.model_reply_msg.decode("utf-8"))

            if pattern:
                LOGGER.info(f'Device Model is: {pattern.group(1)}')
                self.device_model = pattern.group(1)
                return self.device_model

        except:
            LOGGER.error(f'Got exception while trying to run "adb devices -l" command. Got next reply: {self.model_reply_msg}')

    def get_device_platform_version(self):
        """
        This method extract the device PLATFORM VERSION by running the next 'adb' command:
        adb shell getprop ro.build.version.release

        Args:
            NA

        Returns:
            int:    platform version

        Raises:
            NA
        """

        args = ['adb', 'shell', 'getprop', 'ro.build.version.release']
        try:
            self.platform_reply_msg = subprocess.check_output(args, stdin=None, stderr=None, shell=False, universal_newlines=False)
            LOGGER.debug(f'{self.platform_reply_msg}')
            # Extract the PLATFORM VERSION from reply:
            pattern = re.search('(.+?)\r\n', self.platform_reply_msg.decode("utf-8"))

            if pattern:
                LOGGER.info(f'Device OS version: Android {pattern.group(1)}')
                self.platform_version = pattern.group(1)
                return self.platform_version

        except:
            LOGGER.error(f'Got exception while trying to run "adb shell getprop ro.build.version.release" command. Got next reply: {self.platform_reply_msg}')

    def create_desire_capabilities(self, type):
        """
        This method creates a dictionary which hils the desired capabilities, which in turn, used
        by Appium to control the android device

        Args:
            type:   chrome - for launching chrome by appium
                    settings - for launching settings app

        Returns:
            dict:    desired capabilities

        Raises:
            NA
        """

        self.desired_caps["platformName"] = "Android"
        self.desired_caps["deviceName"] = self.get_device_model()
        self.desired_caps["udid"] = self.get_device_udid()
        self.desired_caps["platformVersion"] = self.get_device_platform_version()

        if type == 'chrome':
            self.desired_caps["browserName"] = "Chrome"
            LOGGER.info(f'Created successfully desired capabilities dictionary for settings: {self.desired_caps}')

        elif type == 'settings':
            self.desired_caps["appPackage"] = "com.android.settings"
            self.desired_caps["appActivity"] = ".Settings"
            LOGGER.info(f'Created successfully desired capabilities dictionary for chrome: {self.desired_caps}')

        else:
            pass

        return self.desired_caps

    def turn_wifi_on(self):
        """
        This method turns 'ON' the Wi-Fi button on the Android device

        Args:
            NA

        Returns:
            NA

        Raises:
            NA
        """

        self.get_device_udid()
        args = ['adb', '-s', self.udid, 'shell', 'svc wifi enable']
        try:
            self.wifi_enable_reply_msg = subprocess.check_output(args, stdin=None, stderr=None, shell=False, universal_newlines=False)
            LOGGER.debug(f'{self.wifi_enable_reply_msg}')
            LOGGER.info('Turned Wi-Fi on')

        except:
            LOGGER.error(f"Got exception while trying to turn on device's wi-fi. Got next reply: {self.wifi_enable_reply_msg()}")

    def turn_wifi_off(self):
        """
        This method turns 'OFF' the Wi-Fi button on the Android device

        Args:
            NA

        Returns:
            NA

        Raises:
            NA
        """

        self.get_device_udid()
        args = ['adb', '-s', self.udid, 'shell', 'svc wifi disable']
        try:
            self.wifi_disable_reply_msg = subprocess.check_output(args, stdin=None, stderr=None, shell=False, universal_newlines=False)
            LOGGER.debug(f'{self.wifi_disable_reply_msg}')
            LOGGER.info('Turned Wi-Fi off')
            'usage'
        except:
            LOGGER.error(f"Got exception while trying to turn off device's wi-fi. Got next reply: {self.wifi_disable_reply_msg()}")

    def connect_to_wifi(self):
        """
        This method connects the android device to a Wi-Fi network which its ssid named in the method input argument.

        Args:
            ssid:   Wi-Fi ssid

        Returns:
            True:   If connecting to Wi-Fi was successful
            False:  If was unable to connect the Wi-Fi network or if stated SSID was not found.

        Raises:
            NA
        """

        self.create_desire_capabilities('settings')
        try:
            self.driver = webdriver.Remote("http://localhost:4723/wd/hub", self.desired_caps)
            LOGGER.info(f'Launching chrome')
            time.sleep(1)
            self.el = self.driver.find_element_by_id('com.android.settings:id/dashboard_tile')
            self.el.click()

            time.sleep(1)
            self.el = self.driver.find_element_by_id('com.android.settings:id/icon_frame')
            self.el.click()

        except:
            pass

    def browse_to(self, url):
        """
        This method navigates the chrome browser to the selected 'url' in the method input argument.

        Args:
            url:    a valid url

        Returns:
            NA

        Raises:
            NA
        """

        self.create_desire_capabilities('chrome')
        try:
            self.driver = webdriver.Remote("http://localhost:4723/wd/hub", self.desired_caps)
            LOGGER.info(f'Launching chrome')
            time.sleep(1)
            self.driver.get(url)
            LOGGER.info(f'Navigating chrome to: {url}')
            time.sleep(3)
            self.driver.close()
        except:
            LOGGER.error(f'Was unable to  run chrome')


if __name__ == '__main__':
    init_logger()
    android = AndroidManager()
    # udid = device.get_device_udid()
    # model = device.get_device_model()
    # platform_version = device.get_device_platform_version()
    # print(f'UDID: {udid}\nMODEL: {model}\nPlatform: {platform_version}')

    # aaa = android.create_desire_capabilities('chrome')
    # print(aaa)

    # url1 = 'http://www.bbc.com'
    # url2 = 'http://www.bbc.com/culture'
    # android.browse_to(url2)

    # android.clear_browser_history()

    # android.turn_wifi_off()
    # time.sleep(5)
    # android.turn_wifi_on()

    # android.connect_to_wifi()
