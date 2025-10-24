from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from .models import Category, Thread, Comment
from .forms import ThreadForm, CommentForm
from django.contrib.auth.models import User


def category_list(request):
    categories = Category.objects.all()
    return render(request, 'forum/category_list.html', {'categories': categories})

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
            return redirect('thread_detail', slug=thread.slug)
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
            return redirect('thread_detail', slug=thread.slug)
    else:
        form = ThreadForm()

    return render(request, 'forum/create_thread.html', {'form': form, 'category': category})
