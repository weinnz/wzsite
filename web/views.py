from django import forms
from django.http import JsonResponse
from django.shortcuts import render
from django.views.decorators.csrf import csrf_exempt
import time
import random
from django.conf import settings
from pathlib import Path
from datetime import datetime
from mysite.settings import COLOR_LIST, EMOJI_LIST
from django.utils.safestring import mark_safe
from django.db.models import F


# 定时任务
from apscheduler.schedulers.background import BackgroundScheduler
from django.db import close_old_connections

from web.models import Message
class MessageForm(forms.ModelForm):
    class Meta:
        model = Message
        fields = ['nickname', 'email', 'content', 'level']
        widgets = {
            'nickname': forms.TextInput(attrs={'id': 'nickname', 'placeholder': '昵称'}),
            'email': forms.EmailInput(attrs={'id': 'usremail', 'placeholder': '邮箱'}),
            'content': forms.Textarea(attrs={'id': 'input-area', 'placeholder': 'Say something', 'rows': 4}),
        }

from blog.models import Blog
from notes.models import Reading_Notes, Travel_Notes, Life_Notes
def scheduler_test():
    fpaths = sorted([str(k) for k in (settings.BASE_DIR / "logs").rglob("views.log.*-*")])
    if len(fpaths) > 1 and fpaths[-2] != settings.LOG_FNAME:
        settings.LOG_FNAME = fpaths[-2]
        # 数据分析
        blog_views_cnt = {}
        with open(fpaths[-2], "r", encoding="utf-8") as fp:
            content = fp.read().strip().split("\n")
        for k in content:
            if len(k) == 0:
                continue
            funcname, datestr, guestid, blogid = k.split()
            tm = datetime.strptime(datestr, "%Y-%m-%d-%H-%M-%S").timestamp() // 60
            name = f"{guestid}-{blogid}"
            if name not in blog_views_cnt.keys():
                blog_views_cnt[name] = set()
            blog_views_cnt[name].add(tm)
        for k, v in blog_views_cnt.items():
            _id = k.split("-")[-1]
            _cnt = len(v)
            print(_id, _cnt)
            if _id.lower().startswith("ar"):
                close_old_connections()
                blog = Blog.objects.filter(id=_id).update(views_count = F('views_count') + _cnt)

            elif _id.lower().startswith("rn"):
                close_old_connections()
                note = Reading_Notes.objects.filter(id=_id).update(views_count = F('views_count') + _cnt)

            elif _id.lower().startswith("tn"):
                close_old_connections()
                note = Travel_Notes.objects.filter(id=_id).update(views_count = F('views_count') + _cnt)

            elif _id.lower().startswith("ln"):
                close_old_connections()
                note = Life_Notes.objects.filter(id=_id).update(views_count = F('views_count') + _cnt)           
                
    print('定时任务触发')

# BackgroundScheduler() 调度器在后台执行，不会阻塞当前进程。
#executors = {
#    'default': ProcessPoolExecutor(5)
#}
job_defaults = {
    'coalesce': True,
    'misfire_grace_time': None
}

scheduler = BackgroundScheduler(job_defaults=job_defaults)
try:
# 添加定时任务，第一个参数为需要定时执行的任务，'interval'定时任务类型，每隔900秒执行一次，任务id为test。
	scheduler.add_job(scheduler_test, 'interval', minutes=20, id='analysisviewnum', replace_existing=True)
    # 启动定时任务
	scheduler.start()
except Exception as e:
    print("Error:", e)
    # 停止定时任务
    scheduler.shutdown()


# Create your views here.
from web.models import BGImg, SiteInfo, Message

# 主页
def index(request):
    random.seed((time.time() + 28800)//86400)

    obj = BGImg.objects.all().first()
    imgs_url = [k for k in obj.img_urls.strip().split() if (not k.strip().startswith("#")) and k.strip()]
    backup_imgs_url = [k for k in obj.backup_img_urls.strip().split() if (not k.strip().startswith("#")) and k.strip()]
    imgs = [(settings.CDN_URL + k1, k2) for k1, k2 in zip(random.sample(imgs_url, obj.show_number), random.sample(backup_imgs_url, obj.show_number))]

    info = SiteInfo.objects.all().first()
    signatures = info.signature.strip().split("\n")
    signature = random.choice(signatures)
    spacing = 0.15 if len(signature) > 25 else 0.3

    return render(request, "index.html", {"siteinfo": info,"imgs": imgs, "signature": signature, "spacing": spacing})

@csrf_exempt
def handler404(request, exception):
    return render(request, '404.html')


# contact
def contact(request):
    message_form = MessageForm()
    message = Message.objects.filter(level__gte=0).order_by("-level", "-create_time")

    return render(request, "contact.html", {"message_form": message_form, "messages": message, "message_cnt": Message.objects.filter(level__gte=0).count()})

@csrf_exempt
def leave_message(request):
    if request.method != "POST":
        return JsonResponse({"error": "Invalid request method."}, status=400)

    # print(request.POST)
    form = MessageForm(request.POST)
    if not form.is_valid():
        return JsonResponse({"status": False, "error": form.errors})
    else:
        # print(form.instance.level)
        time.sleep(random.uniform(1.5, 5.5))  # 模拟网络延迟
        if form.instance.level == -1:
            form.instance.level = -1  # 强制设为隐藏
            return JsonResponse({"status": True, "message_html": "", "message_cnt": Message.objects.filter(level__gte=0).count()})
        else:
            form.instance.level = 0  # 正常评论


        form.instance.profile_icon = random.choice(EMOJI_LIST)
        form.instance.color = random.choice(COLOR_LIST)
        form.save()

        # string = f'''<div class="comment-item">
        #             <div class="comment-item-header">
        #             <div class="c-photo" style="background-color: {form.instance.color};">{form.instance.profile_icon}</div>
        #             <div class="c-info">
        #             <div class="c-info-nickname">{form.instance.nickname}</div>
        #             <div class="c-info-t">{form.instance.create_time.strftime("%Y-%m-%d %H:%M:%S")}</div>
        #             </div>
        #             </div>
        #             <div class="comment-text">{form.instance.content}</div>
        #             </div>
        #         '''
        
        string = f'''<div class="message-item">
            <div class="g-header">
              <div class="g-header-left">
              <div class="g-photo" style="background-color: { form.instance.color };" >{form.instance.profile_icon}</div>
              <div class="g-info">
                <div class="g-info-nickname">{form.instance.nickname}</div>
                <div class="g-info-t">{form.instance.create_time.strftime("%Y-%m-%d %H:%M:%S")}</div>
              </div>
            </div>
              <div class="g-header-right">
                  <span style="padding-bottom: 10px;"> :your message:</span>
              </div>

            </div>
            <div>{form.instance.content}</div>
          </div>
        '''

    return JsonResponse({"status": True, "message_html": mark_safe(string), "message_cnt": Message.objects.filter(level__gte=0).count()})


# research
def search(request):

    return render(request, "search.html")
