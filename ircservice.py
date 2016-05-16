import ssl
import irc.bot
import irc.strings

class ChatBot(irc.bot.SingleServerIRCBot):
    
    def __init__(self, api, chan, nick, server, port=6667):
        if str(port)[0] == "+":
            ssl_factory = irc.connection.Factory(wrapper=ssl.wrap_socket)
            irc.bot.SingleServerIRCBot.__init__(self, [(server, int(port[1:]))], nick, nick, connect_factory=ssl_factory)
        else:
            irc.bot.SingleServerIRCBot.__init__(self, [(server, int(port))], nick, nick)
        self.channel = chan
        self.api = api
    
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
        else:
            self.api.handle("learn", args=e.arguments[0])
