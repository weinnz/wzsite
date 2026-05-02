import logging
import random
from django import forms
from django.shortcuts import render
from django.utils.safestring import mark_safe
import uuid
import time
from mysite.settings import COLOR_LIST, EMOJI_LIST
from django.db.models import F

import mistune
#from mistune.util import escape as escape_text
# extended plugins
from mistune.plugins.formatting import strikethrough # 删除线
from mistune.plugins.footnotes import footnotes # 脚注
from mistune.plugins.table import table # 表格 !important
from mistune.plugins.url import url # 自动 url
from mistune.plugins.task_lists import task_lists # 任务列表
from mistune.plugins.formatting import mark # 高亮
from mistune.plugins.formatting import superscript # 上标
from mistune.plugins.formatting import subscript # 下标
from mistune.plugins.math import math # 公式 !important
from mistune.directives import RSTDirective, TableOfContents # 目录 !important

from notes.models import Reading_Notes, Travel_Notes, Life_Notes, ReadingNoteComment, TravelNoteComment, LifeNoteComment
from django.http import JsonResponse
from notes.models import ReadingNoteLike, TravelNoteLike, LifeNoteLike
from django.views.decorators.csrf import csrf_exempt
class ReadingNoteCommentForm(forms.ModelForm):
    class Meta:
        model = ReadingNoteComment
        fields = ['nickname', 'email', 'content']
        widgets = {
            'nickname': forms.TextInput(attrs={'id': 'nickname', 'placeholder': 'Nickname'}),
            'email': forms.EmailInput(attrs={'id': 'email', 'placeholder': 'Email'}),
            'content': forms.Textarea(attrs={'id': 'input-area', 'placeholder': 'Your comment', 'rows': 4}),
        } 
class TravelNoteCommentForm(forms.ModelForm):
    class Meta:
        model = TravelNoteComment
        fields = ['nickname', 'email', 'content']
        widgets = {
            'nickname': forms.TextInput(attrs={'id': 'nickname', 'placeholder': 'Nickname'}),
            'email': forms.EmailInput(attrs={'id': 'email', 'placeholder': 'Email'}),
            'content': forms.Textarea(attrs={'id': 'input-area', 'placeholder': 'Your comment', 'rows': 4}),
        }
class LifeNoteCommentForm(forms.ModelForm):
    class Meta:
        model = LifeNoteComment
        fields = ['nickname', 'email', 'content']
        widgets = {
            'nickname': forms.TextInput(attrs={'id': 'nickname', 'placeholder': 'Nickname'}),
            'email': forms.EmailInput(attrs={'id': 'email', 'placeholder': 'Email'}),
            'content': forms.Textarea(attrs={'id': 'input-area', 'placeholder': 'Your comment', 'rows': 4}),
        }

# Create your views here.
# from notes.models import Sheet_Music

def notes(request):

    reading_notes_list = Reading_Notes.objects.all()
    travel_notes_list = Travel_Notes.objects.all()
    life_notes_list = Life_Notes.objects.all()

    return render(request, 'notes.html', {'reading_notes': reading_notes_list, "travel_notes": travel_notes_list, "life_notes": life_notes_list})


logger = logging.getLogger("request")
def note_detail(request, note_id):

    if note_id.lower().startswith("rn"):
        note_info = Reading_Notes.objects.filter(id=note_id).first()
    elif note_id.lower().startswith("tn"):
        note_info = Travel_Notes.objects.filter(id=note_id).first()
    elif note_id.lower().startswith("ln"):
        note_info = Life_Notes.objects.filter(id=note_id).first()

    renderer = mistune.HTMLRenderer(escape=False)
    markdown = mistune.create_markdown(hard_wrap=True, renderer = renderer, plugins=[strikethrough, footnotes, table, url, task_lists, mark,\
                                                      superscript, subscript, math, RSTDirective([TableOfContents()])])
    html_txt = markdown(note_info.content.replace("\r\n\r\n\r\n\r\n", "\r\n\r\n<br />\r\n\r\n").replace("\n\n\n\n", "\n\n<br />\n\n"))

    guestid = request.COOKIES.get("weinnzguestid")
        # guestid = uuid.uuid4()
        # like_fill = "none"
        # response.set_cookie("weinnzguestid", guestid, max_age=100*24*60*60)
    if note_id.lower().startswith("rn"):
        comment_form = ReadingNoteCommentForm()
        comment = ReadingNoteComment.objects.filter(note_id=note_info).order_by("-create_time")
        if guestid is None or ReadingNoteLike.objects.filter(user=guestid, post=note_id).count() == 0:
            like_fill = "none"
        else:
            like_fill = "#880000"
    elif note_id.lower().startswith("tn"):
        comment_form = TravelNoteCommentForm()
        comment = TravelNoteComment.objects.filter(note_id=note_info).order_by("-create_time")

        if guestid is None or TravelNoteLike.objects.filter(user=guestid, post=note_id).count() == 0:
            like_fill = "none"
        else:
            like_fill = "#880000"
    
    elif note_id.lower().startswith("ln"):
        comment_form = LifeNoteCommentForm()
        comment = LifeNoteComment.objects.filter(note_id=note_info).order_by("-create_time")

        if guestid is None or LifeNoteLike.objects.filter(user=guestid, post=note_id).count() == 0:
            like_fill = "none"
        else:
            like_fill = "#880000"

    logger.info(f"{guestid} {note_id}") 
    
    return render(request, "note_detail.html", {"note": note_info, "note_content": html_txt, "like_fill": like_fill, "comments": comment, "comment_form": comment_form})

