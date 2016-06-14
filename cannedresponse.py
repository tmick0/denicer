import os, sqlite3

class EmptyResponseError (Exception):
    pass

class CannedResponse (object):
    
    def __init__(self, dbFile):
        existed = os.path.exists(dbFile)
        self._con = sqlite3.connect(dbFile)
        if not existed:
            self.init()
    
    def close(self):
        if self._con != None:
            self._con.commit()
            self._con.close()
            self._con = None
    
    def init(self):
        self._con.executescript(
            """
            CREATE TABLE map (id INTEGER PRIMARY KEY, trigger, response);
            """
        )
        self._con.commit()
    
    def add(self, trigger, response):
        trigger = "%s%%" % trigger
        self._con.execute(
            "DELETE FROM map WHERE ? LIKE trigger",
            [trigger]
        )
        self._con.execute(
            "INSERT INTO map (trigger, response) VALUES (LOWER(?), ?)",
            [trigger, response]
        )
        self._con.commit()
    
    def get(self, trigger):
        res = self._con.execute(
            "SELECT response FROM map WHERE ? LIKE trigger",
            [trigger]
        ).fetchone()
        if res == None:
            raise EmptyResponseError()
        return res[0]
    
