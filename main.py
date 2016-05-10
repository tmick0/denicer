import sys
import dchat

def main():
    storage = dchat.storage.SqliteBackend("brain.db")
    composer = dchat.compose.TwoWayExtendingComposer(storage)
    learner = dchat.learn.SimpleLearner(storage)
    
    phrases = [
        "hello world this is denice",
        "this is not the time for shenanigans",
        "the time for action is now",
        "is denice here right now?",
        "i like toast with peanut butter",
        "i like cake and ice cream",
        "peanut butter jelly time"
    ]
    
    for p in phrases:
        learner.learn(p)
    
    for _ in xrange(10):
        print(composer.generate())
    
    storage.close()

if __name__ == "__main__":
    sys.exit(main(*sys.argv[1:]))
