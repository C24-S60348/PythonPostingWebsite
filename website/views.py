from flask import Flask, Blueprint, Response, abort, render_template, request, flash, jsonify, redirect, url_for, send_from_directory
from flask_login import login_user, login_required, logout_user, current_user
from .models import Posting, Comment, User
from . import db
from werkzeug.utils import secure_filename
import json, os
from sqlalchemy.orm import joinedload

views = Blueprint('views', __name__)

UPLOAD_FOLDER = '/website/images'
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif'}

#Add post
@views.route('/', methods=['GET', 'POST'])
@login_required
def home():
    if request.method == 'POST':
        posting = request.form.get('posting')
        image = request.files.get('image')
        comment = request.form.get('comment')
        posting_id = request.form.get('posting_id')
        user_id = request.form.get('user_id')

        if comment :
            if len(comment) < 1 :
                flash('Your comment is too short!', category='error')
            else :
                new_comment = Comment(data=comment, posting_id=posting_id, user_id=user_id)
                print(new_comment)
                db.session.add(new_comment)
                db.session.commit()
                flash('Comment added!', category='success')
        elif len(posting) < 1 :
            flash('Your post is too short!', category='error')
        elif image and image.filename:
            try:
                image_data = image.read()
                new_posting = Posting(data=posting, user_id=current_user.id, image=image_data)
                db.session.add(new_posting)
                db.session.commit()
                flash('Post added!', category='success')
            except Exception as e:
                flash(f'Error uploading image: {e}', category='error')
        else:
            new_posting = Posting(data=posting, user_id=current_user.id)
            db.session.add(new_posting)
            db.session.commit()
            flash('Post added!', category='success')

    #all_postings = Posting.query.join(User).all()
    #print(all_postings)
    
    #all_postings = db.session.query(Posting, User.first_name, Comment) \
    #                .join(User, Posting.user_id == User.id) \
    #                .outerjoin(Comment, Posting.id == Comment.posting_id) \
    #                .all() 

    
    #all_postings = db.session.query(Posting, User.first_name, Comment) \
    #                .join(User, Posting.user_id == User.id) \
    #                .outerjoin(Comment, Posting.id == Comment.posting_id) \
    #                .all()
    
    all_postings = db.session.query(Posting, User.first_name).join(User, Posting.user_id == User.id).options(joinedload(Posting.comments)).all()
    #all_postings = db.session.query(Posting, User.first_name, Comment.data).join(User).all()
    #print(all_postings)
    return render_template("home.html", user=current_user, postings=all_postings)


#Delete post API
@views.route('/delete_posting', methods=['POST'])
def delete_posting():
    posting = json.loads(request.data)
    postingId = posting['postingId']
    posting = Posting.query.get(postingId)
    if posting:
        if (posting.user_id == current_user.id) or (current_user.email == 'admin123@test.com') :
            db.session.delete(posting)
            db.session.commit()

    return jsonify({})

#Delete comment API
@views.route('/delete_comment', methods=['POST'])
def delete_comment():
    comment = json.loads(request.data)
    commentId = comment['commentId']
    comment = Comment.query.get(commentId)
    if comment:
        if (comment.user_id == current_user.id) or (current_user.email == 'admin123@test.com') :
            db.session.delete(comment)
            db.session.commit()

    return jsonify({})

#Upload file
def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

#Route for getting images
@views.route('/display_image/<int:posting_id>')
def display_image(posting_id):
    posting = Posting.query.get(posting_id)
    if not posting or not posting.image:
        return abort(404)  # Handle missing image

    return Response(posting.image, mimetype='image/jpeg')