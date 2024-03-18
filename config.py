class Config():
     SECRET_KEY = 'B!1w8NAt1T^%kvhUI*S^'

class DevelopmentConfig(Config):
    DEBUG = True
    MYSQL_HOST = 'mysql-virtualassistance.alwaysdata.net'
    MYSQL_USER = '345240'
    MYSQL_PASSWORD = 'Lyla1295'
    MYSQL_DB = 'virtualassistance_db'

config = {
    'development': DevelopmentConfig
}