# This script is for sending emails.
# This can be imported in a different script or can be used from the command line.

import smtplib, getpass, sys, os
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.mime.application import MIMEApplication

def read_message(filepath):
	file1 = open(filepath, 'r')
	line = file1.readline()
	mesg = ''
	while line:
		mesg += line
		line = file1.readline()
	file1.close()
	return(mesg)

class EmailSender:
	def __init__(self, my_email):
		self.email = my_email
		self.password = getpass.getpass('Password: ')

	def send_mail_with_attachment(self, receiver_email, message, subject, attachment_filepath_list):
		if os.path.isfile(message):
			message = read_message(message)
		msg = MIMEMultipart()
		msg['Subject'] = subject
		msg['From'] = self.email
		msg['To'] = receiver_email
		msg.attach(MIMEText(message))
		if len(attachment_filepath_list) > 0:
			for epath in attachment_filepath_list:
				if os.path.isfile(epath):
					print("Attaching file " + epath)
					fname = os.path.basename(epath)
					attachment = MIMEApplication(open(epath, "rb").read())
					attachment.add_header('Content-Disposition', 'attachment', filename = fname)
					msg.attach(attachment)

		server = smtplib.SMTP('smtp.gmail.com:587')
		server.ehlo()
		server.starttls()
		server.login(self.email, self.password)
		server.sendmail(msg['From'], msg['To'], msg.as_string())
		server.quit()

# This part is for using the script as a command line tool.
if __name__ == '__main__':
	email_sender = EmailSender(input("Your email: "))
	email_receiver = input("Receiver's email: ")
	email_subject = input('Subject: ')
	email_message = input("If your message is not one line, press Return, or\nenter here: ")
	if len(email_message) == 0:
		filepath = input("If your message is not in a file, press Return, or\nenter path: ")
		if not len(filepath) == 0:
			while True:
				if not os.path.isfile(filepath):
					print("Incorrect file path: " + filepath)
					if input("Want to re-enter path? (Y/n) ").lower() == 'y':
						filepath = input("Path: ")
					else:
						break
				else:
					email_message = read_message(filepath)
					break
		else:
			if input("Do you want to type in your message? (Y/n) ").lower() == 'y':
				message_file = 'email_sender_temp_message'
				if message_file in os.listdir("."):
					os.remove(message_file)
				os.system("nano " + message_file)
				mesg = read_message(message_file)
				if message_file in os.listdir("."):
					os.remove(message_file)
	email_attachment_list = []
	if input('Attachment? (Y/n) ').lower() == 'y':
		while True:
			filepath = input('Enter path for attachment: ')
			if os.path.isfile(filepath):
				email_attachment_list.append(filepath)
			else:
				print("Invalid file path!")
			if not input('More attachment? (Y/n) ').lower() == 'y':
				break
	email_sender.send_mail_with_attachment(email_receiver, email_message, email_subject, email_attachment_list)