@csrf_exempt
def like_toggle(request):
    if request.method != "POST":
        return JsonResponse({"error": "Invalid request method."}, status=400)

    note_id = request.POST.get("note_id", "")
    guestid = request.COOKIES.get("weinnzguestid", str(uuid.uuid4()))

    if note_id.lower().startswith("rn"):
        like_obj = Reading_Notes.objects.get(id=note_id).likes.filter(user=guestid).first()
        if like_obj is None:
            Reading_Notes.objects.filter(id=note_id).update(likes_count = F('likes_count') + 1)
            note = Reading_Notes.objects.filter(id=note_id).first()
            ReadingNoteLike.objects.create(user=guestid, post=note)

            response = JsonResponse({"like_fill": "var(--usr-theme)", "likes_count": note.likes_count})
        else:
            like_obj.delete()
            Reading_Notes.objects.filter(id=note_id).update(likes_count = F('likes_count') - 1)
            note = Reading_Notes.objects.filter(id=note_id).first()

            response = JsonResponse({"like_fill": "none", "likes_count": note.likes_count})


    elif note_id.lower().startswith("tn"):
        like_obj = Travel_Notes.objects.get(id=note_id).likes.filter(user=guestid).first()
        if like_obj is None:
            Travel_Notes.objects.filter(id=note_id).update(likes_count = F('likes_count') + 1)
            note = Travel_Notes.objects.filter(id=note_id).first()
            TravelNoteLike.objects.create(user=guestid, post=note)

            response = JsonResponse({"like_fill": "#880000", "likes_count": note.likes_count})
        else:
            like_obj.delete()
            Travel_Notes.objects.filter(id=note_id).update(likes_count = F('likes_count') - 1)
            note = Travel_Notes.objects.filter(id=note_id).first()

            response = JsonResponse({"like_fill": "none", "likes_count": note.likes_count})


    elif note_id.lower().startswith("ln"):
        like_obj = Life_Notes.objects.get(id=note_id).likes.filter(user=guestid).first()
        if like_obj is None:
            Life_Notes.objects.filter(id=note_id).update(likes_count = F('likes_count') + 1)
            note = Life_Notes.objects.filter(id=note_id).first()
            LifeNoteLike.objects.create(user=guestid, post=note)

            response = JsonResponse({"like_fill": "#880000", "likes_count": note.likes_count})
        else:
            like_obj.delete()
            Life_Notes.objects.filter(id=note_id).update(likes_count = F('likes_count') - 1)
            note = Life_Notes.objects.filter(id=note_id).first()

            response = JsonResponse({"like_fill": "none", "likes_count": note.likes_count})
    
    response.set_cookie("weinnzguestid", guestid, max_age=100*24*60*60)
    return response

@csrf_exempt
def post_comment(request):
    if request.method != "POST":
        return JsonResponse({"error": "Invalid request method."}, status=400)

    _id = request.POST["note_id"]
    if _id.lower().startswith("rn"):
        form = ReadingNoteCommentForm(data = request.POST)
    elif _id.lower().startswith("tn"):
        form = TravelNoteCommentForm(data = request.POST)
    elif _id.lower().startswith("ln"):
        form = LifeNoteCommentForm(data = request.POST)
    
    if not form.is_valid():
        return JsonResponse({"status": False, "error": form.errors})
    else:
        time.sleep(random.uniform(1.5, 5.5))  # 模拟网络延迟

        if _id.lower().startswith("rn"):
            Reading_Notes.objects.filter(id=_id).update(comments_count = F('comments_count') + 1)
            note = Reading_Notes.objects.filter(id=_id).first()
        elif _id.lower().startswith("tn"):
            Travel_Notes.objects.filter(id=_id).update(comments_count = F('comments_count') + 1)
            note = Travel_Notes.objects.filter(id=_id).first()
        elif _id.lower().startswith("ln"):
            Life_Notes.objects.filter(id=_id).update(comments_count = F('comments_count') + 1)
            note = Life_Notes.objects.filter(id=_id).first()

        form.instance.profile_icon = random.choice(EMOJI_LIST)
        form.instance.color = random.choice(COLOR_LIST)
        form.instance.note_id = note
        form.save()

        string = f'''<div class="comment-item">
                    <div class="comment-item-header">
                    <div class="c-photo" style="background-color: {form.instance.color};">{form.instance.profile_icon}</div>
                    <div class="c-info">
                    <div class="c-info-nickname">{form.instance.nickname}</div>
                    <div class="c-info-t">{form.instance.create_time.strftime("%Y-%m-%d %H:%M:%S")}</div>
                    </div>
                    </div>
                    <div class="comment-text">{form.instance.content}</div>
                    </div>
                '''

    return JsonResponse({"status": True, "comment_html": mark_safe(string), "comments_count": note.comments_count})
