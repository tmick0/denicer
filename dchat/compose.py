import collections, itertools, random
from dchat.storage import EmptyResponseError
from dchat.utils import WordTree

class SimpleComposer (object):

    def __init__(self, backend):
        self._st = backend
    
    def generate(self):
        phrase, _, stop = self._st.getStart()
        while not stop:
            try:
                seq, _, stop = self._st.getRowStartingWith(*phrase[-2:])
                phrase.append(seq[-1])
            except EmptyResponseError:
                stop = True
        return " ".join(phrase)

class TwoWayComposer (object):

    def __init__(self, backend):
        self._st = backend
    
    def generate(self):
        seed, start, stop = self._st.getRow()
        phrase = collections.deque(seed)
        
        while not start:
            try:
                seq, start, _ = self._st.getRowEndingWith(phrase[0], phrase[1])
                phrase.appendleft(seq[0])
            except EmptyResponseError:
                start = True
        
        while not stop:
            try:
                seq, _, stop = self._st.getRowStartingWith(phrase[-2], phrase[-1])
                phrase.append(seq[-1])
            except EmptyResponseError:
                stop = True
                
        return " ".join(phrase)

class TwoWayExtendingComposer (object):

    def __init__(self, backend, targetLength = 8, maxAttempts = 10):
        self._st = backend
        self._targetLength = targetLength
        self._maxAttempts = maxAttempts
    
    def generate(self):
        seed, start, stop = self._st.getRow()
        phrase = collections.deque(seed)

        attempts = 0
        count = 0
        
        while not (start and (count >= self._targetLength or attempts >= self._maxAttempts)):
            try:
                seq, start, _ = self._st.getRowEndingWith(phrase[0], phrase[1])
                phrase.appendleft(seq[0])
                count += 1
            except EmptyResponseError:
                phrase.popleft()
                count -=1
                if count > 0:
                    phrase.popleft()
                    count -= 1
                attempts += 1
                start = False
        
        attempts = 0
        count = 0
        
        while not (stop and (count >= self._targetLength or attempts >= self._maxAttempts)):
            try:
                seq, _, stop = self._st.getRowStartingWith(phrase[-2], phrase[-1])
                phrase.append(seq[-1])
                count += 1
            except EmptyResponseError:
                phrase.pop()
                count -= 1
                if count > 0:
                    phrase.pop()
                    count -= 1
                attempts += 1
                stop = False
                
        return " ".join(phrase)

class SeededTreeComposer (object):

    def __init__(self, backend, seed = None, targetLength = 8, iters = None):
        self._st = backend
        self.seed = seed
        self.target = targetLength
        self.iters = iters
        if iters == None:
            self.iters = 2 * targetLength
    
    def generate(self):
    
        seed, start, stop = None, False, False
        
        if self.seed != None:
            try:
                seed, start, stop = self._st.getRowContaining(self.seed)
            except EmptyResponseError:
                pass
        
        if seed == None:
            seed, start, stop = self._st.getRow()
        
        t = WordTree()
        t.insert(*itertools.chain(seed, [start, stop]))
        
        for i in xrange(0, self.iters):
            for n in t.nodes():
                if not n.start:
                    try:
                        seq, start, stop = self._st.getRowEndingWith(n.tup[0], n.tup[1])
                        if not tuple(seq) in set(tuple(x.tup) for x in n.preds):
                            m = t.insert(*itertools.chain(seq, [start, stop]))
                            n.preds.append(m)
                            m.parent = n
                    except EmptyResponseError:
                        n.start = True
                if not n.end:
                    try:
                        seq, start, stop = self._st.getRowStartingWith(n.tup[1], n.tup[2])
                        if not tuple(seq) in set(tuple(x.tup) for x in n.succs):
                            m = t.insert(*itertools.chain(seq, [start, stop]))
                            n.succs.append(m)
                            m.parent = n
                    except EmptyResponseError:
                        n.end = True
                        
        starts = t.starts()
        ends = set(t.ends())
        
        def successor_paths(n):
            for s in n.succs:
                if s in ends:
                    yield [s]
                else:
                    for c in successor_paths(s):
                        p2 = [s]
                        p2.extend(c)
                        yield p2
        
        def compress(path):
            res = list(path[0].tup)
            for n in path[1:]:
                res.append(n.tup[2])
            return res
        
        def get_weight(phrase):
            return 1. / ((abs(self.target - len(x)) + 1))
        
        candidates = set()
        
        for s in starts:
        
            parents = []
            p = s
            while p != None and (s is p or s in p.preds):
                parents.append(p)
                p = p.parent
            
            for i in xrange(0, len(parents)):
                prefix = parents[:i+1]
                root = parents[i]
                succs = [x for x in successor_paths(root)]
                for succ in succs:
                    candidates.add(tuple(itertools.chain(prefix, succ)))

        compressed = set()

        for c in candidates:
            compressed.add(tuple(compress(c)))
            
        compressed = sorted(compressed, key=get_weight, reverse=True)
        total = sum(get_weight(x) for x in compressed)
        r = random.uniform(0, total)
        acc = 0
        for c in compressed:
            acc += get_weight(c)
            if acc > r:
                return " ".join(c)
            
