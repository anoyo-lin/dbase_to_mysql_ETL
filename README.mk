#dbase to mysql ETL tool
when we implement some migrations from old F&B system to the new cloud-based one, it needs to change the legacy database from dbase IV to mysql, it also cost a lot labor work to handle this, whe i take full exam in the detial of both database, i will try to using python-based script and rich supportive library (in this example it is dbf-related library) to create a tool to automate the process when we do the migration task.
the neceesary coponent that is getting from other repositroy is
aenum-2.0.8.tar.gz*
appdirs-1.4.3.tar.gz*
dbf-0.96.8.zip*
enum34-1.1.6.tar.gz*
MySQL-python-1.2.5.zip*
packaging-16.8.tar.gz*
pyparsing-2.2.0.tar.gz*
Python-2.7.13.tgz*
setuptools-35.0.1.zip*
six-1.10.0.tar.gz*
and some RHEL5 linux dont install the mysql component before. and we may need the rpm package
mysql-community-devel-5.7.9-1.el5.i686.rpm*
mysql-community-libs-5.7.9-1.el5.i686.rpm*

