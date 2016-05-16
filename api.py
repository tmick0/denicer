from multiprocessing import JoinableQueue as Queue, Manager
from threading import Thread
from dchat import compose, learn

def customizedFetch(backend, composer, **kwargs):

    if composer == "SimpleComposer":
        c = compose.SimpleComposer(backend, **kwargs)
    elif composer == "TwoWayComposer":
        c = compose.TwoWayComposer(backend, **kwargs)
    elif composer == "TwoWayExtendingComposer":
        c = compose.TwoWayExtendingComposer(backend, **kwargs)
    elif composer == "SeededTreeComposer":
        c = compose.SeededTreeComposer(backend, **kwargs)
    else:
        return {
            "error": "Unknown composer %s" % composer
        }
    
    return {
        "response": c.generate()
    }

def customizedPush(backend, message, **kwargs):
    l = learn.SimpleLearner(backend)
    l.learn(message)
    
    return {
        "response": "ok"
    }

class TextCommandApi (object):

    def __init__(self, storage):
        self._st = storage
    
    def handle(self, method, args=""):
        if method == "fetch":
            composer = "SeededTreeComposer"
            kwargs = {}
            argparts = args.split(" ")
            for v in argparts:
                sp = v.split("=")
                if len(sp) > 1:
                    if sp[0] == "composer":
                        composer = sp[1]
                    else:
                        kwargs[sp[0]] = sp[1]
            r = customizedFetch(self._st, composer, **kwargs)
            if 'error' in r:
                return r['error']
            else:
                return r['response']
        elif method == "learn":
            customizedPush(self._st, args)

class DictionaryApi (object):

    def __init__(self, storage, authenticator):
        self._st = storage
        self._auth = authenticator
    def handle(self, obj):
        if not self._auth(obj['client-id'], obj['timestamp'], obj['client-hmac']):
            return {
                "error": "Invalid credentials"
            }
        mth = obj['body']['method']
        arg = obj['body']['params']
        if mth == 'fetch':
            return customizedFetch(self._st, **arg)
        elif mth == 'push':
            return customizedPush(self._st, **arg)
        else:
            return {
                "error": "Unknown method %s" % mth
            }

class LockingApi (object):

    def __init__(self, backend):
        self._backend = backend
        self._m = Manager()
        self._l = self._m.Lock()
    
    def handle(self, *args, **kwargs):
        self._l.acquire()
        result = self._backend.handle(*args, **kwargs)
        self._l.release()
        return result
    
    def stop(self):
        pass
