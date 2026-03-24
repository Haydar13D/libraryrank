try:
    import MySQLdb
except ImportError:
    # Fallback to pure-Python PyMySQL if mysqlclient fails to load on Windows
    import pymysql
    pymysql.version_info = (1, 4, 3, "final", 0)
    pymysql.install_as_MySQLdb()
