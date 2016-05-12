import ssl
import irc.bot
import irc.strings

class ChatBot(irc.bot.SingleServerIRCBot):
    
    def __init__(self, learner, composer, chan, nick, server, port=6667):
        if str(port)[0] == "+":
            ssl_factory = irc.connection.Factory(wrapper=ssl.wrap_socket)
            irc.bot.SingleServerIRCBot.__init__(self, [(server, int(port[1:]))], nick, nick, connect_factory=ssl_factory)
        else:
            irc.bot.SingleServerIRCBot.__init__(self, [(server, int(port))], nick, nick)
        self.channel = chan
        self.learner = learner
        self.composer = composer
    
    def on_nicknameinuse(self, c, e):
        c.nick(c.get_nickname() + "_")

    def on_welcome(self, c, e):
        c.join(self.channel)

    def on_privmsg(self, c, e):
        self.do_command(e, e.arguments[0])

    def on_pubmsg(self, c, e):
        a = e.arguments[0].split(":", 1)
        if len(a) > 1 and irc.strings.lower(a[0]) == irc.strings.lower(self.connection.get_nickname()):
            if a[1].strip() == "talk":
                c.privmsg(self.channel, self.composer.generate())
        else:
            self.learner.learn(e.arguments[0])
