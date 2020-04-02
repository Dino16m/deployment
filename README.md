#ReadMe of deployment
##Description
This is a collection of scripts in bash and python which **I** use for deployment of my projects.
It is highly opinionated and makes certain assumptions including;
1. That your hosting environment is a linux server.
2. That your terminal processor is bash
3. That you are using apache rather than nginx.
4. That you are using Django for Python or Laravel for PHP.
5. That you are using letsencrypt ssl certificate generator.
6. That you have python3 installed and it's callable as `python3`

All these parts, however, are easily modified.

##Usage
`sudo ./deploy.sh SERVERNAME=example.com SERVERALIAS=www.example.com STACK=python SERVERADMIN=admin@example.com APACHEDIR=/etc/apache2/sites-available`

>`SERVERNAME` and  `Stack` are required and have no defaults.
>The rest have defaults or will request for inputs interactively.

When the above shell script is executed, the program runs in interactive mode requesting input it requires from the user.