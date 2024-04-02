from flask import Blueprint, render_template, request, flash, redirect, url_for, jsonify, current_app
from website.models import User, Comment, BlogPost, Like, Message, Notification
from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import login_user, login_required, logout_user, current_user

from .forms import CommentForm, PostForm, EditPostForm, EmptyForm, MessageForm
from datetime import date, datetime, timezone
from website.utilities import get_local_time
from website.views import views
from website import db
from sqlalchemy import or_


# views = Blueprint('views', __name__)

# Define routes and functions...

@views.route('/')
def home():
    # Check if the user is logged in
    if current_user.is_authenticated:
        # Define predefined keywords for each category
        categories = {
            'Nature': ['landscape', 'environment', 'wilderness', 'mountains', 'forests', 'rivers', 'oceans', 'wildlife',
                       'flora', 'fauna', 'natural', 'ecology', 'habitat', 'climate', 'conservation', 'biodiversity',
                       'ecosystem', 'outdoors', 'scenery', 'countryside'],
            'Science': ['discovery', 'experiment', 'laboratory', 'theory', 'hypothesis', 'data', 'analysis',
                        'observation',
                        'experiment', 'scientific', 'technology', 'research', 'innovation', 'discovery', 'experiment',
                        'laboratory', 'theory', 'hypothesis', 'data'],
            'Animals': ['mammals', 'reptiles', 'amphibians', 'birds', 'insects', 'marine life', 'domesticated',
                        'species',
                        'habitat', 'conservation', 'zoology', 'behavior', 'wildlife', 'pets', 'domesticated', 'feline',
                        'canine', 'pets', 'dog', 'bird', 'cat'],
            'Politics': ['democracy', 'governance', 'legislation', 'policy', 'political', 'government',
                         'administration',
                         'diplomacy', 'elections', 'campaign', 'voting', 'legislation', 'policy', 'political',
                         'government',
                         'administration', 'diplomacy', 'elections', 'campaign']
        }

        # Initialize a dictionary to store posts for each category
        categorized_posts = {}

        # Loop through each category and fetch posts containing predefined keywords
        for category, keywords in categories.items():
            # Construct a filter expression to match any of the keywords for this category
            filter_expression = or_(*(BlogPost.content.ilike('%' + keyword + '%') for keyword in keywords))
            # Fetch posts matching the filter expression
            posts = BlogPost.query.filter(filter_expression).all()
            categorized_posts[category] = posts

        return render_template('home.html', categorized_posts=categorized_posts, user=current_user)
    else:
        # Render a simplified home page for non-logged-in users
        return render_template('welcome.html')


@views.route('/add-comment/<int:post_id>', methods=['POST'])
@login_required
def add_comment(post_id):
    post = BlogPost.query.get_or_404(post_id)
    form = CommentForm()
    if form.validate_on_submit():
        new_comment = Comment(content=form.content.data, author=current_user, post_id=post.id)
        db.session.add(new_comment)
        db.session.commit()
        flash('Comment added successfully!', 'success')
    else:
        flash('Error adding comment.', 'error')
    return redirect(url_for('views.post_detail', post_id=post_id))


@views.route('/delete-post/<int:post_id>', methods=['POST'])
@login_required
def delete_post(post_id):
    post = BlogPost.query.get_or_404(post_id)
    comments = Comment.query.filter_by(post_id=post.id).all()

    # Delete the post
    db.session.delete(post)

    # Delete the associated comments
    for comment in comments:
        db.session.delete(comment)

    db.session.commit()
    flash('Post and associated comments deleted successfully!', 'success')
    return redirect(url_for('views.blogpost'))


