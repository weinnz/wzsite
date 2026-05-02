from django.db import models
import uuid

# Create your models here.
# 目前只用于显示
class Explorer(models.Model):
    LEVEL_CHOICE = (
        (0, "admin"),
        (1, "normal"),
        (2, "guest"),
        )
    
    id = models.CharField(default="", primary_key=True, max_length=20, blank=True)
    name = models.CharField(max_length=100)
    password = models.CharField(max_length=100)
    bio = models.CharField(default="Not lazy, But write nothing.", max_length=200, blank=True, null=True)
    region = models.CharField(default="Earth", max_length=100, blank=True, null=True)
    email = models.CharField(max_length=200)
    phone = models.CharField(max_length=20, blank=True, null=True)
    profile_photo = models.CharField(default="", max_length=200)
    level = models.IntegerField(default=1, choices=LEVEL_CHOICE, editable=False) # 用户权限

    register_time = models.DateTimeField(auto_now_add=True)
    last_login_time = models.DateTimeField(blank=True, null=True)

    def save(self, *args, **kwargs):
        if not self.id:
            user_cnt = int(Explorer.objects.last().id[4:]) + 1
            self.id = f"user{user_cnt:03d}"

        super().save(*args, **kwargs)

    class Meta(object):
        db_table = 'Explorer'
        ordering = ['id']

    def __str__(self):
        return self.name

class Message(models.Model):
    id = models.UUIDField(default=uuid.uuid1, primary_key=True, editable=False)
    profile_icon = models.CharField(max_length=8, default=": )")
    color = models.CharField(max_length=10, default="#000000")

    nickname = models.CharField(max_length=200)
    email = models.EmailField(max_length=200, default="")
    content = models.CharField(max_length=1000)

    level = models.IntegerField(default=0)  # >0 pinned, 0-normal, <0 hidden
    create_time = models.DateTimeField(auto_now_add=True)

    class Meta(object):
        db_table = "Message"
        ordering = ["-level", "-create_time"]


class BGImg(models.Model):
    id = models.AutoField(primary_key=True)
    img_urls = models.TextField()
    backup_img_urls = models.TextField()
    show_number = models.IntegerField(default=3, editable=True)
    total_number = models.IntegerField(default=0, editable=False)
    order = models.IntegerField(default=0, editable=True)

    cat_img_urls = models.TextField(default="")
    cat_says = models.TextField(default="")

    def save(self, *args, **kwargs):
        if not self.id:
            self.id = BGImg.objects.all().count() + 1
        
        self.total_number = len(self.img_urls.strip().split())

        if self.show_number > self.total_number:
            self.show_number = self.total_number
        elif self.show_number < 1:
            self.show_number = 1

        super().save(*args, **kwargs)

    class Meta(object):
        db_table = "bgimg"
        ordering = ["-order"]

class SiteInfo(models.Model):
    id = models.AutoField(primary_key=True)
    title = models.CharField(max_length=100, blank=True)
    name = models.CharField(max_length=100, blank=True)
    signature = models.TextField(blank=True)
    people_cnt = models.BigIntegerField()
    duration_time = models.DurationField()

"""
Notes:
    猫，大海
"""  

