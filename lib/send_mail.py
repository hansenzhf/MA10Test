#-*-coding: utf-8-*-
__author__ = "hank"

import smtplib
from email.mime.text import MIMEText

class SendMail(object):
    def send_mail(self, subject='Test', body='no message'):
        sender = 'zhenghanfeng2021@163.com'
        #receiver = "zhenghanfeng2019@163.com, bigbearxj1988@hotmail.com"
        receiver = "zhenghanfeng2019@163.com"

        smtp = smtplib.SMTP() 
        smtp.connect('smtp.163.com',25) 
        smtp.login("zhenghanfeng2021@163.com", "VTGZPNGWZXUKHEOM") 

        message = MIMEText(body, 'plain', 'utf-8')
        message['From'] = sender
        message['To'] = receiver
        message['Subject'] = subject

        smtp.sendmail(sender, receiver.split(','), message.as_string()) 
        smtp.quit()

