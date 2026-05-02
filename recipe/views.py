from django.shortcuts import render

# Create your views here.
def recipe(request):
    return render(request, 'recipe.html')