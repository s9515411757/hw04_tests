from django.shortcuts import render, get_object_or_404, redirect
from django.core.paginator import Paginator
from django.conf import settings
from django.contrib.auth.decorators import login_required

from .models import Post, Group, User
from .forms import PostForm


def pagination(post_list, request):
    paginator = Paginator(post_list, settings.QUANTITY_POSTS)
    return paginator.get_page(request.GET.get('page'))


def index(request):
    post_list = Post.objects.select_related('author', 'group')
    page_obj = pagination(post_list, request)

    context = {
        'page_obj': page_obj,
    }
    return render(request, 'posts/index.html', context)


def group_posts(request, slug):
    group = get_object_or_404(Group, slug=slug)
    posts = group.posts.select_related('author')
    page_obj = pagination(posts, request)
    context = {
        'group': group,
        'page_obj': page_obj,
        'group_list': True
    }
    return render(request, 'posts/group_list.html', context)


def profile(request, username):
    author = User.objects.get(username=username)
    post_list = author.posts.select_related('group')
    page_obj = pagination(post_list, request)

    context = {
        'page_obj': page_obj,
        'author': author,
        'profile': True
    }
    return render(request, 'posts/profile.html', context)


def post_detail(request, post_id):
    post = get_object_or_404(
        Post.objects.select_related('author', 'group'), pk=post_id
    )
    context = {
        'post': post,
        'post_count': post.author.posts.all(),
    }
    return render(request, 'posts/post_detail.html', context)


@login_required
def post_create(request):
    form = PostForm(request.POST or None)
    if form.is_valid():
        form.instance.author = request.user
        form.save()
        return redirect('posts:profile', request.user.username)

    context = {
        'form': form,
        'is_edit': False
    }
    return render(request, 'posts/create_post.html', context)


@login_required
def post_edit(request, post_id):
    post = get_object_or_404(
        Post.objects.select_related('author', 'group'), pk=post_id
    )
    if request.user != post.author:
        return redirect('posts:post_detail', post.id)

    form = PostForm(request.POST or None, instance=post)

    if form.is_valid():
        form.save()
        return redirect('posts:post_detail', post.id)

    context = {
        'form': form,
        'is_edit': True
    }
    return render(request, 'posts/create_post.html', context)
