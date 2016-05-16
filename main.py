import sys, hmac, time, itertools
import dchat, api, httpservice, ircservice

client_params = {
    'test-client': 'test-client'
}

def main(mode, host='localhost', port=7000, *args):

    storage = dchat.storage.SqliteBackend("brain.db")
    
    if mode == "http":
        backend = api.LockingApi(api.DictionaryApi(storage, authenticator))
        httpservice.listen((host, int(port)), backend)
    elif mode == "irc":
        backend = api.TextCommandApi(storage)
        bot = ircservice.ChatBot(*itertools.chain([backend], args, [host, port]))
        bot.start()
    
    storage.close()
    return 0

def authenticator(cid, timestamp, secret):
    window = 100 # token validity in ms
    cur = int(time.time() * 1000)
    timestamp = int(timestamp)
    if not cid in client_params:
        return False
    if cur - window > timestamp or cur + window < timestamp:
        return False
    h = hmac.new(client_params[cid])
    h.update(str(timestamp))
    d = h.hexdigest()
    return hmac.compare_digest(d, str(secret))

if __name__ == "__main__":
    sys.exit(main(*sys.argv[1:]))
