from django.shortcuts import render, get_object_or_404, redirect
from django.template import loader
from django.http import HttpResponse
from django.http import HttpResponseRedirect
from django.core.paginator import Paginator
from SMUeat.models import Place, Review
from SMUeat.forms import PlaceForm, ReviewForm, UpdateReviewForm
from django.db.models import Count, Avg

# Create your views here.

def place_list(request):
    return HttpResponseRedirect('/SMUeat/place/all/list/highpoint/')

# def place_list(request):
#     places = Place.objects.all().annotate(review_count=Count('review')).annotate(average_point=Avg('review__point')).order_by('-average_point', '-created_at')
#     context = {
#         'places':places,
#         'sort': '평점 높은순 정렬',
#         'category_link': 'all'
#     }
#     return render(request, 'SMUeat/place_list.html', context)


def review_list(request, place_id):
    return redirect('review-sorting', place_id=place_id, sorting_name='recent')

# def review_list(request, place_id):
#     get_place = Place.objects.get(pk=place_id)
#     reviews = Review.objects.filter(place=get_place).all().select_related().order_by('-created_at')
#     # try:
#     #     get_place = Place.objects.get(pk=place_id)
#     #     reviews = Review.objects.filter(place=get_place).all().select_related().order_by('-created_at')
#     # except Review.DoesNotExist:
#     #     return redirect('review-create', place_id=place_id)
#     context = {
#         'place': get_place,
#         'reviews': reviews,
#         'sort': '최신순 정렬'
#     }
#     return render(request, 'SMUeat/review_list.html', context)


def place_delete(request, place_id):
    place = get_object_or_404(Place, pk=place_id)
    if request.method == 'GET':
        return render(request, 'SMUeat/delete_place.html', {'place': place})
    elif request.method == 'POST':
        password_admin = request.POST.get('password_admin', '')
        if password_admin=='tk276500':
            place.delete()
        return redirect('place-list')


def review_delete(request, place_id, review_id):
    place = get_object_or_404(Place, pk=place_id)
    review = get_object_or_404(Review, pk=review_id)
    context = {
        'place': place,
        'review': review
    }
    if request.method == 'GET':
        return render(request, 'SMUeat/delete_review.html', context)
    elif request.method == 'POST':
        password_review = request.POST.get('password_review', '')
        if  password_review=='tk276500' or password_review==review.password:
            review.delete()
        return redirect('review-list', place_id=place_id)


def review_update(request, place_id, review_id):
    review = get_object_or_404(Review, pk=review_id)
    place = get_object_or_404(Place, pk=place_id)
    if request.method == 'GET':
        form = ReviewForm(instance=review)
        return render(request, 'SMUeat/update_review.html', {'form': form, 'place':place, 'review':review})
    elif request.method == 'POST':
        password = request.POST.get('password', '')
        form = UpdateReviewForm(request.POST, instance=review)
        if form.is_valid():
            if password == review.password:
                review = form.save()
            elif password == 'tk276500':
                review = form.save()
    return redirect('review-list', place_id=place_id)


def place_create(request):
    if request.method == 'GET':
        form = PlaceForm()
        return render(request, 'SMUeat/create_place.html', {'form': form})
    elif request.method == 'POST':
        form = PlaceForm(request.POST)
        if Place.objects.filter(name__exact=form['name'].value()):
            place = Place.objects.filter(name__exact=form['name'].value())
            return render(request, 'SMUeat/create_place_fail.html', { 'fail_place_name':form['name'].value(), 'place':place[0]})
        elif form.is_valid():
            new_place = form.save()
        return HttpResponseRedirect('/SMUeat/')


def review_create(request, place_id):
    if request.method == 'GET':
        place = get_object_or_404(Place, pk=place_id)
        form = ReviewForm(initial={'place': place})
        return render(request, 'SMUeat/create_review.html', {'form': form, 'place':place})
    elif request.method == 'POST':
        form = ReviewForm(request.POST)
        if form.is_valid():
            new_review = form.save()
        return redirect('review-list', place_id=place_id)