@views.route('/blogpost')
@login_required
def blogpost():
    page = request.args.get('page', 1, type=int)
    posts = BlogPost.query.order_by(BlogPost.date.desc()).paginate(page=page,
                                                                   per_page=current_app.config['POSTS_PER_PAGE'])
    post_form = PostForm()
    comment_form = CommentForm()  # Create an instance of the CommentForm
    form = EmptyForm()  # Create an instance of the EmptyForm

    # Check if date attribute is None and set it to current time if necessary
    for post in posts.items:
        if post.date is None:
            post.date = datetime.now()

    post_likes_count = {}

    for post in posts.items:
        post_likes_count[post.id] = Like.query.filter_by(blog_post_id=post.id).count()

    return render_template('blogpost.html', post_form=post_form, comment_form=comment_form,
                           posts=posts, user=current_user, user_first_name=current_user.first_name,
                           post_likes_count=post_likes_count, form=form)


@views.route('/add-post', methods=['GET', 'POST'])
@login_required
def add_post():
    post_form = PostForm()
    if post_form.validate_on_submit():
        title = post_form.title.data
        content = post_form.content.data
        author = current_user
        new_post = BlogPost(title=title, content=content, author=author)
        db.session.add(new_post)
        db.session.commit()
        flash('Post added successfully!', 'success')
        return redirect(url_for('views.blogpost'))
    return render_template('add_post.html', post_form=post_form, user=current_user)


@views.route('/edit-post/<int:post_id>', methods=['GET', 'POST'])
@login_required
def edit_post(post_id):
    post = BlogPost.query.get_or_404(post_id)
    form = EditPostForm(obj=post)  # Populate the form with existing post data

    if form.validate_on_submit():
        post.title = form.title.data
        post.content = form.content.data
        db.session.commit()
        flash('Post updated successfully!', 'success')
        return redirect(url_for('views.blogpost'))

    return render_template('edit_post.html', form=form, user=current_user, post=post)


@views.route('/profile/<first_name>')
@login_required
def profile(first_name):
    user = User.query.filter_by(first_name=first_name).first_or_404()
    blog_posts = user.blog_posts  # Assuming 'blog_posts' is the relationship to 'BlogPost'
    following_posts = current_user.following_posts().all()
    return render_template('profile.html', user=user, blog_posts=blog_posts, following_posts=following_posts)


@views.route('/post/<int:post_id>', methods=['GET', 'POST'])
@login_required
def post_detail(post_id):
    post = BlogPost.query.get_or_404(post_id)
    comment_form = CommentForm()
    local_date = get_local_time(post.date)
    return render_template('post_detail.html', post=post, user=current_user,
                           comment_form=comment_form, local_date=local_date, get_local_time=get_local_time)


@views.route('/follow/<username>', methods=['POST'])
@login_required
def follow(username):
    form = EmptyForm()
    if form.validate_on_submit():
        user = User.query.filter_by(first_name=username).first()
        if user is None:
            flash(f'User {username} not found.')
            return redirect(url_for('views.blogpost'))  # Redirect to blogpost endpoint
        if user == current_user:
            flash('You cannot follow yourself!')
            return redirect(url_for('views.blogpost'))  # Redirect to blogpost endpoint
        current_user.follow(user)
        db.session.commit()
        flash(f'You are following {username}!')
    return redirect(url_for('views.blogpost'))  # Redirect to blogpost endpoint


@views.route('/unfollow/<username>', methods=['POST'])
@login_required
def unfollow(username):
    form = EmptyForm()
    if form.validate_on_submit():
        user = User.query.filter_by(first_name=username).first()
        if user is None:
            flash(f'User {username} not found.')
            return redirect(url_for('views.blogpost'))  # Redirect to blogpost endpoint
        if user == current_user:
            flash('You cannot unfollow yourself!')
            return redirect(url_for('views.blogpost'))  # Redirect to blogpost endpoint
        current_user.unfollow(user)
        db.session.commit()
        flash(f'You are not following {username}.')
    return redirect(url_for('views.blogpost'))  # Redirect to blogpost endpoint


@views.route('/get_followers/<username>', methods=['GET'])
@login_required
def get_followers(username):
    user = User.query.filter_by(first_name=username).first_or_404()
    followers = user.followers.all()
    # Return JSON data containing followers' information
    followers_info = [{'username': follower.first_name, 'email': follower.email} for follower in followers]
    return jsonify(followers_info)


