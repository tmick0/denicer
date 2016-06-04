import collections, itertools, random, math
from dchat.storage import EmptyResponseError

__all__ = ['SimpleComposer', 'TwoWayComposer', 'TwoWayExtendingComposer', 'SeededTreeComposer']

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
        self._targetLength = int(targetLength)
        self._maxAttempts = int(maxAttempts)
    
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

    def __init__(self, backend, seed = None, targetLength = 4, breadth = 8, depth = 2):
        self._st = backend
        self.seed = seed
        self.target  = int(targetLength)
        self.depth   = int(depth)
        self.breadth = int(breadth)
    
    def generate(self):
    
        seed = None
    
        if self.seed != None:
            try:
                seed, _, _ = self._st.getRowContaining(self.seed)
            except EmptyResponseError:
                pass
        
        if seed == None:
            seed, _, _ = self._st.getRow()
        
        leaves = set()
        candidates = set()
    
        # extend left side of tree
        nodes, next = [ ], [seed]
        for i in xrange(self.depth):
            nodes, next = next, nodes
            for prev in nodes:
                for j in xrange(0, self.breadth):
                    try:
                        seq, _, _ = self._st.getRowEndingWith(prev[0], prev[1])
                        next.append(seq)
                    except EmptyResponseError:
                        pass
        leaves |= set(tuple(x) for x in next)
        
        # extend right side of tree
        nodes, next = [ ], [seed]
        for i in xrange(self.depth):
            nodes, next = next, nodes
            for prev in nodes:
                for j in xrange(0, self.breadth):
                    try:
                        seq, _, _ = self._st.getRowStartingWith(prev[1], prev[2])
                        next.append(seq)
                    except EmptyResponseError:
                        pass
        leaves |= set(tuple(x) for x in next)
        
        # extend each leaf node into a phrase
        for seed in leaves:
            phrase = collections.deque(seed)
            start, stop = False, False
            
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
            
            candidates.add(tuple(phrase))
        
        #  weighted selection based on deviation from target length
        def get_weight(phrase):
            return 1. / ((abs(self.target - len(phrase)) + 1))
        
        candidates = sorted(candidates, key=get_weight, reverse=True)
        total = sum(get_weight(x) for x in candidates)
        r = random.uniform(0, total)
        acc = 0
        for c in candidates:
            acc += get_weight(c)
            if acc > r:
                return " ".join(c)
        
            
