from django.shortcuts import render, redirect, get_object_or_404
from django.db.models import Q, Count
from django.http import HttpResponseRedirect, JsonResponse
from django.views.decorators.http import require_POST
from .models import Blogs, Category, Comment, CommentReaction
from django.template.loader import render_to_string
from django.urls import reverse


def posts_by_category(request, category_id):
    
    posts = Blogs.objects.filter(status='published', category = category_id)

    try:
        category = Category.objects.get(pk=category_id)
    except Category.DoesNotExist:
        return redirect('home')

    context = {
        'posts': posts,
        'category': category
    }
    return render(request, 'posts_by_category.html', context)

 

#blogs
def blogs(request, slug):
    single_post = get_object_or_404(Blogs, slug=slug, status='published')

    # posting a comment or a reply
    if request.method == "POST":
        if not request.user.is_authenticated:
            return redirect('login')

        text = request.POST.get('comment', '').strip()[:250]
        parent = None
        parent_id = request.POST.get('parent_id', '')
        if parent_id.isdigit():
            # parent must belong to THIS blog post
            parent = Comment.objects.filter(pk=parent_id, blog=single_post).first()

        if text:
            new_comment = Comment.objects.create(
                user=request.user,
                blog=single_post,
                parent=parent,
                comment=text,
            )
            return HttpResponseRedirect(f"{request.path_info}#comment-{new_comment.id}")
        return HttpResponseRedirect(request.path_info)

    # fetch ALL comments of this post in one query, with like/dislike counts
    all_comments = list(
        Comment.objects.filter(blog=single_post)
        .select_related('user')
        .annotate(
            likes=Count('reactions', filter=Q(reactions__value=CommentReaction.LIKE)),
            dislikes=Count('reactions', filter=Q(reactions__value=CommentReaction.DISLIKE)),
        )
        .order_by('created_at')
    )

    # which comments has the current user reacted to?
    user_reactions = {}
    if request.user.is_authenticated:
        user_reactions = dict(
            CommentReaction.objects
            .filter(user=request.user, comment__blog=single_post)
            .values_list('comment_id', 'value')
        )

    # build the tree in Python
    by_id = {}
    for c in all_comments:
        c.child_list = []
        c.user_reaction = user_reactions.get(c.id, 0)
        by_id[c.id] = c

    top_level = []
    for c in all_comments:
        if c.parent_id:
            by_id[c.parent_id].child_list.append(c)
        else:
            top_level.append(c)

    top_level.reverse()  # newest top-level comments first; replies stay oldest-first

    context = {
        'single_post': single_post,
        'comments': top_level,
        'comment_count': len(all_comments),  # includes replies
    }
    return render(request, 'blogs.html', context)


@require_POST
def react_comment(request, comment_id, action):
    if not request.user.is_authenticated:
        return JsonResponse({'error': 'login_required'}, status=401)
    if action not in ('like', 'dislike'):
        return JsonResponse({'error': 'invalid_action'}, status=400)

    comment = get_object_or_404(Comment, pk=comment_id, blog__status='published')
    value = CommentReaction.LIKE if action == 'like' else CommentReaction.DISLIKE

    reaction, created = CommentReaction.objects.get_or_create(
        user=request.user, comment=comment, defaults={'value': value}
    )
    user_reaction = value
    if not created:
        if reaction.value == value:      # clicked the same button again -> undo
            reaction.delete()
            user_reaction = 0
        else:                            # switched like <-> dislike
            reaction.value = value
            reaction.save()

    counts = comment.reactions.aggregate(
        likes=Count('id', filter=Q(value=CommentReaction.LIKE)),
        dislikes=Count('id', filter=Q(value=CommentReaction.DISLIKE)),
    )
    return JsonResponse({**counts, 'user_reaction': user_reaction})


