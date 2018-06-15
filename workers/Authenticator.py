from twisted.internet.defer import inlineCallbacks, returnValue
from autobahn.twisted.wamp import ApplicationSession
from autobahn.wamp.exception import ApplicationError


class Authenticator(ApplicationSession):
    @inlineCallbacks
    def onJoin(self, _details):
        @inlineCallbacks
        def authenticate(realm, authid, details):
            self.log.info("WAMP-CRA dynamic authenticator invoked: "
                          "realm='{}', authid='{}', details='{}".
                          format(realm, authid, details))
            try:
                data = yield self.call('com.example.database.get_user', authid)
                if data:
                    algorithm, salt, iterations, keylen, derived = data['password'].split('$')
                    returnValue({'secret': derived,
                                 'salt': salt,
                                 'iterations': int(iterations),
                                 'keylen': int(keylen),
                                 'role': data['role']})
                    return
            except ApplicationError:
                pass
            raise ApplicationError('com.example.no_such_user',
                                   'could not authenticate session '
                                   '- no such user {}'.format(authid))

        try:
            yield self.register(authenticate, u'com.example.authenticate')
            self.log.debug("WAMP-CRA dynamic authenticator registered!")
        except Exception as e:
            self.log.error("Failed to register dynamic authenticator: {0}".format(e))
