import random
import time
from django.shortcuts import render, HttpResponse
from blog.models import Blog, Category, Column, Tag, BlogComment, BlogLike
from django.views.decorators.csrf import csrf_protect, csrf_exempt
from web.models import Explorer, BGImg
import uuid
from django.utils.safestring import mark_safe
from mysite.settings import BLOG_ITEM_NUM_PER_PAGE, COLOR_LIST, EMOJI_LIST
from django.http import JsonResponse
from django import forms
from django.db.models import F

import logging

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

import random
from utils.generate_captcha import generate_captcha as check_code

class BlogCommentForm(forms.ModelForm):
    class Meta:
        model = BlogComment
        fields = ['nickname', 'email', 'content']
        widgets = {
            'nickname': forms.TextInput(attrs={'id': 'nickname', 'placeholder': '你的昵称'}),
            'email': forms.EmailInput(attrs={'id': 'email', 'placeholder': '你的邮箱'}),
            'content': forms.Textarea(attrs={'id': 'input-area', 'placeholder': 'Your idea or thought about this blog\'s content.', 'rows': 4}),
        }

# 扩展可显示的目录层级
class myTableOfContents(TableOfContents):
    def __init__(self, min_level: int = 1, max_level: int = 4) -> None:
        self.min_level = min_level
        self.max_level = max_level

    # def generate_heading_id(self, token, index) -> str:
    #     return token["text"]
"""
class myHTMLRenderer(mistune.HTMLRenderer):
    def block_code(self, code: str, info: None) -> str:
        code = "".join([f"<div>{escape_text(line)}</div>" for line in code.splitlines(True)])
        html = "<pre><code"
        if info is not None:
            info = info.strip()
        if info:
            lang = info.split(None, 1)[0]
            html += ' class="language-' + lang + '"'
        return html + ">" + code + "</code></pre>\n"
"""

logger = logging.getLogger("request")

# Create your views here.
def blog(request):
    sort_items = {"Recent":"choice", "Earlier":"", "Title a-z": "", "Title z-a":"", "Most views": "", "Fewest views": "", "Most likes": "", "Fewest likes": ""}

    page = int(request.POST.get("page", 1))
    page_size = BLOG_ITEM_NUM_PER_PAGE
    start = (page - 1) * page_size
    end = page * page_size

    #query_set = Blog.objects.all()
    query_set = Blog.objects.filter(status=1)
    total_cnt = query_set.count()
    total_page_cnt, div = divmod(total_cnt, page_size)
    if div:
        total_page_cnt += 1
    
    if total_page_cnt == 1:
        page_nav = ""
    elif page == 1 or page > total_page_cnt:
        page_nav = f"<span></span> <span id='page_n'>1 / {total_page_cnt}</span> <span id='next'>>></span>"
    elif page == total_page_cnt:
        page_nav = f"<span id='prev'><<</span> <span id='page_n'>{page} / {total_page_cnt}</span> <span></span>"
    else:
        page_nav = f"<span id='prev'><<</span> <span id='page_n'>{page} / {total_page_cnt}</span> <span id='next'>>></span>"


    # 类别相关列表，用于顶部菜单显示
    category_list = Category.objects.all()
    column_list = Column.objects.all()
    tag_list = Tag.objects.all()

    # 博客内容列表
    blog_list = query_set[start:end]
    blog_category_list = [obj.category.name for obj in blog_list if obj.category]
    blog_columns_list = [[k.name for k in obj.columns.all()] for obj in blog_list]
    blog_tags_list = [[k.name for k in obj.tags.all()] for obj in blog_list if obj]

    return render(request, "blog.html", {"category_list": category_list, "column_list": column_list, "tag_list": tag_list, "blog_list": zip(blog_list, blog_category_list, blog_columns_list, blog_tags_list), "num": len(blog_list), "page_nav": mark_safe(page_nav), "sort_items": zip(sort_items.keys(), sort_items.values())})

