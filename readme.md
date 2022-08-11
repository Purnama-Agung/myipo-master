##### CRAWLER #####
yum groupinstall "Development tools"
yum install -y screen mercurial mysql mysql-devel python-devel python-setuptools python-yaml
yum -y install gcc openssl-devel bzip2-devel libffi-devel
cd /usr/src
wget https://www.python.org/ftp/python/3.7.3/Python-3.7.3.tgz
tar xzf Python-3.7.3.tgz
cd Python-3.7.3
./configure --enable-optimizations
make altinstall
cd /home/ && mkdir crawler && cd /home/crawler && mkdir log && mkdir worker && mkdir proxy && cd /home/crawler/log && mkdir circus && cd /home/crawler
git clone http://git.blackeye.id/Jeni.Priyanton/dosm_crawler_py3.git
cd dosm_crawler
pip install -r requirements.txt

##jika install circus error##
pip install --upgrade setuptools
 
##fiefox 68##
wget https://download-installer.cdn.mozilla.net/pub/firefox/releases/68.0.1/linux-x86_64/en-US/firefox-68.0.1.tar.bz2
tar xvjf firefox-68.0.1.tar.bz2
mv firefox /usr/local/
ln -s /usr/local/firefox/firefox /usr/bin/firefox

##### selenium crawler #####
yum install -y Xvfb
yum install -y firefox
**cd /tmp/ && wget https://github.com/mozilla/geckodriver/releases/download/v0.22.0/geckodriver-v0.22.0-linux64.tar.gz
tar -zxvf geckodriver-v0.22.0-linux64.tar.gz && mv geckodriver /usr/local/share/
ln -s /usr/local/share/geckodriver /usr/local/bin/geckodriver && ln -s /usr/local/share/geckodriver /usr/bin/geckodriver**

##install chromedriver##
#source http://chromedriver.chromium.org/
wget https://dl.google.com/linux/direct/google-chrome-stable_current_x86_64.rpm
yum localinstall -y google-chrome-stable_current_x86_64.rpm
cd /tmp/ && wget https://chromedriver.storage.googleapis.com/75.0.3770.90/chromedriver_linux64.zip
unzip chromedriver_linux64.zip && mv chromedriver /usr/local/share/
ln -s /usr/local/share/chromedriver /usr/local/bin/chromedriver && ln -s /usr/local/share/chromedriver /usr/bin/chromedriver

### install pool server ###
yum install httpd

#install php#
yum install php

#install mysql#
wget http://repo.mysql.com/mysql-community-release-el7-5.noarch.rpm
rpm -ivh mysql-community-release-el7-5.noarch.rpm
yum install mysql-server
systemctl start mysqld
mysqladmin -u root password <set password>

#install phpmyadmin#
rpm -iUvh http://dl.fedoraproject.org/pub/epel/epel-release-latest-7.noarch.rpm
yum install phpmyadmin
Vim /etc/httpd/conf.d/phpMyAdmin.conf
===
<Directory /usr/share/phpMyAdmin/>
   AddDefaultCharset UTF-8

   <IfModule mod_authz_core.c>
     # Apache 2.4
     <RequireAny>
       Require ip 192.168.20.125
       #Require ip ::1
       Require all granted
     </RequireAny>
   </IfModule>
   <IfModule !mod_authz_core.c>
     # Apache 2.2
     Order Deny,Allow
     Allow from All
     #Deny from All
     #Allow from 127.0.0.1
     #Allow from ::1
   </IfModule>
</Directory>

<Directory /usr/share/phpMyAdmin/setup/>
   <IfModule mod_authz_core.c>
     # Apache 2.4
     <RequireAny>
       Require ip 192.168.20.125
       #Require ip ::1
     </RequireAny>
   </IfModule>
   <IfModule !mod_authz_core.c>
     # Apache 2.2
     Order Deny,Allow
     Allow from All
     #Deny from All
     #Allow from 127.0.0.1
     Allow from ::1
   </IfModule>
</Directory>
====
systemctl restart httpd.service

##install SSDB###
http://ssdb.io/docs/php/
https://github.com/ideawu/ssdb
cd /tmp/
wget --no-check-certificate https://github.com/ideawu/ssdb/archive/master.zip
unzip master.zip
cd ssdb-master
vim ssdb-master/ssdb.conf
    ip 0.0.0.0.0
    output : stdout
    size : 100000000
    cache_size: 50
    
make && make install
cd /usr/local/ssdb
start: ./ssdb-server ssdb.conf

###UI SSDB###
scp phpssdbadmin.tar.gz
tar -xzvf phpssdbadmin.tar.gz
path var/www/html
vim /etc/httpd/conf.d/phpssdbadmin.conf
Insert text:
    Alias /phpssdbadmin /var/www/html/phpssdbadmin
    <Directory "/var/www/html/phpssdbadmin">
         Options FollowSymlinks
         AllowOverride All
         Order allow,deny
         Allow from all
    </Directory>
systemctl restart httpd.service
user = root
pass = rahasia123

###install Beanstalk###
yum install beanstalkd
chkconfig beanstalkd on
systemctl start beanstalkd.service
cd /etc
vim sysconfig/beanstalkd
Uncomentar : BINLOG_DIR=-b /var/lib/beanstalkd/binlog

###UI Beanstalkd###
scp beanstalk.zip
unzip beanstalk.zip
path var/www/html
chmod 777 html/beanstalk-ui/storage.json

##create database##
mysql -u root -p
Mysql> Create database dosm_crawler;
mysql>exit
import struktur dan data database
mysql -u root -p dosm_crawler < dosm_crawler_struktur.sql
mysql -u root -p dosm_crawler < dosm_crawler_data.sql 

#git#
git reset --hard
    
#xdpyinfo#
yum -y install xorg-x11-utils

#install supervisor
https://linoxide.com/linux-how-to/supervisor-monitor-linux-servers-processes/
yum install epel-release -y
yum install supervisor -y
