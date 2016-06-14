import ssl
import irc.bot
import irc.strings
from cannedresponse import CannedResponse, EmptyResponseError

class ChatBot(irc.bot.SingleServerIRCBot):
    
    def __init__(self, api, chan, nick, server, port=6667):
        if str(port)[0] == "+":
            ssl_factory = irc.connection.Factory(wrapper=ssl.wrap_socket)
            irc.bot.SingleServerIRCBot.__init__(self, [(server, int(port[1:]))], nick, nick, connect_factory=ssl_factory)
        else:
            irc.bot.SingleServerIRCBot.__init__(self, [(server, int(port))], nick, nick)
        self.channel = chan
        self.api = api
        self.canned = CannedResponse("canned.db")
    
    def on_nicknameinuse(self, c, e):
        c.nick(c.get_nickname() + "_")

    def on_welcome(self, c, e):
        c.join(self.channel)

    def on_privmsg(self, c, e):
        self.do_command(e, e.arguments[0])

    def on_pubmsg(self, c, e):
        a = e.arguments[0].split(":", 1)
        if len(a) > 1 and irc.strings.lower(a[0]) == irc.strings.lower(self.connection.get_nickname()):
            a[1] = a[1].strip()
            if a[1][0:4] == "talk":
                r = self.api.handle("fetch", args=a[1][4:].strip())
                c.privmsg(self.channel, r)
            elif a[1][0:6] == "canned":
                parts = a[1][6:].split("->")
                if len(parts) < 2:
                    c.privmsg(self.channel, "usage: canned trigger prefix -> response phrase")
                else:
                    self.canned.add(parts[0].strip(), parts[1].strip())
                    c.privmsg(self.channel, "mapped \"%s\" to \"%s\"" % (parts[0].strip(), parts[1].strip()))
        else:
            self.api.handle("learn", args=e.arguments[0])
            try:
                resp = self.canned.get(e.arguments[0])
                c.privmsg(self.channel, resp)
            except EmptyResponseError:
                pass