@csrf_exempt
def get_blog(request):
    if request.method != "POST":
        return JsonResponse({"error": "Invalid request method."}, status=400)

    sort_items = {"Recent":"", "Earlier":"", "Title a-z": "", "Title z-a":"", "Most views": "", "Fewest views": "", "Most likes": "", "Fewest likes": ""}

    task = request.POST.get("task")
    type1 = request.POST.get("type1")
    type2 = request.POST.get("type2")
    lang = "zh-cn"
    page = int(request.POST.get("page", "1").split()[0])
    sort_by = request.POST.get("sort", "recent")
    if type1.lower() == "articles" and type2.lower() == "all":
        #query_set = Blog.objects.all()
        query_set = Blog.objects.filter(status=1)
        # blog_category_list = [obj.category.name for obj in blog_list if obj.category]
        # blog_columns_list = [[k.name for k in obj.columns.all()] for obj in blog_list]
        # blog_tags_list = [[k.name for k in obj.tags.all()] for obj in blog_list]
        
    elif type1.lower() == "articles": 
        obj = Category.objects.get(name = type2)
        #type1 = "文章"
        #query_set = obj.blogs.all()
        query_set = obj.blogs.filter(status=1)
    elif type1.lower() == "columns":
        obj = Column.objects.get(name = type2)
        #type1 = "专栏"
        #query_set = obj.blogs.all()
        query_set = obj.blogs.filter(status=1)
    elif type1.lower() == "tags":
        obj = Tag.objects.get(name = type2)
        #type1 = "标签"
        #query_set = obj.blogs.all()
        query_set = obj.blogs.filter(status=1)

    # blog_category_list = [obj.category.name for obj in blog_list]
    # blog_columns_list = [[k.name for k in obj.columns.all()] for obj in blog_list]
    # blog_tags_list = [[k.name for k in obj.tags.all()] for obj in blog_list]
    if task.lower() == "prev":
        page -= 1
    elif task.lower() == "next":
        page += 1

    page_size = BLOG_ITEM_NUM_PER_PAGE
    start = (page - 1) * page_size
    end = page * page_size

    total_cnt = query_set.count()
    total_page_cnt, div = divmod(total_cnt, page_size)
    if div:
        total_page_cnt += 1

    if total_page_cnt == 1:
        page_nav = ""
    elif page == 1:
        page_nav = f"<span></span> <span id='page_n'>1 / {total_page_cnt}</span> <span id='next'>>></span>"
    elif page == total_page_cnt:
        page_nav = f"<span id='prev'><<</span> <span id='page_n'>{page} / {total_page_cnt}</span> <span></span>"
    else:
        page_nav = f"<span id='prev'><<</span> <span id='page_n'>{page} / {total_page_cnt}</span> <span id='next'>>></span>"

    # if sort_by.lower() == "recent":
    #     query_set = query_set.order_by("publish_time")
    if sort_by.lower() == "earlier":
        query_set = query_set.order_by("publish_time")
    elif sort_by.lower() == "title a-z":
        query_set = query_set.order_by("title")
    elif sort_by.lower() == "title z-a":
        query_set = query_set.order_by("-title")
    elif sort_by.lower() == "most views":
        query_set = query_set.order_by("-views_count")
    elif sort_by.lower() == "fewest views":
        query_set = query_set.order_by("views_count")
    elif sort_by.lower() == "most likes":
        query_set = query_set.order_by("-likes_count")
    elif sort_by.lower() == "fewest likes":
        query_set = query_set.order_by("likes_count")
    else:
        query_set = query_set.order_by("-publish_time")
    sort_items[sort_by.capitalize()] = "choice"

    blog_list = query_set[start:end]  # 未增加filter
    blog_category_list = [obj.category.name for obj in blog_list if obj.category]
    blog_columns_list = [[k.name for k in obj.columns.all()] for obj in blog_list]
    blog_tags_list = [[k.name for k in obj.tags.all()] for obj in blog_list]

    return render(request, "blog_area_div.html", {"type1": type1, "type2": type2, "sort_by": sort_by, "sort_items": zip(sort_items.keys(), sort_items.values()) ,"blog_list": zip(blog_list, blog_category_list, blog_columns_list, blog_tags_list), "num": len(blog_list), "page_nav": mark_safe(page_nav)})

