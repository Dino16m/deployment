from helper import read_file, write_file
import argparse
import sys
import os

BASE_DIR = os.path.dirname(os.path.abspath(__file__))

def init(arguments, apachedir, appname):
	filename = appname + '.conf'
	if os.path.isfile(os.path.join(apachedir, filename)):
		print("file {} already exists, leaving it alone....".format(os.path.join(apachedir, filename)))
		sys.exit(1)
	raw_data = read_file(os.path.join(BASE_DIR,'init_install.conf'))
	for key, argument in arguments.items():
		raw_data = raw_data.replace("{{"+key+"}}", argument)
	if write_file(os.path.join(apachedir, filename), raw_data):
		print('Initial config written to outfile')
		sys.exit(0)
	else:
		sys.exit('Initial config could not be written')

def main():
	parser = argparse.ArgumentParser(description='Add arguments for setup')
	parser.add_argument('--servername', type=str)
	parser.add_argument('--serveralias', type=str, default='', required=False)
	parser.add_argument('--serveradmin', type=str, default='', required=False)
	parser.add_argument('--apachedir', type=str, default='', required=False)
	parser.add_argument('--appname', type=str, default='')
	args = parser.parse_args()
	arguments = {}
	arguments["servername"] = args.servername
	arguments["serveradmin"] = args.serveradmin
	arguments["serveralias"] = args.serveralias
	apachedir = args.apachedir
	appname = args.appname if args.appname != 'default' else arguments['servername'].replace(".", '')
	init(arguments, apachedir, appname)

if __name__ == '__main__':
	main()
