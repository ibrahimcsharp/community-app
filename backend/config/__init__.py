# This code runs once, when Django starts.

# 1) Use PyMySQL as the MySQL driver.
#    Django expects a driver called "MySQLdb" (from the mysqlclient package),
#    which needs a C compiler to install on Windows. PyMySQL is pure Python
#    and can pretend to be MySQLdb, so `pip install` just works.
import pymysql

pymysql.install_as_MySQLdb()

# 2) Make Django 5.2 work with XAMPP's MariaDB 10.4 (see that file for why).
from . import mariadb104  # noqa: E402,F401