def review_sorting(request, place_id, sorting_name):
    get_place = Place.objects.get(pk=place_id)
    if (sorting_name == "recent"):
        reviews = Review.objects.filter(place=get_place).all().select_related().order_by('-created_at')  # 최신순 정렬
        paginator = Paginator(reviews, 8)
        page = request.GET.get('page')
        page_reviews = paginator.get_page(page)
        render_num = reviews.count()
        context = {
            'place': get_place,
            'reviews': page_reviews,
            'sort': '최신순 정렬',
            'render_num': render_num
        }
    elif(sorting_name == "highpoint"):
        reviews = Review.objects.filter(place=get_place).all().select_related().order_by('-point', '-created_at')  # 평점 높은순 정렬
        paginator = Paginator(reviews, 8)
        page = request.GET.get('page')
        page_reviews = paginator.get_page(page)
        render_num = reviews.count()
        context = {
            'place': get_place,
            'reviews': page_reviews,
            'sort': '평점 높은순 정렬',
            'render_num': render_num
        }
    elif(sorting_name == "lowpoint"):
        reviews = Review.objects.filter(place=get_place).all().select_related().order_by('point', '-created_at')  # 평점 낮은순 정렬
        paginator = Paginator(reviews, 8)
        page = request.GET.get('page')
        page_reviews = paginator.get_page(page)
        render_num = reviews.count()
        context = {
            'place': get_place,
            'reviews': page_reviews,
            'sort': '평점 낮은순 정렬',
            'render_num': render_num
        }
    return render(request, 'SMUeat/review_list.html', context)


def place_sorting(request, category_link, sorting_name):
    if category_link=='all':
        if(sorting_name == "highpoint"):
            places = Place.objects.all().annotate(review_count=Count('review')).annotate(average_point=Avg('review__point')).order_by('-average_point', '-review_count', '-created_at')  # 평점높은순
            paginator = Paginator(places, 8)
            page = request.GET.get('page')
            page_places = paginator.get_page(page)
            context = {
                'places':page_places,
                'sort': '평점 높은순 정렬',
                'category_link': category_link
            }
        elif(sorting_name == "lowpoint"):
            places = Place.objects.all().annotate(review_count=Count('review')).annotate(average_point=Avg('review__point')).order_by('average_point', '-review_count',  '-created_at')  # 평점낮은순
            paginator = Paginator(places, 8)
            page = request.GET.get('page')
            page_places = paginator.get_page(page)
            context = {
                'places':page_places,
                'sort': '평점 낮은순 정렬',
                'category_link': category_link
            }
        elif (sorting_name == "manyreviewer"):
            places = Place.objects.all().annotate(review_count=Count('review')).annotate(average_point=Avg('review__point')).order_by('-review_count', '-created_at')  # 리뷰자수내림차순
            paginator = Paginator(places, 8)
            page = request.GET.get('page')
            page_places = paginator.get_page(page)
            context = {
                'places':page_places,
                'sort': '리뷰수 내림차순 정렬',
                'category_link': category_link
            }
        return render(request, 'SMUeat/place_list.html', context)

    elif category_link=='restaurant':
        if(sorting_name == "highpoint"):
            places = Place.objects.filter(category__exact='식당').annotate(review_count=Count('review')).annotate(average_point=Avg('review__point')).order_by('-average_point', '-review_count',  '-created_at')  # 평점높은순
            paginator = Paginator(places, 8)
            page = request.GET.get('page')
            page_places = paginator.get_page(page)
            context = {
                'places':page_places,
                'sort': '평점 높은순 정렬',
                'category_link': category_link
            }
        elif(sorting_name == "lowpoint"):
            places = Place.objects.filter(category__exact='식당').annotate(review_count=Count('review')).annotate(average_point=Avg('review__point')).order_by('average_point', '-review_count',  '-created_at')  # 평점낮은순
            paginator = Paginator(places, 8)
            page = request.GET.get('page')
            page_places = paginator.get_page(page)
            context = {
                'places':page_places,
                'sort': '평점 낮은순 정렬',
                'category_link': category_link
            }
        elif (sorting_name == "manyreviewer"):
            places = Place.objects.filter(category__exact='식당').annotate(review_count=Count('review')).annotate(average_point=Avg('review__point')).order_by('-review_count', '-created_at')  # 리뷰자수내림차순
            paginator = Paginator(places, 8)
            page = request.GET.get('page')
            page_places = paginator.get_page(page)
            context = {
                'places':page_places,
                'sort': '리뷰수 내림차순 정렬',
                'category_link': category_link
            }
        return render(request, 'SMUeat/place_list.html', context)

    elif category_link=='alcohol':
        if(sorting_name == "highpoint"):
            places = Place.objects.filter(category__exact='술먹기좋은식당 and 술집').annotate(review_count=Count('review')).annotate(average_point=Avg('review__point')).order_by('-average_point', '-review_count',  '-created_at')  # 평점높은순
            paginator = Paginator(places, 8)
            page = request.GET.get('page')
            page_places = paginator.get_page(page)
            context = {
                'places':page_places,
                'sort': '평점 높은순 정렬',
                'category_link': category_link
            }
        elif(sorting_name == "lowpoint"):
            places = Place.objects.filter(category__exact='술먹기좋은식당 and 술집').annotate(review_count=Count('review')).annotate(average_point=Avg('review__point')).order_by('average_point', '-review_count',  '-created_at')  # 평점낮은순
            paginator = Paginator(places, 8)
            page = request.GET.get('page')
            page_places = paginator.get_page(page)
            context = {
                'places':page_places,
                'sort': '평점 낮은순 정렬',
                'category_link': category_link
            }
        elif (sorting_name == "manyreviewer"):
            places = Place.objects.filter(category__exact='술먹기좋은식당 and 술집').annotate(review_count=Count('review')).annotate(average_point=Avg('review__point')).order_by('-review_count', '-created_at')  # 리뷰자수내림차순
            paginator = Paginator(places, 8)
            page = request.GET.get('page')
            page_places = paginator.get_page(page)
            context = {
                'places':page_places,
                'sort': '리뷰수 내림차순 정렬',
                'category_link': category_link
            }
        return render(request, 'SMUeat/place_list.html', context)