@views.route('/followers', methods=['GET'])
@login_required
def followers():
    # Fetch follower information for the current user
    followers_info = [{'username': follower.first_name, 'email': follower.email} for follower in
                      current_user.followers.all()]
    return render_template('followers.html', followers_info=followers_info, user=current_user)


@views.route('/like_post/<int:post_id>', methods=['POST'])
@login_required
def like_post(post_id):
    post = BlogPost.query.get_or_404(post_id)
    user_id = current_user.id

    # Check if the user has already liked the post
    like = Like.query.filter_by(user_id=user_id, blog_post_id=post_id).first()

    if like:
        # Unlike the post if already liked
        db.session.delete(like)
        db.session.commit()
    else:
        # Like the post if not already liked
        new_like = Like(user_id=user_id, blog_post_id=post_id)
        db.session.add(new_like)
        db.session.commit()

    # Redirect back to the same page
    return redirect(request.referrer)


@views.route('/search')
@login_required
def search():
    query = request.args.get('query')
    if query:
        search_results = BlogPost.query.filter(BlogPost.title.ilike(f'%{query}%') |
                                               BlogPost.content.ilike(f'%{query}%')).all()
    else:
        search_results = []
    return render_template('search.html', search_results=search_results, user=current_user)


@views.route('/get-user-profile/<first_name>')
@login_required
def get_user_profile(first_name):
    user = User.query.filter_by(first_name=first_name).first()

    if user:
        profile_data = {
            'avatar': user.avatar(40),  # Generate avatar URL using the user's email
            'name': user.first_name,
            'email': user.email,
            'bio': user.about_me,
            'followers': user.followers_count()  # Assuming you have a followers_count method
        }
        return jsonify(profile_data)
    else:
        return jsonify({'error': 'User not found'}), 404


@views.route('/followers/<username>', methods=['GET'])
@login_required
def show_followers(username):
    user = User.query.filter_by(first_name=username).first_or_404()
    followers = user.followers.all()
    return render_template('followers.html', followers=followers, user=current_user)


@views.route('/send_message/<recipient>', methods=['GET', 'POST'])
@login_required
def send_message(recipient):
    user = db.first_or_404(db.select(User).where(User.first_name == recipient))
    form = MessageForm()
    if form.validate_on_submit():
        msg = Message(author=current_user, recipient=user,
                      body=form.message.data)
        db.session.add(msg)
        user.add_notification('unread_message_count', user.unread_message_count())

        db.session.commit()
        flash('Your message has been sent.')
        return redirect(url_for('views.profile', first_name=recipient))
    return render_template('send_message.html', title='Send Message',
                           form=form, recipient=recipient, user=current_user)


@views.route('/messages')
@login_required
def messages():
    current_user.last_message_read_time = datetime.now(timezone.utc)
    current_user.add_notification('unread_message_count', 0)
    # current_user.unread_message_count = 0  # Assuming unread_message_count is an attribute of the User model
    db.session.commit()

    page = request.args.get('page', 1, type=int)
    query = current_user.messages_received.order_by(
        Message.timestamp.desc())
    messages = query.paginate(page=page,
                              per_page=current_app.config['POSTS_PER_PAGE'],
                              error_out=False)

    next_url = url_for('views.messages', page=messages.next_num) \
        if messages.has_next else None
    prev_url = url_for('views.messages', page=messages.prev_num) \
        if messages.has_prev else None

    return render_template('messages.html', messages=messages.items,
                           next_url=next_url, prev_url=prev_url, user=current_user)


@views.route('/notifications')
@login_required
def notifications():
    since = request.args.get('since', 0.0, type=float)
    query = Notification.query.filter(
        Notification.user_id == current_user.id,
        Notification.timestamp > since
    ).order_by(Notification.timestamp.asc())
    notifications = query.all()
    return [{
        'name': n.name,
        'data': n.get_data(),
        'timestamp': n.timestamp
    } for n in notifications]

