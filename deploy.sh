#!/bin/bash

for ARGUMENT in "$@"
do
	[[ $ARGUMENT =~  "=" ]] || continue
    KEY=$(echo $ARGUMENT | cut -f1 -d=)
    VALUE=$(echo $ARGUMENT | cut -f2 -d=)   

    case "$KEY" in
            SERVERNAME)              SERVERNAME=${VALUE} ;;
            SERVERALIAS)    SERVERALIAS=${VALUE} ;; 
			SERVERADMIN)	SERVERADMIN=${VALUE} ;;
			APACHEDIR)		APACHEDIR=${VALUE} ;;
			APPNAME)		APPNAME=${VALUE} ;;
			STACK)			STACK=${VALUE} ;;
            *)   
    esac    

done

[[ -n $SERVERNAME ]] || { echo "SERVERNAME must be set" ; exit; }

[[ -n $STACK  ]] || { echo "STACK must be set" ; exit; }
	
[[ -n $SERVERALIAS  ]] || SERVERALIAS="www.${SERVERNAME}"
	
[[ -n $SERVERADMIN  ]] || SERVERADMIN="default"
	
[[ -n $APACHEDIR  ]] || APACHEDIR="/mnt/e/xampp/htdocs/deployment/" 

[[ -n $APPNAME  ]] || APPNAME=${SERVERNAME//./}

python3 setup.py --servername $SERVERNAME --serveralias $SERVERALIAS --serveradmin $SERVERADMIN --apachedir $APACHEDIR --appname $APPNAME

if [[ $? == 1 ]]; then
	exit
fi

a2ensite "${APACHEDIR}${APPNAME}.conf":
systemctl restart apache2

certbot --apache -d $SERVERNAME -d $SERVERALIAS

python3 py_setup.py --servername $SERVERNAME --serveralias $SERVERALIAS --serveradmin $SERVERADMIN --apachedir $APACHEDIR --appname $APPNAME --stack $STACK

if [[ $? == 1 ]]; then
	exit
fi

echo what is your mysql root username?

read RootMysqlUser

echo what is your mysql root password?

read MysqlRootPassword

echo input a db name for your app, it will be created.

read DbName

echo input a db user for your app

read DbUser

echo input a db password for user $DbUser

read DbPassword

mysql -u $RootMysqlUser -p $MysqlRootPassword <<EOF
CREATE DATABASE $DbName DEFAULT CHARACTER SET utf8 COLLATE utf8_unicode_ci;
GRANT ALL ON ${DbName}.* TO '${DbUser}'@'localhost' IDENTIFIED BY $DbPassword
EOF
