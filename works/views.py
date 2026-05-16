from django.shortcuts import render

# Create your views here.
def works(request):
    return render(request, 'works.html')