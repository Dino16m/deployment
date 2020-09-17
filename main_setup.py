from helper import read_file, append_file, write_file
import os
import argparse
import sys
import re
import shutil
import random
import string as charset

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
class BaseSetUp:
	REQUIRED = ['servername', 'serveralias', 'serveradmin']
	CONF_FILE = ''
	appname = ''
	arguments = {}

	@classmethod
	def init(cls, arguments, apachedir, appname):
		cls.appname = appname
		filename = appname + '.conf'
		sec_filename = os.path.join(apachedir, appname + '-le-ssl' + '.conf')
		if not os.path.isfile(os.path.join(apachedir, sec_filename)):
			sys.exit('It seems that certbot has not made a file for you, restart installation')
		unavailable = set(cls.REQUIRED) - set(arguments.keys())
		for item in unavailable:
			arguments[item] = input('please input the value for {}: '.format(item))
		sec_file = read_file(sec_filename)
		sslcertfile = re.search("SSLCertificateFile.*", sec_file)
		sslkeyfile = re.search("SSLCertificateKeyFile.*", sec_file)
		if not sslcertfile:
			sys.exit('SSLCertificateFile not set in {}, aborting'.format(sec_filename))
		if not sslkeyfile:
			sys.exit('SSLCertificateKeyFile not set in {}, aborting'.format(sec_filename))
		arguments['sslcertfile'] = sslcertfile.group()
		arguments['sslkeyfile'] = sslkeyfile.group()
		conf_file = os.path.join(BASE_DIR, cls.CONF_FILE)
		raw_data = read_file(conf_file)
		for key, argument in arguments.items():
			raw_data = raw_data.replace("{{"+key+"}}", argument)
		if append_file(os.path.join(apachedir, filename), raw_data):
			print('Config file for https set up')
			os.remove(os.path.join(apachedir, sec_filename))
		else:
			sys.exit('Could not set up config file for https, aborting...')
		cls.arguments = arguments
		cls.hook()
		print('We are done here')

	@classmethod
	def hook(cls):
		pass

class PySetUp(BaseSetUp):
	REQUIRED = ['servername', 'serveralias', 'serveradmin', 'wsgidir', 'pythonhome', 
		'homepath', 'medianame', 'mediapath', 'staticname', 'staticpath', 'name']

	CONF_FILE = 'py_secure.conf'

class PhpSetup(BaseSetUp):
	REQUIRED = ['servername', 'serveralias', 'serveradmin', 'documentroot']

	@classmethod
	def hook(cls):
		print('If this installation is Laravel, enter 1')
		print('=======================================')
		print('If this installation is WordPress, enter 2')
		print('=======================================')
		print('If this installation is plain PHP, enter 3')
		print('If you can takeover the installation from here please enter 0 ')
		install_type = int(input('please type a number from 1 - 3 corresponding to the options above: ')) or 0
		if install_type == 0:
			return
		elif install_type == 1:
			cls.install_laravel()
		elif install_type == 2:
			cls.install_wp()
		elif install_type == 3:
			return
		else:
			return

	@classmethod
	def install_laravel(cls):
		print('We are about to setup a supervisor queue, please type ctrl+c if you don\'t want that to happen')
		supervisor_dir = str(input("Input the full path to supervisor conf.d, defaults to /etc/supervisor/conf.d/ if empty: ")) or '/etc/supervisor/conf.d/'
		artisan_root = str(input("Input the full path to artisan"))
		sup_src_file = read_file('supervisor.conf')
		sup_src_file = sup_src_file.replace("{{queuename}}", cls.appname)
		sup_src_file = sup_src_file.replace("{{artisan_root}}", artisan_root)
		if write_file(os.path.join(supervisor_dir, cls.appname+'.conf')):
			print('laravel queue supervisor set up, restart supervisorctl')
		else:
			sys.exit('laravel queue supervisor not set up')


	@classmethod
	def install_wp(cls):
		wp_requirements = ['db_name', 'db_user', 'db_pass', 'db_host']
		wp_template_path = None
		tries = 0
		while not wp_template_path and tries < 2:
			wp_template_path = input('please input the fully qualified path to your downloaded wordpress folder: ')
			tries += 1
		if not wp_template_path:
			sys.exit('wordpress template folder is required')
		documentroot = cls.arguments.get('documentroot', None) or input('What directory do you want to install wordpress? ') 
		print('installing wordpress in {} please wait'.format(documentroot))
		shutil.copytree(wp_template_path, documentroot)
		arguments = {}
		for req in wp_requirements:
			arguments[req] = input('input the value for {} : '.format(req))
		arguments.update(cls.get_wp_secrets())
		src_wp_config = read_file('wp-config-sample.php')
		for key, argument in arguments.items():
			src_wp_config = src_wp_config.replace("{{"+key+"}}", argument)
		if write_file(os.path.join(documentroot, 'wp-config.php'), src_wp_config):
			print('wordpress set up successful, exiting...')


	@classmethod
	def get_wp_secrets(cls):
		keys = ['auth_key', 'secure_auth_key', 'logged_in_key', 'nonce_key', 'auth_salt', 'secure_auth_salt', 'logged_in_salt', 'nonce_salt']
		return {key: gen_str() for key in keys}

def gen_str(len=70):
	allowed = charset.ascii_letters + charset.digits + charset.punctuation.replace("'", '').replace('"', '')
	return ''.join(random.choice(allowed) for i in range(len))



def get_handler(stack):
	Handlers = {'php': PhpSetup, 'py': PySetUp, 'python': PySetUp, 'django': PySetUp, 'laravel': PhpSetup, 'wp': PhpSetup, 'wordpress': PhpSetup}
	return Handlers[stack.lower()]

def main():
	parser = argparse.ArgumentParser(description='Add arguments for setup')
	parser.add_argument('--servername', type=str)
	parser.add_argument('--serveralias', type=str, default='', required=False)
	parser.add_argument('--serveradmin', type=str, default='', required=False)
	parser.add_argument('--apachedir', type=str, default='', required=False)
	parser.add_argument('--appname', type=str, default='')
	parser.add_argument('--stack', type=str)
	args = parser.parse_args()
	arguments = {}
	arguments["servername"] = args.servername
	arguments["serveradmin"] = args.serveradmin
	arguments["serveralias"] = args.serveralias
	apachedir = args.apachedir
	appname = args.appname if args.appname != 'default' else arguments['servername'].replace(".", '')
	arguments["appname"] = appname 
	Handler = get_handler(args.stack)
	Handler.init(arguments, apachedir, appname)

if __name__ == '__main__':
	main()

