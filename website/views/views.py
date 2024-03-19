from flask import Blueprint, render_template, request, flash, redirect, url_for, jsonify, current_app
from website.models import User, Comment, BlogPost, Like
from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import login_user, login_required, logout_user, current_user

from .forms import CommentForm, PostForm, EditPostForm, UpdateFirstNameForm, EditProfileForm, EmptyForm
from datetime import date, datetime
from website.utilities import get_local_time
from website.views import views
from website import db


# views = Blueprint('views', __name__)

# Define routes and functions...


@views.route('/', methods=['GET', 'POST'])
@login_required
def home():
    return render_template("home.html", user=current_user)


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
    posts = BlogPost.query.order_by(BlogPost.date.desc()).paginate(page=page, per_page=current_app.config['POSTS_PER_PAGE'])
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
    return render_template('profile.html', user=user, blog_posts=blog_posts)


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
    followers_info = [{'username': follower.first_name, 'email': follower.email} for follower in current_user.followers.all()]
    return render_template('followers.html', followers_info=followers_info, user=current_user)


@views.route('/edit-profile', methods=['GET', 'POST'])
@login_required
def edit_profile():
    form = EditProfileForm()
    if form.validate_on_submit():
        current_user.first_name = form.first_name.data
        current_user.about_me = form.about_me.data
        db.session.commit()
        flash('Your profile has been updated!', 'success')
        return redirect(url_for('views.edit_profile'))
    elif request.method == 'GET':
        form.first_name.data = current_user.first_name
        form.about_me.data = current_user.about_me
    return render_template('edit_profile.html', title='Edit Profile', form=form, user=current_user)


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
