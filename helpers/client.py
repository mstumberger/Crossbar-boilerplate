from autobahn.twisted.wamp import ApplicationSession, ApplicationRunner
from autobahn.wamp.types import SubscribeOptions, RegisterOptions
from autobahn.wamp.auth import derive_key, compute_wcs
from twisted.internet.defer import inlineCallbacks

USER = 'admin'
USER_SECRET = 'adminadmin'

REGISTER_OPTIONS = RegisterOptions(details_arg='details')
SUBSCRIBE_OPTIONS = SubscribeOptions(details_arg='details')


class AppSession(ApplicationSession):
    def onConnect(self):
        self.log.info("Client session connected. "
                      "Starting WAMP-CRA authentication on realm "
                      "'{}' as user '{}' ..".format(
                       self.config.realm, USER))
        self.join(self.config.realm, [u"wampcra"], USER)

    def onChallenge(self, challenge):
        if challenge.method == u"wampcra":
            self.log.debug("WAMP-CRA challenge received: {}".format(challenge))
            if u'salt' in challenge.extra:
                # salted secret
                key = derive_key(USER_SECRET,
                                 challenge.extra['salt'],
                                 challenge.extra['iterations'],
                                 challenge.extra['keylen'])
                # return the signature to the router for verification
                return compute_wcs(key, challenge.extra['challenge'])
        else:
            raise Exception("Invalid authmethod {}".format(challenge.method))

    @inlineCallbacks
    def onJoin(self, details):
        yield self.subscribe(self.handle_message, 'com.example.topic', options=SUBSCRIBE_OPTIONS)

        data = {'username': 'user',
                'name': 'user',
                'surname': 'user',
                'role': 'user',
                'email': 'user@user.user',
                'password': 'user',
                'config': {'user': 'user'}}

        result = yield self.call('com.example.database.create_user', data)
        self.log.info(str(result))

    def handle_message(self, msg, details=None):
        self.log.info(msg)
        self.log.debug(details)


# Start main program
if __name__ == '__main__':
    runner = ApplicationRunner(url=u"ws://localhost:8080/ws", realm=u"realm1")
    runner.run(AppSession, auto_reconnect=True)
