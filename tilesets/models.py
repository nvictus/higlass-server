from __future__ import unicode_literals

import django
import django.contrib.auth.models as dcam
import slugid

from django.db import models
from django.db.models.signals import post_delete
from django.dispatch import receiver


def decoded_slugid():
    return slugid.nice()


class ViewConf(models.Model):
    created = models.DateTimeField(auto_now_add=True)
    higlassVersion = models.CharField(max_length=16, default='')
    uuid = models.CharField(max_length=100, unique=True, default=slugid.nice)
    viewconf = models.TextField()

    class Meta:
        ordering = ('created',)

    def __str__(self):
        '''
        Get a string representation of this model. Hopefully useful for the
        admin interface.
        '''
        return "Viewconf [uuid: {}]".format(self.uuid)


class Project(models.Model):
    created = models.DateTimeField(auto_now_add=True)
    last_viewed_time = models.DateTimeField(default=django.utils.timezone.now)

    owner = models.ForeignKey(
        dcam.User, on_delete=models.CASCADE, blank=True, null=True)
    name = models.TextField(unique=True)
    description = models.TextField(blank=True)
    uuid = models.CharField(max_length=100, unique=True,
                            default=decoded_slugid)
    private = models.BooleanField(default=False)

    class Meta:
        ordering = ('created',)
        permissions = (('read', "Read permission"),
                       ('write', 'Modify tileset'),
                       ('admin', 'Administrator priviliges'),
                       )

    def __str__(self):
        return "Project [name: " + self.name + "]"


class Tileset(models.Model):
    created = models.DateTimeField(auto_now_add=True)

    uuid = models.CharField(max_length=100, unique=True,
                            default=decoded_slugid)

    # processed_file = models.TextField()
    datafile = models.FileField(upload_to='uploads')
    filetype = models.TextField()
    datatype = models.TextField(default='unknown', blank=True, null=True)
    project = models.ForeignKey(Project, on_delete=models.CASCADE,
                                blank=True, null=True)
    description = models.TextField(blank=True)

    coordSystem = models.TextField()
    coordSystem2 = models.TextField(default='', blank=True)
    temporary = models.BooleanField(default=False)

    owner = models.ForeignKey(
        'auth.User', related_name='tilesets', on_delete=models.CASCADE,
        blank=True, null=True  # Allow anonymous owner
    )
    private = models.BooleanField(default=False)
    name = models.TextField(blank=True)

    class Meta:
        ordering = ('created',)
        permissions = (('read', "Read permission"),
                       ('write', 'Modify tileset'),
                       ('admin', 'Administrator priviliges'),
                       )

    def __str__(self):
        '''
        Get a string representation of this model. Hopefully useful for the
        admin interface.
        '''
        return "Tileset [name: {}] [ft: {}] [uuid: {}]".format(
            self.name, self.filetype, self.uuid)


@receiver(post_delete, sender=Tileset)
def tileset_on_delete(sender, instance, **kwargs):

    if not instance.datafile.name.endswith('..'):
        instance.datafile.delete(False)
