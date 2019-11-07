#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
#===========================================================================================================
# Copyright (c) 2006-2018 Paseman & Associates (www.paseman.com).  All rights reserved.
#===========================================================================================================

# https://codehandbook.org/how-to-read-email-from-gmail-using-python/
# Enable  POP - https://pythonprogramminglanguage.com/read-gmail-using-python/
# https://support.google.com/mail/answer/7104828?hl=en&visit_id=636729767012957184-344900862&rd=2
# https://pythonprogramminglanguage.com/read-gmail-using-python/
"""
import time
import imaplib
import email

ORG_EMAIL   = "@gmail.com"
SMTP_SERVER = "imap.gmail.com"
SMTP_PORT   = 993

FROM_EMAIL = ""
FROM_PWD   = ""

# -------------------------------------------------
#866 246 6453
# Utility to read email from Gmail Using Python
#bjpeppy@sbcglobal.net
# ------------------------------------------------
keys=['Delivered-To', 'Received', 'X-Google-Smtp-Source', 'X-Received', 'ARC-Seal', 'ARC-Message-Signature',
 'ARC-Authentication-Results', 'Return-Path', 'Received', 'Received-SPF', 'Authentication-Results',
 'Received', 'Received', 'Received', 'DKIM-Signature', 'Date', 'From', 'Reply-To', 'To',
 'Message-ID', 'Subject', 'Mime-Version', 'Content-Type', 'Content-Transfer-Encoding',
 'X-SA-serial', 'X-SA-workid', 'X-SA-messageid', 'X-SA-userid', 'x-provider', 'Sender', 'X-DynectEmail-Msg-Hash',
 'X-DynEmail-Meta', 'X-DynectEmail-Msg-Key', 'X-DynectEmail-X-Headers', 'X-Feedback-ID', 'X-Spam-Flag', 'X-UI-Out-Filterresults']

import os
#===========================================================================================================
# def save_attachment(msg, download_folder="/tmp"):
# https://stackoverflow.com/questions/6225763/downloading-multiple-attachments-using-imaplib
#===========================================================================================================
def save_attachment(msg, prefix, download_folder=""):
  """
  Given a message, save its attachments to the specified
  download folder (default is /tmp)

  return: file path to attachment
  """
  att_path = "No attachment found."
  for part in msg.walk():
    if part.get_content_maintype() == 'multipart':
      continue
    if part.get('Content-Disposition') is None:
      continue

    filename = part.get_filename()
    att_path = os.path.join(download_folder, prefix+filename)
    print att_path

    if not os.path.isfile(att_path):
      fp = open(att_path, 'wb')
      fp.write(part.get_payload(decode=True))
      fp.close()
  return att_path

#===========================================================================================================
month_dict = {"Jan":"01","Feb":"02","Mar":"03","Apr":"04","May":"05","Jun":"06","Jul":"07","Aug":"08","Sep":"09","Oct":"10","Nov":"11","Dec":"12",}
def read_email_from_gmail(label):
  """  # Need https://myaccount.google.com/lesssecureapps?pli=1"""
  try:
    mail = imaplib.IMAP4_SSL(SMTP_SERVER)
    mail.login(FROM_EMAIL,FROM_PWD)
    rv, mailboxes = mail.list()
    mail.select(label)

    # https://stackoverflow.com/questions/19001266/how-to-search-specific-e-mail-using-python-imaplib-imap4-search
    #type, data = mail.search(None, '(OR (TO "tech163@fusionswift.com") (FROM "Patty.Dewey@raymondjames.com"))')
    type, data = mail.search(None, 'ALL')
    
    mail_ids = data[0]

    id_list = mail_ids.split()   
    first_email_id = int(id_list[0])
    latest_email_id = int(id_list[-1])

    for i in range(latest_email_id,first_email_id, -1):
      typ, data = mail.fetch(i, '(RFC822)' )

      for response_part in data:
        if isinstance(response_part, tuple):
          msg = email.message_from_string(response_part[1])
          print 'Date : ' + msg['Date']
          print 'From : ' + msg['from']
          print 'Subject : ' + msg['subject']
          dt=msg['Date'].split(" ")
          prefix="%s-%s-%02d_"%(dt[3],month_dict[dt[2]],int(dt[1]))
          print save_attachment(msg,prefix,label) + "\n"

  except Exception, e:
      print str(e)

#===========================================================================================================
import time
if __name__ == '__main__':
  # FIRST https://myaccount.google.com/lesssecureapps?pli=1
  FROM_EMAIL = raw_input("gmail: ")
  FROM_PWD   = raw_input("password: ")

  FROM_EMAIL  = FROM_EMAIL + ORG_EMAIL
  print ">",FROM_EMAIL,"<  ",">",FROM_PWD,"<  "
  start_time = time.time()
  # Need Directory to match label, here it is: myFinance/PattyDewey
  # Step1: Download pdf Files (in "downloadAttachments.py")
  read_email_from_gmail('myFinance/PattyDewey')
  print("Finished in --- %s seconds ---" % (time.time() - start_time))

