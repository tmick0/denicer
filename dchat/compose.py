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
