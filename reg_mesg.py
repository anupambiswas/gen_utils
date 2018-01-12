#!/usr/bin/python3
import sys, datetime, os, random, re

def usage(to_quit = True, show_advanced_options = False):
	def append_usage(command_description_text, command_text):
		command_description_text = "\tDescription: " + command_description_text + "\n"
		command_text = "\t$ python " + os.path.basename(sys.argv[0]) + " " + command_text + "\n"
		return(command_description_text + command_text + "\n")
	usage = "Usage:\n"
	usage += append_usage("Register message by providing subject description. End message indicator is, by default, '--endmessage'. To use a different one use the optional --emi.", "--sub <subject description> [--emi <end message indicator>]")
	usage += append_usage("Show all message filter types.", "--sft")
	usage += append_usage("Filter message display by filter type. Filter type detail, if required, and not provided in command-line, script will anyway ask for it.", "--fm <filter type> [<filter type detail>]")
	usage += append_usage("Remove message.", "--rem <message id>")
	usage += append_usage("Update message.", "--upd <message id>")

	if show_advanced_options:
		usage += "Advanced usage:\n"
		# to be developed later

	print(usage)
	if to_quit:
		quit()

def usage_error(error_message):
	print("\nERROR: " + error_message + "\n")
	usage()

def get_message(end_message_indicator):
	print("Message: (End your message with '" + end_message_indicator + "')")
	msg = ''
	while True:
		text_input = input()
		if text_input == end_message_indicator:
			break
		msg += text_input + "\n"
		# print("\t" + str(len(text_input))) # DB
	return(msg)

def get_time_or_period(tm):
	tp = lambda m, i: int(m.group(i))
	now = datetime.datetime.now()
	year, month, day = now.year, now.month, now.day
	hour, minute, second = 0, 0, 0 #now.hour, now.minute, now.second
	# upto second
	m0 = re.search("^(\d\d\d\d)-(\d\d)-(\d\d)\s+(\d\d)\:(\d\d)\:(\d\d)$", tm)
	m1 = re.search("^(\d\d\d\d)-(\d\d)-(\d\d)\s+(\d\d)\:(\d\d)$", tm)
	m2 = re.search("^(\d\d\d\d)-(\d\d)-(\d\d)\s+(\d\d)$", tm)
	m3 = re.search("^(\d\d\d\d)-(\d\d)-(\d\d)$", tm)
	m4 = re.search("^(\d\d)\:(\d\d)\:(\d\d)$", tm)
	m5 = re.search("^(\d\d)\:(\d\d)$", tm)
	m6 = re.search("^(\d\d)$", tm)
	for m in [m0, m1, m2, m3]:
		if m:
			year, month, day = tp(m, 1), tp(m, 2), tp(m, 3)
			break
	if m0 or m1 or m2:
		hour = tp(m, 4)
	if m0 or m1:
		minute = tp(m, 5)
	if m0:
		second = tp(m, 6)
	for m in [m4, m5, m6]:
		if m:
			hour = tp(m, 1)
			break
	if m4 or m5:
		minute = tp(m, 2)
	if m4:
		second = tp(m, 3)
	return(datetime.datetime(year, month, day, hour, minute, second))


def decide_what_to_do(messages_directory):
	subject_last_index = len(sys.argv)
	end_message_indicator = '--endmessage'
	if '--emi' in sys.argv:
		emi_ind = sys.argv.index('--emi')
		if len(sys.argv) > (emi_ind + 1):
			end_message_indicator = sys.argv[emi_ind + 1]
			subject_last_index = emi_ind
		else:
			usage_error("End message indicator not provided after using '--emi'.")
	if len(sys.argv) == 1:
		usage()
	option_provided = sys.argv[1]
	message_keeper = MessageKeeper(messages_directory)
	if option_provided == '--sub':
		if len(sys.argv) == 2:
			usage_error("Subject not provided.")
		# get end message indicator (if a different one is requested)
		subject_text = ' '.join(sys.argv[2: subject_last_index])
		# print(subject_text, end_message_indicator, subject_last_index) # DB
		print("Subject: " + subject_text)
		message = get_message(end_message_indicator)
		# print(message) # DB
		message_keeper.add_message(subject_text, message)

	elif option_provided == '--sft':
		pass

	elif option_provided == '--fm':
		pass

	elif option_provided == '--rem' or option_provided == '--upd':
		if not len(sys.argv) > 2:
			usage_error("No message id provided.")
		if not re.search("^\d+$", sys.argv[2]):
			usage_error("Incorrect message id provided - '" + sys.argv[2] + "'.")
		mesg_id = int(sys.argv[2])
		new_message = ''
		if option_provided == '--upd':
			new_message = get_message(end_message_indicator)
		message_keeper.parse_messages()
		message_keeper.update_message(mesg_id, new_message)
		message_keeper.save_update()
		# print(mesg_id) # DB

	elif option_provided == '--shall':
		message_keeper.parse_messages()
		message_keeper.show_in_time_range(None, None)

	elif option_provided == '--ship':
		message_keeper.parse_messages()
		from_= datetime.datetime.strptime(sys.argv[2], "%Y-%m-%d %H:%M:%S")
		to_ = datetime.datetime.strptime(sys.argv[3], "%Y-%m-%d %H:%M:%S")
		message_keeper.show_in_time_range(from_, to_)

	elif option_provided == '--chk':
		print(get_time_or_period(sys.argv[2]))

	elif option_provided == '--shsub':
		subs = sys.argv[2:]
		cf = lambda m, p: m['subject'] in p
		message_keeper.parse_messages()
		message_keeper.show_if(cf, subs)

	elif option_provided == '--chsub':
		mesg_id = int(sys.argv[2])
		message_keeper.parse_messages()
		if len(sys.argv) > 3:
			subj = sys.argv[3]
		else:
			subj = input('subject? ')
		message_keeper.update(mesg_id, 'subject', subj)

	else:
		usage()

