from django.shortcuts import render
from django.conf import settings


# Create your views here.
from gallery.models import Gallery
def gallery(request):
    page = int(request.GET.get('page', 1))  # 当前页
    page_size = 10  # 每页个数
    start = (page - 1) * page_size
    end = page * page_size
    #gallery_list = Gallery.objects.all()[start:end]
    gallery_list = Gallery.objects.filter(status=1)[start:end]

    #total_cnt = Gallery.objects.all().count()
    total_cnt = Gallery.objects.filter(status=1).count()
    total_page_cnt, div = divmod(total_cnt, page_size)  # 总页数
    if div:
        total_page_cnt += 1

    if total_page_cnt == 1:
        prev_page = {"text": "NOW", "status": "toc-inactive", "url": "javascript:void (0);"}
        next_page = {"text": "ORIGINAL", "status": "toc-inactive", "url": "javascript:void (0);"}
    elif page == 1 or page > total_page_cnt:
        prev_page = {"text": "NOW", "status": "toc-inactive", "url": "javascript:void (0);"}
        next_page = {"text": "Next", "status": "next-active", "url": f"?page={page + 1}"}    
    elif page == total_page_cnt:
        prev_page = {"text": "Prev", "status": "prev-active", "url": f"?page={page-1}"}
        next_page = {"text": "ORIGINAL", "status": "toc-inactive", "url": "javascript:void (0);"}
    else:
        prev_page = {"text": "Prev", "status": "prev-active", "url": f"?page={page - 1}"}
        next_page = {"text": "Next", "status": "next-active", "url": f"?page={page + 1}"} 

    total_n = 0
    for i in range(len(gallery_list)):
        gallery_list[i].url =  [settings.CDN_URL + k.split(",")[0].strip() for k in gallery_list[i].url.strip().split("\n")]
        gallery_list[i].cover = settings.CDN_URL + gallery_list[i].cover
        title = gallery_list[i].id
        gallery_list[i].title = f"{title[6:8]}/{title[8:]} {title[2:6]}"
        total_n += 1
        
    total_n = sum([int(k.number) for k in gallery_list])

    return render(request, 'gallery.html', {"gallery_list": gallery_list, "total_n": total_n, "prev_page": prev_page, "next_page": next_page})

def gallery_detail(request, gallery_id):
    gallery_info = Gallery.objects.filter(id=gallery_id, status=1).first()
    title = gallery_info.id
    gallery_info.title = f"{title[6:8]}/{title[8:]} {title[2:6]}"
    gallery_urls = [k for k in gallery_info.url.strip().split("\n") if (not k.strip().startswith("#")) and k.strip()]
    gallery_urls = [{"index": n+1,"url":settings.CDN_URL+k.split(",")[0].strip(),"desc":k.split("#")[-1] if "#" in k else ""} for n, k in enumerate(gallery_urls)]
    return render(request, 'gallery_detail.html', {"gallery_info": gallery_info, "gallery_urls": gallery_urls})
