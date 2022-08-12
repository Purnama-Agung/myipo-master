### firefox 68 ###
yum install -y firefox
cd /tmp/ && wget https://github.com/mozilla/geckodriver/releases/download/v0.30.0/geckodriver-v0.30.0-linux32.tar.gz
tar -x geckodriver -zf geckodriver-v0.30.0-linux32.tar.gz
sudo mv geckodriver /usr/bin/geckodriver
cd /usr/bin/ && scp geckodriver /usr/local/bin/
sudo chmod +x /usr/bin/geckodriver 
cd /tmp/ && rm -rf geckodriver-v0.30.0-linux32.tar.gz

### selenium crawler ###
yum install -y Xvfb

### install chromedriver ###
First check to - https://chromedriver.storage.googleapis.com/index.html
curl --insecure https://intoli.com/install-google-chrome.sh | bash or yum install -y https://dl.google.com/linux/chrome/rpm/stable/x86_64/<match specify version what you want>
cd /tmp/ && wget https://chromedriver.storage.googleapis.com/<get from first step>
unzip chromedriver_linux64.zip
sudo mv chromedriver /usr/bin/chromedriver
sudo chown root:root /usr/bin/chromedriver
sudo chmod +x /usr/bin/chromedriver
cd /tmp && rm -rf chromedriver_linux64.zip

### install pool server ###
yum install httpd

### install php ###
yum install php

### install mysql ###
wget http://repo.mysql.com/mysql-community-release-el7-5.noarch.rpm
rpm -ivh mysql-community-release-el7-5.noarch.rpm
yum install mysql-server
systemctl start mysqld
mysqladmin -u root password <set password>

### install phpmyadmin ###
rpm -iUvh http://dl.fedoraproject.org/pub/epel/epel-release-latest-7.noarch.rpm
yum install phpmyadmin
Vim /etc/httpd/conf.d/phpMyAdmin.conf

===
<Directory /usr/share/phpMyAdmin/>
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

### install SSDB ###
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

### UI SSDB ###
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

### install Beanstalk ###
wget http://cbs.centos.org/kojifiles/packages/beanstalkd/1.9/3.el7/x86_64/beanstalkd-1.9-3.el7.x86_64.rpm
wget http://cbs.centos.org/kojifiles/packages/beanstalkd/1.9/3.el7/x86_64/beanstalkd-debuginfo-1.9-3.el7.x86_64.rpm
rpm -ivh beanstalkd-1.9-3.el7.x86_64.rpm
rpm -ivh beanstalkd-debuginfo-1.9-3.el7.x86_64.rpm
systemctl enable beanstalkd
systemctl start beanstalkd
ps aux | grep beanstalkd
beanstalkd -v

### UI Beanstalkd ### 
git clone https://github.com/ptrofimov/beanstalk_console.git
put into your /var/www/html/
chmod +777 /var/www/html/beanstalk_console/storage.json
http://<ip server>/beanstalk_console/public/

### create database ###
mysql -u root -p
Mysql> Create database dosm_crawler;
mysql>exit
import struktur dan data database
mysql -u root -p dosm_crawler < dosm_crawler_struktur.sql
mysql -u root -p dosm_crawler < dosm_crawler_data.sql 

### git ###
git reset --hard
    
### xdpyinfo ###
yum -y install xorg-x11-utils

### install supervisor ###
https://linoxide.com/linux-how-to/supervisor-monitor-linux-servers-processes/
yum install epel-release -y
yum install supervisor -y