class MessageKeeper:
	def __init__(self, mesg_direc):
		if not os.path.isdir(mesg_direc):
			print("\nERROR: Invalid messages directory.")
			quit()
		self.mesg_file = os.path.join(mesg_direc, 'messages')

	def get_display_message(self, mesg):
		disp_message = "\t"
		for c in mesg:
			disp_message += c
			if c == "\n":
				disp_message += "\t"
		return(disp_message)

	def parse_messages(self, to_display = False):
		self.messages = {}
		if not os.path.isfile(self.mesg_file):
			return
		getting_mesg = False
		f = open(self.mesg_file, 'r')
		l = f.readline()
		delim = None
		mesg_id = 0
		while l:
			m = re.search("\*\*\*\s*MESSAGE\s+TS\s+(.*)\s+SUB\s+(.*)\s+DELIMITER\s+([a-zA-Z]*)", l)
			if m:
				deleted = False
				m2 = re.search("DELIMITER\s+.*\s+DELETED", l)
				if m2:
					deleted = True
				time_str = m.group(1)
				subj = m.group(2)
				delim = m.group(3)
				# print(time_str, subj, delim) # DB
			if delim and delim in l:
				if '--start' in l:
					mesg = ''
					#disp_mesg = ''
					getting_mesg = True
				elif '--end' in l:
					getting_mesg = False
					if not deleted and to_display:
						print("Message " + str(mesg_id) + ": time " + time_str + " subject \"" + subj + "\"\n" + self.get_display_message(mesg) + "\n")
					self.messages[mesg_id] = {'time': time_str, 'subject': subj, 'message': mesg, 'deleted': deleted, 'delim': delim}
					mesg_id += 1
			elif getting_mesg:
				mesg += l
				#disp_mesg += "\t" + l
			l = f.readline()
		f.close()
		# print(self.messages) # DB

	def get_delimiter(self, num):
		delim = ''
		ch_range = list(range(65, 91))
		ch_range.extend(list(range(97, 123)))
		l = len(ch_range)
		for i in range(num):
			ch = chr(ch_range[random.randrange(l)])
			delim += ch
		return(delim)

	def get_formatted_message(self, subj, mesg, delim = None, timestamp = None, deleted = False):
		if not timestamp:
			timestamp = str(datetime.datetime.now())
		if not delim:
			delim = self.get_delimiter(50)
		fmesg = "*** MESSAGE TS " + timestamp + " SUB " + subj + " DELIMITER " + delim
		if deleted:
			fmesg += " DELETED"
		fmesg += "\n"
		fmesg += delim + " --start\n" + mesg + "\n" + delim + " --end"
		return(fmesg)

	def add_message(self, subj, mesg):
		fmesg = self.get_formatted_message(subj, mesg)
		#print("Formatted message:\n" + fmesg); return # DB
		f = open(self.mesg_file, 'a')
		f.write("\n" + fmesg)
		f.close()

	def update_message(self, message_id, new_message = ''):
		if new_message == '':
			self.messages[int(message_id)]['deleted'] = True
		else:
			self.messages[int(message_id)]['message'] = new_message

	def save_update(self):
		keys = list(self.messages.keys())
		keys.sort()
		f = open(self.mesg_file, 'w')
		for k in keys:
			message = self.messages[k]
			fmesg = self.get_formatted_message(message['subject'], message['message'], message['delim'], message['time'], message['deleted'])
			f.write("\n" + fmesg)
		f.close()

	def show_in_time_range(self, from_, to_):
		keys = list(self.messages.keys())
		keys.sort()
		for k in keys:
			message = self.messages[k]
			time_str = message['time']
			time = datetime.datetime.strptime(time_str, "%Y-%m-%d %H:%M:%S.%f")
			if not message['deleted']:
				if (from_ == None or time >= from_) and (to_ == None or time <= to_):
					print("Message " + str(k) + ": time " + time_str + " subject \"" + message['subject'] + "\"\n" + self.get_display_message(message['message']) + "\n")

	def show_if(self, cond_func, parms):
		keys = list(self.messages.keys())
		keys.sort()
		for k in keys:
			message = self.messages[k]
			time_str = message['time']
			if not message['deleted'] and cond_func(message, parms):
				print("Message " + str(k) + ": time " + time_str + " subject \"" + message['subject'] + "\"\n" + self.get_display_message(message['message']) + "\n")

	def update(self, mesg_id, field, content):
		if mesg_id in self.messages.keys():
			message = self.messages[mesg_id]
			if field in message.keys():
				message[field] = content
			else:
				pass
		else:
			pass
		self.save_update()




# configuration
messages_directory = "."

# main script
decide_what_to_do(messages_directory)

