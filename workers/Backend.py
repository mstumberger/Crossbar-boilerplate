# Django specific settings
import os
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "settings")
# Ensure settings are read
from django.core.wsgi import get_wsgi_application
application = get_wsgi_application()
from autobahn.twisted.wamp import ApplicationSession, ApplicationRunner
from autobahn.wamp.types import SubscribeOptions, RegisterOptions
from autobahn.wamp.auth import derive_key, generate_wcs
from twisted.internet.defer import inlineCallbacks
from django.db.utils import IntegrityError
from django.conf import settings
from models.User.models import *


class Backend(ApplicationSession):
    REGISTER_OPTIONS = RegisterOptions(details_arg='details')
    SUBSCRIBE_OPTIONS = SubscribeOptions(details_arg='details')

    @inlineCallbacks
    def onJoin(self, details=None):
        self.log.info("Backend component is connected - session ID - {}".format(details.session))

        yield self.subscribe(self.on_session_join, 'wamp.session.on_join')
        yield self.subscribe(self.on_session_leave, 'wamp.session.on_leave')
        yield self.register(self.get_user, 'com.example.database.get_user', options=self.REGISTER_OPTIONS)
        yield self.register(self.get_config, 'com.example.database.get_config', options=self.REGISTER_OPTIONS)
        yield self.register(self.create_user, 'com.example.database.create_user', options=self.REGISTER_OPTIONS)
        yield self.register(self.update_settings, 'com.example.database.update_settings',
                            options=self.REGISTER_OPTIONS)

    @staticmethod
    def get_user(username, details=None):
        try:
            user = UserSerializer(User.objects.get(username__exact=username)).data
            return user
        except User.DoesNotExist:
            return None

    @staticmethod
    def get_config(details=None):
        try:
            return UserSerializer(User.objects.get(username=details.caller_authid)).data['settings']
        except User.DoesNotExist:
            return None

    @staticmethod
    def create_user(data, details=None):
        try:
            # Add user
            salt = generate_wcs(12).decode('utf8')
            user = User(username=data['username'],
                        role=data['role'],
                        password='$'.join([
                            'salted_autobahn_auth',
                            salt,
                            str(settings.ITERATIONS),
                            str(settings.KEYLEN),
                            derive_key(data['password'], salt, settings.ITERATIONS, settings.KEYLEN).decode('ascii')
                        ]),
                        settings={},
                        created_by=details.caller_authid)
            user.save()
            return True
        except IntegrityError as e:
            return str(e)
        except Exception as e:
            return str(e)

    @staticmethod
    def update_settings(settings, details=None):
        try:
            old_settings = User.objects.get(username__exact=details.caller_authid)
            old_settings.settings = settings
            old_settings.save()
            return True
        except User.DoesNotExist:
            return False

    @staticmethod
    def on_session_join(session_details):
        user = session_details['authid']
        role = session_details['authrole']
        session = int(session_details['session'])

        print("User {} with role {} connected with session {}".format(user, role, session))

    @staticmethod
    def on_session_leave(session):
        print(session, "left")


# Start main program
if __name__ == '__main__':
    runner = ApplicationRunner(url="ws://localhost:8080/ws", realm="realm1")

    runner.run(Backend, auto_reconnect=True)
