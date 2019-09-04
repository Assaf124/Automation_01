import logging
from logger import init_logger
import xml.etree.cElementTree as XML
import subprocess
import time


LOGGER = logging.getLogger(__name__)
LOGGER.setLevel(logging.DEBUG)


class WiFiManager:
    """
    This class use 'netsh' windows cmd tool in order to create wifi profile file (xml).
    Note that end user is unable to connect windows machine to a secured wifi network
    unless it has a saved profile.
    Once the profile file is created, it can be added to the profiles list.
    The next step is to connect the windows machine to the secured network - this is done
    by the executing the 'netsh wlan connect' command.
    """

    def __init__(self, wifi_profile_filename):
        self.wifi_profile_filename = wifi_profile_filename

    def create_wifi_profile(self, ssid, password, authentication, encryption):
        """
        This method create the profile.xml file.

        Args:
            ssid: The network name/ssid
            password: The network password/key
            authentication: authentication type. could be WPA2PSK | WPA2
            encryption: Should be set to 'AES'

        Returns:
            NA

        Raises:
            NA
        """

        self.root = XML.Element("WLANProfile", attrib={'xmlns': 'http://www.microsoft.com/networking/WLAN/profile/v1'})
        XML.SubElement(self.root, "name").text = ssid
        self.ssid_config = XML.SubElement(self.root, "SSIDConfig")
        self.ssid_sub = XML.SubElement(self.ssid_config, "SSID")
        XML.SubElement(self.ssid_sub, "name").text = ssid
        XML.SubElement(self.root, "connectionType").text = 'ESS'
        XML.SubElement(self.root, "connectionMode").text = 'auto'

        self.msm = XML.SubElement(self.root, "MSM")
        self.security = XML.SubElement(self.msm, "security")
        self.auth_encryption = XML.SubElement(self.security, "authEncryption")
        XML.SubElement(self.auth_encryption, "authentication").text = authentication
        XML.SubElement(self.auth_encryption, "encryption").text = encryption
        XML.SubElement(self.auth_encryption, "useOneX").text = 'false'

        self.shared_key = XML.SubElement(self.security, "sharedKey")
        XML.SubElement(self.shared_key, "keyType").text = 'passPhrase'
        XML.SubElement(self.shared_key, "protected").text = 'false'
        XML.SubElement(self.shared_key, "keyMaterial").text = password

        try:
            tree = XML.ElementTree(self.root)
            tree.write(self.wifi_profile_filename)
            LOGGER.info(f'{self.wifi_profile_filename} was created successfully at {"TBD: add location"}')

        except:
            LOGGER.error(f'Was unable to create {self.wifi_profile_filename}')
            pass

    def add_wifi_profile(self):
        """
        This method adds the profile to the profile list using the windows cmd command:
        'netsh wlan add profile filename=<wifi_profile_xml_file>'

        Args:
            ssid: The network name/ssid
            password: The network password/key
            authentication: authentication type. could be WPA2PSK | WPA2
            encryption: Should be set to 'AES'

        Returns:
            NA

        Raises:
            NA
        """

        args = ['netsh', 'wlan', 'add', 'profile', f'filename={self.wifi_profile_filename}']
        try:
            self.reply_msg1 = subprocess.check_output(args, stdin=None, stderr=None, shell=False, universal_newlines=False)
            if b'added on interface' in self.reply_msg1:
                LOGGER.info(f'{self.reply_msg1}')
                # return self.ssid

        except():
            LOGGER.error(f'{self.reply_msg1}')

    def connect_to_wifi(self, ssid):
        """
        This method connects the windows machine to the wi-fi network using the windows cmd command:
        'netsh wlan connect name=<network_ssid>'

        Args:
            ssid: The network name/ssid

        Returns:
            NA

        Raises:
            NA
        """

        args = ['netsh', 'wlan', 'connect', f'name={ssid}']
        try:
            self.reply_msg2 = subprocess.check_output(args, stdin=None, stderr=None, shell=False, universal_newlines=False)
            if b'request was completed successfully' in self.reply_msg2:
                LOGGER.info(f'{self.reply_msg2}')

        except:
            LOGGER.error(f'{self.reply_msg2}')


if __name__ == '__main__':
    init_logger()
    ssid = 'Hilton Opera'
    password = '00099999'
    authentication = 'WPA2PSK'
    encryption = 'AES'

    wfm = WiFiManager('wifi_profile.xml')
    wfm.create_wifi_profile(ssid, password, authentication, encryption)
    time.sleep(1)
    wfm.add_wifi_profile()
    wfm.connect_to_wifi(ssid)
