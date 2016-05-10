import os, sqlite3, itertools

class EmptyResponseError (Exception):
    pass

class AbstractBackend (object):

    def __init__(self):
        raise NotImplementedError()
    def __del__(self):
        self.close()
    def close(self):
        raise NotImplementedError()
    def addRow(self, row, start, end):
        raise NotImplementedError()
    def getStart(self):
        raise NotImplementedError()
    def getEnd(self):
        raise NotImplementedError()
    def getRow(self):
        raise NotImplementedError()
    def getRowStartingWith(self, a, b):
        raise NotImplementedError()
    def getRowEndingWith(self, b, c):
        raise NotImplementedError()

class SqliteBackend (AbstractBackend):
    
    def __init__(self, dbFile):
        existed = os.path.exists(dbFile)
        self._con = sqlite3.connect(dbFile)
        if not existed:
            self.init()
    
    def _tupleToRow(self, res):
        return (
            [res[0], res[1], res[2]],
            True if res[3] else False,
            True if res[4] else False
        )
    
    def close(self):
        if self._con != None:
            self._con.commit()
            self._con.close()
            self._con = None
    
    def init(self):
        self._con.executescript(
            """
            CREATE TABLE dictionary (id INTEGER PRIMARY KEY, a, b, c, s INTEGER, e INTEGER);
            CREATE INDEX dict_ab    ON dictionary(a, b);
            CREATE INDEX dict_bc    ON dictionary(b, c);
            """
        )
        self._con.commit()
    
    def addRow(self, row, start=False, end=False):
        self._con.execute(
            "INSERT INTO dictionary (a, b, c, s, e) VALUES (?, ?, ?, ?, ?)",
            list(itertools.chain(row, [1 if start else 0, 1 if end else 0]))
        )
        self._con.commit()
    
    def getRow(self):
        res = self._con.execute(
            "SELECT a, b, c, s, e FROM dictionary ORDER BY RANDOM() LIMIT 1"
        ).fetchone()
        if res == None:
            raise EmptyResponseError()
        return self._tupleToRow(res)
    
    def getStart(self):
        res = self._con.execute(
            "SELECT a, b, c, s, e FROM DICTIONARY WHERE s = 1 ORDER BY RANDOM() LIMIT 1"
        ).fetchone()
        if res == None:
            raise EmptyResponseError()
        return self._tupleToRow(res)
    
    def getEnd(self):
        res = self._con.execute(
            "SELECT a, b, c, s, e FROM DICTIONARY WHERE e = 1 ORDER BY RANDOM() LIMIT 1"
        ).fetchone()
        if res == None:
            raise EmptyResponseError()
        return self._tupleToRow(res)
    
    def getRowStartingWith(self, a, b):
        res = self._con.execute(
            "SELECT a, b, c, s, e FROM DICTIONARY WHERE a = ? AND b = ? ORDER BY RANDOM() LIMIT 1",
            [a, b]
        ).fetchone()
        if res == None:
            raise EmptyResponseError()
        return self._tupleToRow(res)
        
    def getRowEndingWith(self, b, c):
        res = self._con.execute(
            "SELECT a, b, c, s, e FROM DICTIONARY WHERE b = ? AND c = ? ORDER BY RANDOM() LIMIT 1",
            [b, c]
        ).fetchone()
        if res == None:
            raise EmptyResponseError()
        return self._tupleToRow(res)
