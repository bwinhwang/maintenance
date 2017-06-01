#!/usr/bin/python
# -*- coding: UTF-8 -*-
#=============================================================
# Copyright: 2012~2015 NokiaSiemensNetworks
# FullName: utils.mail
# Changes: 
#==============================================================
# Date: 2013-8-23  
# Author:  klarke(miaoyun-klarke.guo@nsn.com)
# Comment: 
#==============================================================

import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.application import MIMEApplication

import logging
import os.path
import argparse

klarke_mail = 'miaoyun-klarke.guo@nokia.com'

class Mail:
    def __init__(self, subject, mail_from, mail_to, content, attachment=None, subtype='plain'):
        ''' get data to send the mail
        @param subject: str, subject for mail, title
        @param content: str, content of the mail
        @param attachment:  the files in attachment
        '''
        self.init_smtp(subject, mail_from, mail_to) 
        self.logger = logging.getLogger('error_statistic')
        if content:
            self.add_mail_content(content, subtype)
        if attachment:
            self.add_mail_attach(attachment)
        self.send_mail()
        self.close_smtp()
    
    def init_smtp(self, subject, mail_from, mail_to):
        self.smtp = smtplib.SMTP('mail.emea.nsn-intra.net')
        self.message = MIMEMultipart()
        self.message['Subject'] = subject
        self.message['From'] = mail_from 
        self.message['To'] = mail_to 
        
    def send_mail(self):
        '''use to send mail
        @param cc_list: the cc list of the mail
        @param message: email.message.Message, include the content and the attachements 
        '''
#         self.logger.info('From: '+self.from_addr+' To:'+self.to_addrs+' Message:'+self.message.as_string())
        self.smtp.sendmail( self.message['From'], self.message['To'], self.message.as_string())
    
    def close_smtp(self):
        self.smtp.close()
        
    def add_mail_content(self, content_str, subtype):
        ''' add mail content
        @param content_str: str, content of the mail
        '''
        mail_msg = MIMEText(content_str,subtype)
        self.message.attach(mail_msg)
        
    def add_mail_attach(self, attach_list):
        ''' add attachment to mail
        @param attach_list: list, the files that want to be attached
        '''
        for filename in attach_list:
            source_file = open(filename, 'rb')
            attachment = MIMEApplication(source_file.read())
            attachment.add_header('Content-Disposition', 'attachment', filename=os.path.basename(filename))
            self.message.attach(attachment)
            self.logger.info('add %s as attachment' % filename)
            


def args_parse():
    parser = argparse.ArgumentParser()
    parser.add_argument("-t", "--to", type=str, dest="mail_to", metavar="to",required = True, help="mail send to")
    parser.add_argument("-f", "--from", type=str, dest="mail_from", default = klarke_mail)
    parser.add_argument("-c", "--content", type=str, dest="content", metavar="content",  help="content of mail")
    parser.add_argument("-s", "--subject", type=str, dest="subject", metavar="subject",required = True, help="content of mail")
    args = parser.parse_args()
    return args        
    
if __name__  ==  '__main__':
    args = args_parse()
    Mail(args.subject, args.mail_from, args.mail_to, open(args.content).read())
