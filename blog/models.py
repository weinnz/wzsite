import uuid
from django.db import models
from web.models import Explorer
import random

emoji_dict = {":sunny:": "&#x2609;",":cloud:": "&#x26C5;",":snowflake:": "&#x2744;",":zap:": "&#x26A1;",":cat:": "&#x1F431;",":dog:": "&#x1F436;",":gift:": "&#x1F381;",":arrow_up:": "&#x2B06;",":arrow_down:": "&#x2B07;",":arrow_left:": "&#x2B05;",":arrow_right:": "&#x27A1;",":arrow_lower_left:": "&#x2934;",":arrow_lower_right:": "&#x2935;",":camera:": "&#x1F4F7;",":camera_flash:": "&#x1F4F8;",":rocket:": "&#x1F680;",":airplane:": "&#x2708;",":alarm_clock:": "&#x23F0;",":bike:": "&#x1F6B2;",":bicyclist:": "&#x1F6B4;",":high_brightness:": "&#x1F506;",":star:": "&#x2B50;",":star2:": "&#x1F31F;",":boom:": "&#x1F4A5;",":anger:": "&#x1F4A2;",":exclamation:": "&#x2757;",":question:": "&#x2753;",":zzz:": "&#x1F4A4;",":dash:": "&#x1F32C;",":notes:": "&#x1F3B6;",":musical_score:": "&#x1F3BC;",":fire:": "&#x1F525;",":rose:": "&#x1F339;",":moneybag:": "&#x1F4B0;",":warning:": "&#x26A0;",":shit:": "&#x1F4A9;",":thumbsup:": "&#x1F44D;",":thumbsdown:": "&#x1F44E;",":v:": "&#x270C;",":pill:": "&#x1F48A;",":date:": "&#x1F4C5;",":calendar:": "&#x1F4C6;",":book:": "&#x1F4D6;",":eyes:": "&#x1F440;",":copyright:": "&#x00A9;",":speech_balloon:": "&#x1F4AC;",":thought_balloon:": "&#x1F4AD;",":bulb:": "&#x1F4A1;",":memo:": "&#x1F4DD;",":o:": "&#x2B55;",":dart:": "&#x1F3AF;",":coffee:": "&#x2615;",":birthday:": "&#x1F382;",":cake:": "&#x1F370;",":joy:": "&#x1F602;",":smile:": "&#x1F600;",":writing_hand:": "&#x270D;",":rainbow:": "&#x1F308;",":balloon:": "&#x1F388;",":fireworks:": "&#x1F386;",":chart_with_downwards_trend:": "&#x1F4C9;",":chart_with_upwards_trend:": "&#x1F4C8;",":bar_chart:": "&#x1F4CA;",":tada:": "&#x1F389;",":paperclip:": "&#x1F4CE;",":mag:": "&#x1F50D;",":mag_right:": "&#x1F50E;",":printer:": "&#x1F5A8;",":no_entry_sign:": "&#x1F6AB;"}

# Create your models here.
class Category(models.Model):
    id = models.AutoField(primary_key=True)
    name = models.CharField(default="", max_length=100)
    name_en = models.CharField(default="", max_length=100, blank=True)
    create_time = models.DateTimeField(auto_now_add=True)

    def save(self, *args, **kwargs):
        if not self.name_en:
            self.name_en = self.name

        super().save(*args, **kwargs)

    class Meta(object):
        db_table = 'Category'
        ordering = ['-name']

    def __str__(self):
        return self.name

class Column(models.Model):
    id = models.AutoField(primary_key=True)
    name = models.CharField(max_length=100)
    name_en = models.CharField(max_length=100, blank=True)
    create_time = models.DateTimeField(auto_now_add=True)

    def save(self, *args, **kwargs):
        if not self.name_en:
            self.name_en = self.name

        super().save(*args, **kwargs)

    class Meta(object):
        db_table = 'Column'
        ordering = ['-name']
    
    def __str__(self):
        return self.name

class Tag(models.Model):
    id = models.AutoField(primary_key=True)
    name = models.CharField(default="", max_length=100)
    name_en = models.CharField(default="", max_length=100, blank=True)
    create_time = models.DateTimeField(auto_now_add=True)

    def save(self, *args, **kwargs):
        if not self.name_en:
            self.name_en = self.name

        super().save(*args, **kwargs)

    class Meta(object):
        db_table = 'Tag'
        ordering = ['-name']  

    def __str__(self):
        return self.name

