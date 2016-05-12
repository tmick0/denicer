import sys, hmac, time
import dchat, api, httpservice

client_params = {
    'test-client': 'test-client'
}

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

def main():
    storage = dchat.storage.SqliteBackend("brain.db")
    backend = api.LockingApi(api.DictionaryApi(storage, authenticator))
    httpservice.listen(('localhost', 7002), backend)
    storage.close()

if __name__ == "__main__":
    sys.exit(main(*sys.argv[1:]))
