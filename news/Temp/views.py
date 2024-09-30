from django.shortcuts import render, get_object_or_404, redirect
from .models import Article, News
from .filters import ArticleFilter
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.contrib.auth.decorators import login_required
from datetime import date
from django.utils import timezone

def home(request):
    return render(request, 'news/home.html')

def edit_news(request, pk):
    article = get_object_or_404(Article, pk=pk, type=True)
    if request.method == 'POST':
        title = request.POST.get('title')
        author = request.POST.get('author')
        content = request.POST.get('content')

        if not title or not author or not content:
            return render(request, 'news/edit_news.html', {
                'error': 'Все поля должны быть заполнены.',
                'article': article
            })

        article.title = title
        article.author = author
        article.content = content
        article.publication_date = timezone.now()
        article.save()
        return redirect('article_detail', id=article.pk)

    return render(request, 'news/edit_news.html', {'article': article})

def edit_article(request, pk):
    article = get_object_or_404(Article, pk=pk, type=False)
    if request.method == 'POST':
        title = request.POST.get('title')
        author = request.POST.get('author')
        content = request.POST.get('content')

        if not title or not author or not content:
            return render(request, 'news/edit_article.html', {
                'error': 'Все поля должны быть заполнены.',
                'article': article
            })

        article.title = title
        article.author = author
        article.content = content
        article.publication_date = timezone.now()
        article.save()
        return redirect('article_detail', id=article.pk)

    return render(request, 'articles/edit_article.html', {'article': article})

@login_required
def delete_news(request, pk):
    item = get_object_or_404(Article, pk=pk, type=True)  # Убедитесь, что тип записи - новость
    if request.method == 'POST':
        item.delete()
        return redirect('article_list')  # Или другой URL для отображения списка новостей
    return render(request, 'news/delete_news.html', {'item': item})


@login_required
def delete_article(request, pk):
    item = get_object_or_404(Article, pk=pk, type=False)  # Убедитесь, что тип записи - статья
    if request.method == 'POST':
        item.delete()
        return redirect('article_list')  # Или другой URL для отображения списка статей
    return render(request, 'articles/delete_article.html', {'item': item})






def article_list(request):
    articles = Article.objects.all().order_by('-publication_date')
    paginator = Paginator(articles, 10)
    page_number = request.GET.get('page')
    try:
        page_obj = paginator.get_page(page_number)
    except PageNotAnInteger:
        page_obj = paginator.get_page(1)
    except EmptyPage:
        page_obj = paginator.get_page(paginator.num_pages)
    return render(request, 'news/article_list.html', {'page_obj': page_obj})

def article_detail(request, id):
    article = get_object_or_404(Article, id=id)
    return render(request, 'news/article_detail.html', {'article': article})

@login_required
def admin_page(request):
    if request.method == 'POST':
        # Очистка старых данных сессии перед обработкой новых действий
        request.session.pop('edit_mode', None)
        request.session.pop('delete_mode', None)

        record_type = request.POST.get('record_type')

        # Обработка кнопки "Создать новую запись"
        if 'create' in request.POST:
            if record_type == 'news':
                return redirect('create_news')
            elif record_type == 'article':
                return redirect('create_article')

        # Обработка кнопки "Редактировать запись"
        elif 'edit' in request.POST:
            # Передаем параметры через сессию
            request.session['edit_mode'] = True
            request.session['delete_mode'] = False
            request.session['record_type'] = record_type
            return redirect('article_search')

        # Обработка кнопки "Удалить запись"
        elif 'delete' in request.POST:
            # Передаем параметры через сессию
            request.session['edit_mode'] = False
            request.session['delete_mode'] = True
            request.session['record_type'] = record_type
            return redirect('article_search')

    return render(request, 'news/admin_page.html')


def article_search(request):
    # Проверка значения радиокнопок и выполнение соответствующего фильтрации
    filterset = ArticleFilter(request.GET, queryset=Article.objects.all().order_by('-publication_date'))
    edit_mode = request.GET.get('edit_mode') == 'true'
    delete_mode = request.GET.get('delete_mode') == 'true'

    # Проверяем, были ли отправлены критерии поиска
    if any(request.GET.getlist(k) for k in filterset.form.fields):
        paginator = Paginator(filterset.qs, 10)
        page_number = request.GET.get('page')
        try:
            page_obj = paginator.get_page(page_number)
        except PageNotAnInteger:
            page_obj = paginator.get_page(1)
        except EmptyPage:
            page_obj = paginator.get_page(paginator.num_pages)


        show_edit_button = edit_mode and filterset.qs.count() == 1
        show_delete_button = delete_mode and filterset.qs.count() == 1

        return render(request, 'news/article_search.html', {
            'filterset': filterset,
            'page_obj': page_obj,
            'show_edit_button': show_edit_button,
            'show_delete_button': show_delete_button,
        })
    else:
        return render(request, 'news/article_search.html', {
            'filterset': filterset,
        })




def create_news(request):
    if request.method == 'POST':
        title = request.POST.get('title')
        author = request.POST.get('author')
        content = request.POST.get('content')

        if not title or not author or not content:
            return render(request, 'news/create_news.html', {
                'error': 'Все поля должны быть заполнены.'
            })

        Article.objects.create(
            title=title,
            author=author,
            content=content,
            publication_date=date.today(),
            type=True
        )
        return redirect('admin_page')
    return render(request, 'news/create_news.html')

def create_article(request):
    if request.method == 'POST':
        title = request.POST.get('title')
        author = request.POST.get('author')
        content = request.POST.get('content')

        if not title or not author or not content:
            return render(request, 'news/create_article.html', {
                'error': 'Все поля должны быть заполнены.'
            })

        Article.objects.create(
            title=title,
            author=author,
            content=content,
            publication_date=date.today(),
            type=False
        )
        return redirect('admin_page')
    return render(request, 'news/create_article.html')



@login_required
def delete_news(request, pk):
    item = get_object_or_404(Article, pk=pk, type=True)  # Убедитесь, что тип записи - новость
    if request.method == 'POST':
        item.delete()
        return redirect('article_list')  # Или другой URL для отображения списка новостей
    return render(request, 'news/delete_news.html', {'item': item})

@login_required
def delete_article(request, pk):
    item = get_object_or_404(Article, pk=pk, type=False)  # Убедитесь, что тип записи - статья
    if request.method == 'POST':
        item.delete()
        return redirect('article_list')  # Или другой URL для отображения списка статей
    return render(request, 'articles/delete_article.html', {'item': item})