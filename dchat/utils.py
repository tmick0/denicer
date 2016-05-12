
class WordNode (object):

    def __init__(self, tup, start=False, end=False):
        self.tup = tup
        self.preds = []
        self.succs = []
        self.start = start
        self.end = end
        self.parent=None
    
    def __repr__(self):
        return " ".join(self.tup)

class WordTree (object):

    def __init__(self):
        self._root   = None
        self._nodes  = []
        self._starts = []
        self._ends   = []
    
    def insert(self, a, b, c, start=False, end=False):
        n = WordNode((a, b, c), start, end)
        self._nodes.append(n)
        if self._root == None:
            self._root = n
        if start:
            self._starts.append(n)
        if end:
            self._ends.append(n)
        return n
    
    def nodes(self):
        return self._nodes[:]

    def starts(self):
        return self._starts[:]
    
    def ends(self):
        return self._ends[:]
