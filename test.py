from helper import read_file
import re
import sys

sec_filename = "php_secure.conf"
sec_file = read_file(sec_filename)
sslcertfile = re.search("SSLCertificateFile.*", sec_file)
sslkeyfile = re.search("SSLCertificateKeyFile.*", sec_file)
if not sslcertfile:
	sys.exit('SSLCertificateFile not set in {}, aborting'.format(sec_filename))
if not sslkeyfile:
	sys.exit('SSLCertificateKeyFile not set in {}, aborting'.format(sec_filename))