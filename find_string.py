import sys, os

def get_opt(args, opt):
	if opt in args:
		ind = args.index(opt) + 1
		if len(args) > ind:
			return(args[ind])
	return(None)

def usage():
	usage = "Usage:\n"
	usage += "\tpython " + sys.argv[0] + " <string> <directory> [options]\n"
	usage += "\t" + "--cs for case sensitive search\n"
	usage += "\t" + "--pl for printing lines\n"
	return(usage)

class StringPolice:
	def __init__(self, strng, direc, case_sens, first_only, file_exts, file_exts_no):
		self.strng = strng
		self.direc = direc
		self.files_found = {}
		self.case_sens = case_sens
		self.first_only = first_only
		self.files_not_read = []
		self.file_exts = file_exts
		self.file_exts_no = file_exts_no
		if not self.case_sens:
			self.strng = self.strng.lower()
		self.search_dir(self.direc)

	def scan_file(self, filepath):
		try:
			line_nos = []
			file1 = open(filepath, 'r')
			line = file1.readline()
			lno = 1
			while line:
				oline = line
				if not self.case_sens:
					line = line.lower()
				if self.strng in line:
					line_nos.append([lno, oline.strip()])
					if self.first_only:
						break
				line = file1.readline()
				lno += 1
			file1.close()
			if len(line_nos) > 0:
				self.files_found[filepath] = line_nos
		except (IOError, UnicodeDecodeError):
			self.files_not_read.append(filepath)
		if not first_only:
			if len(self.files_found.keys()) > 100:
				self.print_results()
				self.files_found = {}

	def search_dir(self, direc):
		if not os.path.isdir(direc):
			return
		contents = os.listdir(direc)
		dirs_to_search = []
		for e in contents:
			fpath = os.path.join(direc, e)
			if os.path.isdir(fpath):
				dirs_to_search.append(fpath)
			else:
				# print("Searching", fpath) # DB
				to_look = True
				if len(self.file_exts) > 0:
					to_look = False
					for ee in self.file_exts:
						if len(ee) <= len(e) and e[-len(ee):] == ee:
							to_look = True
							break
				elif len(self.file_exts_no) > 0:
					for ee in self.file_exts_no:
						if len(ee) <= len(e) and e[-len(ee):] == ee:
							to_look = False
							break
				if to_look:
					self.scan_file(fpath)
		for e in dirs_to_search:
			self.search_dir(e)

	def print_results(self):
		for k in self.files_found.keys():
			print("Filename: ", k)
			if not self.first_only:
				for e in self.files_found[k]:
					print("\t", e[0], ":", e[1])

if len(sys.argv) > 2:
	try:
		strng = sys.argv[1]
		direc = sys.argv[2]
		case_sens, first_only = False, True
		file_exts = []
		file_exts_no = []
		if '--cs' in sys.argv:
			case_sens = True
		if '--pl':
			first_only = False
		for e in sys.argv[3:]:
			if '-exc-' in e and '-exc-' == e[0:5]:
				file_exts = e[5:].split('_')
				break
		for e in sys.argv[3:]:
			if '-no-' in e and '-no-' == e[0:4]:
				file_exts_no = e[5:].split('_')
				break
		sp = StringPolice(strng, direc, case_sens, first_only, file_exts, file_exts_no)
		sp.print_results()
	except KeyboardInterrupt:
		print("\n\nGoodbye!\n")

