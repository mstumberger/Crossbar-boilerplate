import sys
try:
    from django.contrib.auth.models import BaseUserManager, AbstractBaseUser
    from django.contrib.postgres.fields import JSONField
    from rest_framework import serializers
    from django.db import models
    " https://docs.djangoproject.com/en/2.0/ref/contrib/postgres/fields/#jsonfield "
except Exception as e:
    print("There was an error loading django modules. Do you have django installed?", e)
    sys.exit()


class UserManager(BaseUserManager):
    def create_user(self, username, password, name, surname, role):
        user = self.model(
            username=username,
            name=name,
            surname=surname,
            role=role,
            settings={}
        )
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, username, password, name='', surname=''):
        u = self.create_user(
            username=username,
            password=password,
            name=name,
            surname=surname,
            role='admin'
        )
        u.superuser = True
        u.staff = True
        u.is_active = True
        u.save(using=self._db)
        return u


# Sample User model
class User(AbstractBaseUser):
    class Meta:
        verbose_name_plural = "Users"
        verbose_name = "user"

    username = models.CharField(max_length=255, unique=True)
    name = models.CharField(max_length=255)
    surname = models.CharField(max_length=255)
    TYPES = (
        ('admin', 'admin'),
        ('user', 'user'),
    )
    role = models.CharField(choices=TYPES, max_length=155, default='user')
    staff = models.BooleanField(default=False)
    superuser = models.BooleanField(default=False)
    email = models.EmailField(max_length=255)
    password = models.CharField(max_length=255)
    registered = models.DateTimeField(auto_now_add=True)
    settings = JSONField()
    created_by = models.CharField(max_length=255)

    USERNAME_FIELD = 'username'
    objects = UserManager()

    REQUIRED_FIELDS = []

    def get_full_name(self):
        return self.username

    def get_short_name(self):
        return self.username

    def __unicode__(self):
        return self.username

    def has_perm(self, perm, obj=None):
        return True

    def has_module_perms(self, app_label):
        return True

    @property
    def is_staff(self):
        return self.staff

    @property
    def is_superuser(self):
        return self.superuser


class UserSerializer(serializers.ModelSerializer):

    password = serializers.CharField(required=False)

    class Meta:
        model = User
        fields = '__all__'


class SettingsSerializer(serializers.ModelSerializer):

    class Meta:
        model = User.settings
        fields = '__all__'
