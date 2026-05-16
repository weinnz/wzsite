from django.db import models
import uuid
import random

# Create your models here.
class Gallery(models.Model):
    STATUS_CHOICES = (
            (0, "draft"),
            (1, "public"),
            (2, "private"),
            (3, "trash"),
            )
    id = models.CharField(max_length=32, primary_key=True, editable=False, blank=True)
    title = models.CharField(max_length=10, default='')
    cover_description = models.TextField(default="", blank=True, null=True)
    detail_description = models.TextField(default="", blank=True, null=True)

    location = models.CharField(max_length=100, default='')
    camera = models.CharField(max_length=100, default='', blank=True, null=True)
    number = models.IntegerField(default=0, blank=True, null=True)
    author = models.CharField(max_length=100, blank=True, null=True)

    cover = models.CharField(max_length=255, default='', blank=True, null=True)
    url = models.TextField(default='')
    create_time = models.DateTimeField(auto_now_add=True)
    status = models.IntegerField(default=1, choices=STATUS_CHOICES)

    def save(self, *args, **kwargs):
        if not self.id:
            cnt = Gallery.objects.filter(id__startswith = self.title).count() + 1
            if cnt == 1:
                self.id = f"GA{self.title}"
            else:
                self.id = f"GA{self.title}.{cnt}"

        urls = [k for k in self.url.strip().split("\n") if (not k.strip().startswith("#")) and k.strip()]
        self.number = len(urls)

        if not self.camera:
            self.camera = "Sony A7CII"
        
        if not self.author:
            self.author = "zhangwei"

        if not self.cover:
            self.cover = self.url.strip().split("\n")[0]

        super().save(*args, **kwargs)

    class Meta(object):
        db_table = 'gallery'
        ordering = ['-title']

    def __str__(self):
        return self.title
