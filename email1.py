
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText

# When email fails https://support.google.com/mail/answer/14257

def get_server(login, password, smtpserver='smtp.gmail.com:587'):

    """
        login -- Login username to an email server
        password -- Password for the given username for login
        smtpserver -- SMTP server to use to send emails; default is GMail's
                      'smtp.gmail.com:587' address
    """

    server = smtplib.SMTP(smtpserver)
    server.ehlo()
    server.starttls()
    server.ehlo()
    server.login(login, password)

    return server


def send(server, from_addr, to_addrs, subject, msg_text, msg_html,
        cc_addrs = None, bcc_addrs = None):
    """ Sends an email to a set of recipients by using a SMTP sever

        from_addr -- The email address of the sender
        to_addsr -- A list of destination email addresses
        subject -- Subject of the email
        msg_text -- The email message in plain text format
        msg_html -- THe email message in HTML format
        cc_addrs -- A list of CC destination email addresses
        bcc_addrs -- A list of BCC destination email addresses
    """

    # Create message container - the correct MIME type is multipart/alternative.
    msg = MIMEMultipart('alternative')
    msg['Subject'] = subject
    msg['From'] = from_addr
    msg['To'] = ','.join(to_addrs)
    if (cc_addrs and len(cc_addrs) > 0):
        msg['Cc'] = ','.join(cc_addrs)
    if (bcc_addrs and len(bcc_addrs) > 0):
        msg['Bcc'] = ','.join(bcc_addrs)

    # Record the MIME types of both parts - text/plain and text/html.
    part1 = MIMEText(unicode(msg_text).encode('utf-8'), 'plain')
    part2 = MIMEText(unicode(msg_html).encode('utf-8'), 'html')

    # Attach parts into message container.
    # According to RFC 2046, the last part of a multipart message, in this case
    # the HTML message, is best and preferred.
    msg.attach(part1)
    msg.attach(part2)
 
    server.sendmail(from_addr, to_addrs, msg.as_string())

