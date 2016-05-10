import collections
from dchat.storage import EmptyResponseError

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

    def __init__(self, backend, targetLength = 4, maxAttempts = 10):
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
