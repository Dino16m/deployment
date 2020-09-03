def read_file(path):
	try:
		with open(path, 'r+') as file:
			data = file.read()
			return data
	except IOError:
		return ''

def write_file(path, content):
	try:
		with open(path, 'w+') as file:
			file.write(content)
			return True
	except IOError:
		return False

def append_file(path, content):
	try:
		with open(path, 'a') as file:
			file.write(content)
			return True
	except IOError:
		return False

