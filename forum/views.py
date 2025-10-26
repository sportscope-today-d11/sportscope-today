from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from forum.models import Category, Thread, Comment
from forum.forms import ThreadForm, CommentForm, CategoryForm
from django.contrib.auth.models import User
from django.db.models import Q
from django.http import JsonResponse
from django.urls import reverse


def category_list(request):
    categories = Category.objects.all()
    return render(request, 'forum/category_list.html', {'categories': categories})

def category_list_json(request):
    categories = Category.objects.all()
    data = {
        "categories": [
            {
                "id": category.id,
                "name": category.name,
                "slug": category.slug,
                "thread_list_url": reverse("forum:thread_list", args=[category.slug]),
                "create_thread_url": reverse("forum:create_thread", args=[category.slug]),
            }
            for category in categories
        ]
    }
    return JsonResponse(data)

def thread_list(request, category_slug):
    category = get_object_or_404(Category, slug=category_slug)
    threads = category.threads.all().order_by('-created_at')
    return render(request, 'forum/thread_list.html', {'category': category, 'threads': threads})

def thread_detail(request, slug):
    thread = get_object_or_404(Thread, slug=slug)
    comments = thread.comments.filter(parent__isnull=True).order_by('-created_at')
    
    if request.method == 'POST':
        comment_form = CommentForm(request.POST)
        if comment_form.is_valid():
            comment = comment_form.save(commit=False)
            comment.thread = thread

            dummy_user, _ = User.objects.get_or_create(username="guest_user")
            comment.author = dummy_user

            parent_id = request.POST.get('parent_id')
            if parent_id:
                comment.parent = Comment.objects.get(id=parent_id)
            comment.save()
            return redirect('forum:thread_detail', slug=thread.slug)
    else:
        comment_form = CommentForm()
    
    return render(request, 'forum/thread_detail.html', {
        'thread': thread,
        'comments': comments,
        'comment_form': comment_form
    })

def create_thread(request, category_slug):
    category = get_object_or_404(Category, slug=category_slug)
    
    if request.method == 'POST':
        form = ThreadForm(request.POST)
        if form.is_valid():
            thread = form.save(commit=False)

            # Cari atau buat user dummy (agar tidak error)
            dummy_user, _ = User.objects.get_or_create(username="guest_user")

            thread.author = dummy_user
            thread.category = category
            thread.save()
            return redirect('forum:thread_detail', slug=thread.slug)
    else:
        form = ThreadForm()

    return render(request, 'forum/create_thread.html', {'form': form, 'category': category})

def all_threads(request):
    category_slug = request.GET.get('category')  # Ambil slug dari query string
    if category_slug:
        threads = Thread.objects.filter(category__slug=category_slug).order_by('-created_at')
    else:
        threads = Thread.objects.all().order_by('-created_at')

    categories = Category.objects.all()
    return render(request, 'forum/all_threads.html', {
        'threads': threads,
        'categories': categories,
        'selected_category': category_slug,
    })

def create_category(request):
    if request.method == 'POST':
        form = CategoryForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('forum:category_list')
    else:
        form = CategoryForm()
    return render(request, 'forum/create_category.html', {'form': form})

