import httplib, sys, time, hmac, json

CLIENT_ID     = "test-client"
CLIENT_SECRET = "test-client"

def get_secret(timestamp):
    h = hmac.new(CLIENT_SECRET)
    h.update(timestamp)
    return h.hexdigest()

def main(host="localhost", port="7000"):
    port = int(port)
    
    conn = httplib.HTTPConnection(host, port)
    
    timestamp = "%d" % int(time.time() * 1000)
    
    request = {
        'timestamp':     timestamp,
        'client-id':     CLIENT_ID,
        'client-hmac':   get_secret(timestamp),
        'body': {
            'method': 'fetch',
            'params': {
                'composer': 'SeededTreeComposer'
            }
        }
    }
    
    conn.request("POST", "/", json.dumps(request), {'content-type': 'application/json'})
    resp = conn.getresponse().read()
    conn.close()

    print(resp)
    
    return 0

if __name__ == "__main__":
    sys.exit(main(*sys.argv[1:]))
