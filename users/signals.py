from .models import Profile
from django.contrib.auth.models import User
from django.db.models.signals import post_save,post_delete
from django.dispatch import receiver


def CreateProfile(sender,instance, created, **kwargs):
    if created:
        user = instance
        profile = Profile.objects.create(
            user = user,
            username = user.username,
            email = user.email,
            name = user.first_name,
        )

def DeleteUser(sender,instance,**kwargs):
    user = instance.user
    user.delete()

post_save.connect(CreateProfile,sender=User)
post_delete.connect(DeleteUser,sender=Profile)