class Blog(models.Model):
    STATUS_CHOICES = (
        (0, "draft"),
        (1, "published_public"),
        (2, "published_private"),
        (3, "trashed"),
        )

    id = models.CharField(max_length=100, primary_key=True, editable=False, blank=True)
    title = models.CharField(max_length=200, default='')
    user = models.ForeignKey(Explorer, on_delete=models.SET_NULL, null=True)

    abstract = models.TextField(default='')
    content = models.TextField(default='')

    category = models.ForeignKey(Category, on_delete=models.SET_NULL, null=True, blank=True, related_name="blogs")
    columns = models.ManyToManyField(Column, blank=True, related_name="blogs")
    tags = models.ManyToManyField(Tag, blank=True, related_name="blogs")

    status = models.IntegerField(default=1, choices=STATUS_CHOICES)

    views_count = models.IntegerField(default=0, editable=False)
    likes_count = models.IntegerField(default=0, editable=False)
    comments_count = models.IntegerField(default=0, editable=False)
    words_count = models.CharField(max_length=16, default=0, editable=False)
    read_time = models.CharField(max_length=16, default=0, editable=False)
    publish_time = models.DateTimeField(auto_now_add=True, editable=True)
    update_time = models.DateTimeField(auto_now=True)

    def save(self, *args, **kwargs):
        READ_SPEED = 250  # words/min

        words_cnt = self.get_words_cnt(self.content)
        read_t = words_cnt // READ_SPEED
        self.words_count = f"{words_cnt/1000:.1f}k" if words_cnt > 1000 else f"{words_cnt}"
        self.read_time = f"{read_t}"

        self.content = self.emoji(self.content)

        if not self.id:
            while True:
                randn = random.randint(100000, 999999)
                self.id = "AR%d"%randn
                if not Blog.objects.filter(id=self.id).exists():
                    break
        super(Blog, self).save(*args, **kwargs)

    class Meta(object):
        db_table = 'blog'
        ordering = ['-publish_time']

    def __str__(self):
        return self.title
    
    # 行代码里的也会被替换
    @staticmethod
    def emoji_replace(s):
        for k, v in emoji_dict.items():
            s = s.replace(k, v)
        return s

    # 效率不行
    @staticmethod
    def emoji(s):
        p, prev, res = -1, 0, ""
        for n in range(len(s)):
            if s[n] == ":" and p == -1:
                p = n
            elif s[n] == ":" and n > p:
                if s[p:n+1] in emoji_dict.keys():
                    res += s[prev:p] + emoji_dict[s[p:n+1]]
                    p, prev = -1, n+1
                else:
                    res += s[prev:n]
                    p, prev = n, n
        return res + s[prev:]
    
    @staticmethod
    def get_words_cnt(s):
        tmp = ""
        for c in s:
            if "a" <= c <= "z" or "A" <= c <= "Z" or "0" <= c <= "9":
                tmp += c
                pass
            elif "\u4e00" <= c <= "\u9fff":
                tmp += c + " "
            else:
                tmp += " "
        return len(tmp.split())

class BlogComment(models.Model):
    id = models.UUIDField(default=uuid.uuid1, primary_key=True, editable=True)
    profile_icon = models.CharField(max_length=8, default=": )")
    color = models.CharField(max_length=10, default="#000000")
    
    nickname = models.CharField(max_length=100)
    email = models.EmailField(max_length=200, default="")
    blog_id = models.ForeignKey(Blog, on_delete=models.CASCADE, related_name="comments")
    content = models.TextField()
    create_time = models.DateTimeField(auto_now_add=True)

    class Meta(object):
        db_table = "blog_comment"
        ordering = ["create_time"]

class BlogLike(models.Model):
    id = models.UUIDField(default=uuid.uuid1, primary_key=True, editable=False)
    user = models.CharField(default="", max_length=200)
    post = models.ForeignKey(Blog, on_delete=models.CASCADE, related_name="likes")
    create_time = models.DateTimeField(auto_now_add=True)

    class Meta(object):
        db_table = "blog_like"
        ordering = ["create_time"]
