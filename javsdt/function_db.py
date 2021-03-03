import mysql.connector
import sys

config = {
  'user': 'root',
  'password': 'lovefishd1c',
  'host': '192.168.1.251',
  'port': '3307',
  'database': 'video_info',
  'raise_on_warnings': True
}

class my_db:
    
    def __init__(self) -> None:
        super().__init__()
        try:
            self._cnx = mysql.connector.connect(**config)
            self._cursor = self._cnx.cursor()
        except:
            print(sys.exc_info())

    def commit(self):
        self._cnx.commit()

    def close(self):
        self._cnx.close()

    def get_cursor(self):
        return self._cursor
    
    def execute(self, sql, param = None):
        try:
            self._cursor.execute(sql, param)

            return self._cursor
        except:
            print(sys.exc_info())

    

