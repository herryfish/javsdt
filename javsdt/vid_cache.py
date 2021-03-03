from function_db import my_db
import os
import sys
from traceback import format_exc

class VidCache:
    
    _vid_list = []
    _add_list = []
    _db = None

    def __del__(self) -> None:
        self._db.close()
        

    def __init__(self) -> None:
        super().__init__()

        self._db = my_db()

        sql = 'select vid from video'

        cursor = self._db.execute(sql)
        alldata = cursor.fetchall()
        for s in alldata:
            self._vid_list.append(s[0])

    def add_jpgfile_dir(self, root_choose):
        for root, dirs, files in os.walk(root_choose):
            if not files:
                continue
            for file_raw in files:
                if file_raw.endswith('.jpg'):
                    #print(file_raw[:len(file_raw)-4])
                    self._vid_list.append(file_raw[:len(file_raw)-4])

    def contains(self, vid):
        if (not vid in self._vid_list):
            #self._vid_list.append(vid)
            return False
        else:
            return True 

    def print(self):
        print(self._vid_list)

    def getlist(self):
        return self._vid_list

    def selectNeedUpdate(self, vid):
        sql = '''
        SELECT COUNT(1) FROM video WHERE vid = %s AND blurb = %s
        '''
        try:
            self._db.execute(sql, (vid, ''))
            #print(self._db.get_cursor().fetchone()[0])
            if (int(self._db.get_cursor().fetchone()[0]) == 0):
                #print('\t该车牌已发车。')
                return False
            return True
        except:
            print(format_exc())

    def add(self, vid, title, actor, blurb, tag, mpaa, country, release, runtime, director, studio, rate, poster_path):
        self._vid_list.append(vid)
        if vid in self._vid_list:
            if self.selectNeedUpdate(vid):
                self.updateDB(vid, title, actor, blurb, tag, mpaa, country, release, runtime, director, studio, rate, poster_path)
        else:
            self._vid_list.append(vid)
            self.insertDB(vid, title, actor, blurb, tag, mpaa, country, release, runtime, director, studio, rate, poster_path)
        
    def insertDB(self, vid, title, actor, blurb, tag, mpaa, country, release, runtime, director, studio, rate, poster_path):
        sql = '''
        INSERT INTO video (vid, title, actor, blurb, tag, mpaa, country, `release`, runtime, director, studio, rate, poster_path)
        VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
        '''
        try:
            self._db.execute(sql, (vid, title, actor, blurb, tag, mpaa, country, release, runtime, director, studio, rate, poster_path))
            self._db.commit()
        except:
            print(sys.exc_info())

    def updateDB(self, vid, title, actor, blurb, tag, mpaa, country, release, runtime, director, studio, rate, poster_path):
        sql = '''
        UPDATE video SET title = %s, actor = %s, blurb = %s, tag = %s, mpaa = %s, country = %s, `release` = %s, runtime = %s, director = %s, studio = %s, rate = %s
        WHERE vid = %s
        '''
        try:
            self._db.execute(sql, (title, actor, blurb, tag, mpaa, country, release, runtime, director, studio, rate, vid))
            self._db.commit()
        except:
            print(sys.exc_info())


def test():
    cache = VidCache()
    cache.print()
    print(cache.check('STAR-866'))
    print(cache.check('STAR-100'))
    print(cache.check('STAR-100'))
    cache.add_jpgfile_dir(os.getcwd() +  '\\temp\\')
    print(cache.check('XVSR-543'))

# test()