# 详情页
def blog_detail(request, blog_id):
    blog = Blog.objects.filter(id=blog_id).first()
    renderer = mistune.HTMLRenderer(escape=False)
    markdown = mistune.create_markdown(hard_wrap=False, renderer = renderer, plugins=[strikethrough, footnotes, table, url, task_lists, mark,\
                                                      superscript, subscript, math, RSTDirective([myTableOfContents()])])
    
    html_txt = markdown((".. toc::\n\n" + blog.content.replace("\r\n\r\n\r\n\r\n", "\r\n\r\n<br />\r\n\r\n").replace("\n\n\n\n","\n\n<br />\n\n")))
    #html_txt = markdown((".. toc::\n\n" + blog.content))
    html_txt = html_txt.replace('<table>', '<div class="table-wrapper"><table>').replace('</table>', '</table></div>')
    toc0, _, blog.content = html_txt.partition("</details>")
    _, _, toc = toc0.partition("</summary>")
    toc = '<div class="toc">' + toc + '</div>'

    blog_comment_form = BlogCommentForm()
    blog_comment = BlogComment.objects.filter(blog_id=blog).order_by("-create_time")
    # BlogLike.objects.get_or_create(user=request.COOKIES.get("weinnzguestid", ""), post=blog_id)
    # blog.views_count += 1
    # blog.save())

    # response = render(request, "blog_detail.html", {"author": blog.user, "toc": toc, "details": blog})
    guestid = request.COOKIES.get("weinnzguestid")
        # guestid = uuid.uuid4()
        # like_fill = "none"
        # response.set_cookie("weinnzguestid", guestid, max_age=100*24*60*60)
    if guestid is None or BlogLike.objects.filter(user=guestid, post=blog_id).count() == 0:
        like_fill = "none"
    else:
        like_fill = "var(--usr-theme)"

    logger.info(f"{guestid} {blog_id}")

    CAT_IMG = BGImg.objects.all().first().cat_img_urls.strip().split("\n")
    CAT_SAY = BGImg.objects.all().first().cat_says.strip().split("\n")
    return render(request, "blog_detail.html", {"author": blog.user, "toc": toc, "details": blog, "like_fill": like_fill, "comments": blog_comment, "comment_form": blog_comment_form,"cat_url": random.choice(CAT_IMG), "cat_say": random.choice(CAT_SAY)})

@csrf_exempt
def like_toggle(request):
    if request.method != "POST":
        return JsonResponse({"error": "Invalid request method."}, status=400)

    blog_id = request.POST.get("blog_id", "")
    guestid = request.COOKIES.get("weinnzguestid", str(uuid.uuid4()))


    like_obj = Blog.objects.get(id=blog_id).likes.filter(user=guestid).first()
    #like_obj = BlogLike.objects.filter(user=guestid, post=blog_id).first()
    if like_obj is None:
        Blog.objects.filter(id=blog_id).update(likes_count = F('likes_count') + 1)
        blog = Blog.objects.filter(id=blog_id).first()
        BlogLike.objects.create(user=guestid, post=blog)

        response = JsonResponse({"like_fill": "var(--usr-theme)", "likes_count": blog.likes_count})
    else:
        like_obj.delete()
        Blog.objects.filter(id=blog_id).update(likes_count = F('likes_count') - 1)
        blog = Blog.objects.filter(id=blog_id).first()

        response = JsonResponse({"like_fill": "none", "likes_count": blog.likes_count})
    response.set_cookie("weinnzguestid", guestid, max_age=100*24*60*60)
    return response

@csrf_exempt
def post_comment(request):
    if request.method != "POST":
        return JsonResponse({"error": "Invalid request method."}, status=400)

    
    form = BlogCommentForm(data = request.POST)
    if not form.is_valid():
        return JsonResponse({"status": False, "error": form.errors})
    else:
        time.sleep(random.uniform(1.5, 5.5))  # 模拟网络延迟


        blog_id = request.POST.get("blog_id", "")
        Blog.objects.filter(id=blog_id).update(comments_count = F('comments_count') + 1)

        blog = Blog.objects.filter(id=blog_id).first()
        form.instance.profile_icon = random.choice(EMOJI_LIST)
        form.instance.color = random.choice(COLOR_LIST)
        form.instance.blog_id = blog
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

    return JsonResponse({"status": True, "comment_html": mark_safe(string), "comments_count": blog.comments_count})
