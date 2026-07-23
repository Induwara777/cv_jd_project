import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.utils import formatdate, make_msgid
import logging
logger = logging.getLogger(__name__)

def email_sending(receiver_email:str, sender_email:str,subject:str,email_body_plain:str,email_body_html:str)->str:
    try:
        app_password = "masked"
        sender_email = "harshaniherath2002@gmail.com"
        msg = MIMEMultipart("alternative")
        msg["Subject"] = subject
        msg["From"] = f"Recruitment Team <{sender_email}>"  
        msg["To"] = receiver_email

        msg["Date"] = formatdate(localtime=True)                          
        msg["Message-ID"] = make_msgid(domain=sender_email.split("@")[1]) 
        msg["Reply-To"] = sender_email                                    
        msg["Return-Path"] = sender_email                                
        msg["MIME-Version"] = "1.0"                                       
        msg["X-Mailer"] = "Python-smtplib"                              
        msg["X-Priority"] = "3" 
        msg["Precedence"] = "bulk"     

        part1 = MIMEText(email_body_plain, "plain", "utf-8")
        part2 = MIMEText(email_body_html, "html", "utf-8")

        msg.attach(part1)
        msg.attach(part2)

        # --- Send ---
        server = smtplib.SMTP_SSL("smtp.gmail.com", 465)
        server.login(sender_email, app_password)
        server.sendmail(sender_email, receiver_email, msg.as_string())
        server.quit() 
        text_data = "EMAIL IS SENDING SUCCESSFULLY"  

    except smtplib.SMTPAuthenticationError:
        logging.exception("AUTH FAILED — CHECK APP PASSWARD / ACCOUNT SETTING  \nFUNCTION_NAME : email_sending \nSCRIPT_NAME : email.py")
        text_data = "EMAIL FAILED. Authentication error — check app password."

    except smtplib.SMTPRecipientsRefused:
        logging.exception("RECEIVER ADDRESS REJECTED \nFUNCTION_NAME : email_sending \nSCRIPT_NAME : email.py")
        text_data = "EMAIL FAILED. Recipient address was refused."

    except smtplib.SMTPSenderRefused:
        logging.exception("SENDER REFUSED — POSSIBLE GEMAIL SUSPICIOUS ACTIVITIES FLAG \nFUNCTION_NAME : email_sending \nSCRIPT_NAME : email.py")
        text_data = "EMAIL FAILED. Sender address was refused."

    except smtplib.SMTPServerDisconnected:
        logging.exception("SERVER DISCONNECTED — POSSIBLE RATE LIMITING \nFUNCTION_NAME : email_sending \nSCRIPT_NAME : email.py")
        text_data = "EMAIL FAILED. Server disconnected unexpectedly."

    except smtplib.SMTPConnectError:
        logging.exception("CONNECTION FAILED — NETWORK/FIREWELL ISSUE \nFUNCTION_NAME : email_sending \nSCRIPT_NAME : email.py")
        text_data = "EMAIL FAILED. Could not connect to SMTP server."

    except (TimeoutError, ConnectionRefusedError) as e:
        logging.exception(f"NETWORK ERROR \nFUNCTION_NAME : email_sending \nSCRIPT_NAME : email.py")
        text_data = "EMAIL FAILED. Network/connection issue."

    except smtplib.SMTPException as e:
        logging.exception(f"GENERAL SMTP ERROR \nFUNCTION_NAME : email_sending \nSCRIPT_NAME : email.py")
        text_data = "EMAIL FAILED. SMTP error occurred."

    except Exception as e:
        logging.exception(f"UNEXPECTED ERROR \nFUNCTION_NAME : email_sending \nSCRIPT_NAME : email.py")
        text_data = "EMAIL FAILED." 

    return text_data