#search Functionality
def search(request):
    keyword = request.GET.get('keyword', '').strip()
    blogs = Blogs.objects.filter(
        Q(title__icontains=keyword)
        | Q(short_description__icontains=keyword)
        | Q(blog_body__icontains=keyword),
        status='published',
    )
    context = {
        'blogs': blogs,
        'keyword': keyword,
    }
    return render(request, 'search.html', context)


@require_POST
def edit_comment(request, comment_id):
    if not request.user.is_authenticated:
        return JsonResponse({'error': 'login_required'}, status=401)

    comment = get_object_or_404(Comment, pk=comment_id, blog__status='published')

    # only the author of the comment can edit it
    if comment.user_id != request.user.id:
        return JsonResponse({'error': 'forbidden'}, status=403)

    text = request.POST.get('comment', '').strip()[:250]
    if not text:
        return JsonResponse({'error': 'empty'}, status=400)

    if text != comment.comment:      # only mark as edited if something changed
        comment.comment = text
        comment.is_edited = True
        comment.save()

    return JsonResponse({'comment': comment.comment, 'is_edited': comment.is_edited})


@require_POST
def delete_comment(request, comment_id):
    if not request.user.is_authenticated:
        return JsonResponse({'error': 'login_required'}, status=401)

    comment = get_object_or_404(Comment.objects.select_related('blog'), pk=comment_id)
    user = request.user

    # comment owner, blog author, or staff/admin
    if not (comment.user_id == user.id or comment.blog.author_id == user.id or user.is_staff):
        return JsonResponse({'error': 'forbidden'}, status=403)

    # count this comment + all nested replies, so the page can update "Comments (N)"
    ids = [comment.id]
    frontier = [comment.id]
    while frontier:
        frontier = list(
            Comment.objects.filter(parent_id__in=frontier).values_list('id', flat=True)
        )
        ids.extend(frontier)

    comment.delete()   # replies and reactions are removed by CASCADE
    return JsonResponse({'deleted': len(ids)})

@require_POST
def add_comment(request, slug):
    is_ajax = request.headers.get('x-requested-with') == 'XMLHttpRequest'
    single_post = get_object_or_404(Blogs, slug=slug, status='published')

    if not request.user.is_authenticated:
        if is_ajax:
            return JsonResponse({'error': 'login_required'}, status=401)
        return redirect('login')

    text = request.POST.get('comment', '').strip()[:250]
    if not text:
        if is_ajax:
            return JsonResponse({'error': 'empty'}, status=400)
        return redirect('blogs', slug=slug)

    # a reply's parent must belong to THIS blog post
    parent = None
    parent_id = request.POST.get('parent_id', '')
    if parent_id:
        if not parent_id.isdigit():
            return JsonResponse({'error': 'invalid_parent'}, status=400)
        parent = Comment.objects.filter(pk=parent_id, blog=single_post).first()
        if parent is None:
            return JsonResponse({'error': 'invalid_parent'}, status=400)

    new_comment = Comment.objects.create(
        user=request.user, blog=single_post, parent=parent, comment=text
    )

    # normal (non-JS) form submit: fall back to redirect
    if not is_ajax:
        return HttpResponseRedirect(f"{reverse('blogs', args=[slug])}#comment-{new_comment.id}")

    # depth = number of ancestors (top-level = 0, reply = 1, reply-to-reply = 2 ...)
    depth = 0
    p = parent
    while p is not None:
        depth += 1
        p = p.parent

    # values the template normally gets from the annotated queryset
    new_comment.likes = 0
    new_comment.dislikes = 0
    new_comment.user_reaction = 0
    new_comment.child_list = []

    html = render_to_string(
        'partials/comment_item.html',
        {'comment': new_comment, 'depth': depth, 'single_post': single_post},
        request=request,
    )

    return JsonResponse({
        'html': html,
        'parent_id': parent.id if parent else None,
        'depth': depth,
        'count': Comment.objects.filter(blog=single_post).count(),
    })