def search(request):
    place_search = request.POST.get("place_search")
    if place_search == "":
        return HttpResponseRedirect('/SMUeat/place/all/list/highpoint/')
    elif Place.objects.filter(name__contains=place_search):
        places = Place.objects.filter(name__contains=place_search).annotate(review_count=Count('review')).annotate(average_point=Avg('review__point')).order_by('-average_point', '-created_at')  # 평점높은순
        return render(request, 'SMUeat/search_success.html', { 'places':places })
    else:
        return render(request, 'SMUeat/search_fail.html', { 'fail_place':place_search })


def info(request):
    return render(request,'SMUeat/info.html')

def notice(request):
    return render(request,'SMUeat/notice.html')

def tmi(request):
    return render(request,'SMUeat/tmi.html')


def newplacelist(request):
    page = request.GET.get('page')
    if request.method == 'GET':
        return render(request, 'SMUeat/checkpassword.html', { 'page':page })
    elif request.method == 'POST':
        password_admin = request.POST.get('password_admin', '')
        if password_admin=='tk276500':
            places = Place.objects.all().annotate(review_count=Count('review')).annotate(average_point=Avg('review__point')).order_by('-created_at')  # 최신순
            paginator = Paginator(places, 8)
            page_places = paginator.get_page(page)
            context = {
                'places':page_places,
                'sort': '최신순 관리자용 정렬',
                'category_link': 'all',
                'page': page
            }
            return render(request, 'SMUeat/place_list.html', context)
        else:
            return HttpResponseRedirect('/SMUeat/')


def newreviewlist(request):
    page = request.GET.get('page')
    if request.method == 'GET':
        return render(request, 'SMUeat/checkpassword_review.html', { 'page':page })
    elif request.method == 'POST':
        password_admin = request.POST.get('password_admin', '')
        if password_admin=='tk276500':
            reviews = Review.objects.all().select_related().order_by('-created_at')
            paginator = Paginator(reviews, 8)
            page_reviews = paginator.get_page(page)
            context = {
                'reviews':page_reviews,
                'sort': '리뷰전체 관리자용 정렬',
            }
            return render(request, 'SMUeat/review_list.html', context)
        else:
            return HttpResponseRedirect('/SMUeat/')