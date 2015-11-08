__author__ = 'sebastien'


#!/usr/bin/python
import os
import re
import sys
import time
from rancher_metadata import MetadataAPI

__author__ = 'Sebastien LANGOUREAUX'

TOMCAT_PATH = '/opt/tomcat'

class ServiceRun():



  def run(self, list_config, path):

    if list_config is None:
        raise KeyError("You must set the list_config")

    if path is None or path == '':
        raise KeyError("You must set the path")

    while True:
        try:
            status = self.set_app_setting(list_config, path)
            if status == True:
                break
        except Exception,e:
            print("Some error appear : " + e.message)

        print("We try again in 60s")
        time.sleep(60)

    print("Setting app done")




  def set_app_setting(self, list_config, path):
    global TOMCAT_PATH

    for key, value in list_config.iteritems():
        self.replace_all(TOMCAT_PATH + '/' + path, re.escape(key) + '\s*=.*', key + '=' + value)

    return True




  def replace_all(self, file, searchRegex, replaceExp):
    """ Replace String in file with regex
    :param file: The file name where you should to modify the string
    :param searchRegex: The pattern witch must match to replace the string
    :param replaceExp: The string replacement
    :return:
    """

    regex = re.compile(searchRegex, re.IGNORECASE)

    f = open(file,'r')
    out = f.readlines()
    f.close()

    f = open(file,'w')

    for line in out:
      if regex.search(line) is not None:
        line = regex.sub(replaceExp, line)

      f.write(line)

    f.close()


  def add_end_file(self, file, line):
    """ Add line at the end of file
    :param file: The file where you should to add line to the end
    :param line: The line to add in file
    :return:
    """
    with open(file, "a") as myFile:
        myFile.write("\n" + line + "\n")



if __name__ == '__main__':
    # Start

    list_config = {}

    # Database setting
    if os.getenv('EQUARIUS_DB_INIT') is None:
        list_config['database.init'] = 'false'
    else:
        list_config['database.init'] = 'true'

    if os.getenv('DB_ENV_DB') is None:
        raise KeyError('No DB name setting. Are you sure you have link postgresql with the name DB ?')
    if os.getenv('DB_ENV_USER') is None:
        raise KeyError('No user setting for DB. Are you sure you have link postgresql with the name DB ?')
    if os.getenv('DB_ENV_PASS') is None:
        raise KeyError('No password setting for DB. Are you sure you have link postgresql with the name DB ?')
    list_config['dataSource.url'] = 'jdbc:postgresql://db:5432/' + os.getenv('DB_ENV_DB')
    list_config['dataSource.username'] = os.getenv('DB_ENV_USER')
    list_config['dataSource.password'] = os.getenv('DB_ENV_PASS')

    #Mail setting
    if os.getenv('EQUARIUS_SMTP_HOST') is not None:
        list_config['mailSender.host'] = os.getenv('EQUARIUS_SMTP_HOST')
    if os.getenv('EQUARIUS_SMTP_PORT') is not None:
        list_config['mailSender.port'] = os.getenv('EQUARIUS_SMTP_PORT')
    if os.getenv('EQUARIUS_SMTP_LOGIN') is not None:
        list_config['mailSender.username'] = os.getenv('EQUARIUS_SMTP_LOGIN')
    if os.getenv('EQUARIUS_SMTP_PASS') is not None:
        list_config['mailSender.password'] = os.getenv('EQUARIUS_SMTP_PASS')

    # Captcha setting
    if os.getenv('EQUARIUS_CAPTCHA_PRIVATE') is not None:
        list_config['reCaptcha.privateKey'] = os.getenv('EQUARIUS_CAPTCHA_PRIVATE')
    if os.getenv('EQUARIUS_CAPTCHA_PUBLIC') is not None:
        list_config['reCaptcha.publicKey'] = os.getenv('EQUARIUS_CAPTCHA_PUBLIC')

    # Domain setting
    if os.getenv('EQUARIUS_URL') is not None:
        list_config['urlGeneratorService.webDomain'] = os.getenv('EQUARIUS_URL')
    if os.getenv('EQUARIUS_PORT') is not None:
        list_config['urlGeneratorService.webProtocol'] = os.getenv('EQUARIUS_PORT')
    if os.getenv('EQUARIUS_CRYPTO_KEY') is not None:
        list_config['cryptoService.twoFishKey'] = os.getenv('EQUARIUS_CRYPTO_KEY')

    # User account setting
    if os.getenv('EQUARIUS_ACCOUNT_ACTIVATED_WAIT') is not None:
        list_config['user.not.activated.duration'] = os.getenv('EQUARIUS_ACCOUNT_ACTIVATED_WAIT')
    if os.getenv('EQUARIUS_ACCOUNT_NO_ACTIVITY_WAIT') is not None:
        list_config['user.not.enable.duration'] = os.getenv('EQUARIUS_ACCOUNT_NO_ACTIVITY_WAIT')
    if os.getenv('EQUARIUS_ACCOUNT_NO_ACTIVITY__REAL_WAIT') is not None:
        list_config['user.not.enable.duration.real'] = os.getenv('EQUARIUS_ACCOUNT_NO_ACTIVITY__REAL_WAIT')

    service = ServiceRun()
    service.run(list_config, 'e-quarius/config.properties')
