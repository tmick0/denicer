
class SimpleLearner (object):

    def __init__(self, backend):
        self._st = backend
    
    def learn(self, phrase):
        phrase = phrase.split(" ")
        start = True
        end = False
        while len(phrase) >= 3:
            if len(phrase) == 3:
                end = True
            self._st.addRow(phrase[:3], start, end)
            phrase = phrase[1:]
            start = False
