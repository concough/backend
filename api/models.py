# coding=utf-8
from django.contrib.auth.models import User
from django.core import validators
from django.db import models
from django.utils import timezone
from django.utils.translation import ugettext_lazy as _


AUTH_TYPE_CHOICES = (('SIGNUP', 'Sign Up'),
                     ('PASS_RECOVERY', 'Password Recovery'),)
GRADE_TYPE_CHOICES = (('BE', "سراسری"),
                     ('ME', "کارشناسی ارشد"),
                      ('NME', 'کاردانی به کارشناسی')
                      )
GENDER_CHOICES = (('M', 'Male'),
                  ('F', 'Female'),
                  ('O', 'Others'))


class PreAuth(models.Model):
    username = models.CharField(
        _('username'),
        max_length=30,
        help_text=_('Required. 30 characters or fewer. Letters, digits and @/./+/-/_ only.'),
        validators=[
            validators.RegexValidator(
                r'^[\w.@+-]+$',
                _('Enter a valid username. This value may contain only '
                  'letters, numbers ' 'and @/./+/-/_ characters.')
            ),
        ],
    )

    email = models.EmailField(null=False)
    created = models.DateTimeField(auto_now_add=True)
    auth_type = models.CharField(max_length=20, choices=AUTH_TYPE_CHOICES, blank=False, null=False)
    approved = models.BooleanField(default=False)
    user_agent_data = models.TextField()
    token = models.CharField(max_length=300)

    class Meta:
        unique_together = ("username", "auth_type")


class Profile(models.Model):
    user = models.OneToOneField(User, related_name="profile")
    grade = models.CharField(max_length=20, null=False, default="BE")
    created = models.DateTimeField(auto_now_add=True)
    modified = models.DateTimeField(auto_now=True)
    gender = models.CharField(max_length=1, choices=GENDER_CHOICES, default="M")
    birthday = models.DateField(null=False)


class UserBugReport(models.Model):
    user = models.ForeignKey(User, related_name="bugs")
    description = models.TextField(max_length=500)
    app_version = models.CharField(max_length=3)
    api_version = models.CharField(max_length=3)
    device_model = models.CharField(max_length=100)
    os_version = models.CharField(max_length=100)
    created = models.DateTimeField(auto_now_add=True)
    replyed = models.BooleanField(default=False)

    def __unicode__(self):
        return "%s: %s" % (self.user, self.description)


class AppVersionRepo(models.Model):
    device = models.CharField(max_length=100)
    version = models.IntegerField(default=1)
    released = models.DateTimeField(auto_now_add=True)

    def __unicode__(self):
        return "%s: %d - %s" % (self.device, self.version, self.released)


class UserRegisteredDevice(models.Model):
    user = models.ForeignKey(User, related_name="devices")
    device_name = models.CharField(max_length=100)
    device_model = models.CharField(max_length=100)
    device_unique_id = models.CharField(max_length=250)
    created = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)
    state = models.BooleanField(default=False)

    class Meta:
        unique_together = ("user", "device_unique_id", "device_name")

    def __unicode__(self):
        return "%s: (%s, %s) - %s" % (self.user, self.device_name, self.device_unique_id, self.state)