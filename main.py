import sys
import dchat

def main():
    storage = dchat.storage.SqliteBackend("brain.db")
    composer = dchat.compose.SimpleComposer(storage)
    learner = dchat.learn.SimpleLearner(storage)
    
    phrases = [
        "hello world this is denice",
        "this is not the time for shenanigans",
        "the time for action is now"
    ]
    
    for p in phrases:
        learner.learn(p)
    
    for _ in xrange(10):
        print(composer.generate())
    
    storage.close()

if __name__ == "__main__":
    sys.exit(main(*sys.argv[1:]))
