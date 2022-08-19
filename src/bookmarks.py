from crypt import methods
import json
from wsgiref.validate import validator
from flask import Blueprint, request, jsonify
import validators
from flask_jwt_extended import get_jwt_identity, jwt_required
from flasgger import swag_from
from src.database import Bookmark, db

bookmarks = Blueprint("auth",__name__,url_prefix="/api/v1/bookmarks")

@bookmarks.route('/', methods=["POST", "GET"])
@jwt_required()
def handle_bookmarks():
    current_user = get_jwt_identity()
    if request.method == "POST":
        body = request.get_json().get('body', '')
        url = request.get_json().get('url', '')

        if not validators.url(url):
            return jsonify({
            "error" : "enter a valid url"
        }),400

        if Bookmark.query.filter_by(url=url).first():
             return jsonify({
            "error" : "url already exist"
        }),409

        bookmark = Bookmark(url=url, body=body, user_id=current_user)

        db.session.add(bookmark)
        db.session.commit()

        return jsonify({

        "id" : bookmark.id,
        "url" : bookmark.url,
        "short_url" : bookmark.short_url,
        "visits" : bookmark.visits,
        "body" : bookmark.body,
        "created_at" : bookmark.created_at,
        "updated_at" : bookmark.updated_at
         }), 201
    
    else: 

        page = request.args.get("page", 1, type=int)
        per_page = request.args.get("per_page", 5, type=int)

        bookmarkz = Bookmark.query.filter_by(user_id=current_user).paginate(page=page, per_page=per_page)

        data = []

        for bookmark in bookmarkz.items:
            data.append({
                "id" : bookmark.id,
                "url" : bookmark.url,
                "short_url" : bookmark.short_url,
                "visits" : bookmark.visits,
                "body" : bookmark.body,
                "created_at" : bookmark.created_at,
                "updated_at" : bookmark.updated_at
            })

            meta = {
                "page" : bookmarkz.page,
                "pages": bookmarkz.pages,
                "total_count": bookmarkz.total,
                "prev_page": bookmarkz.prev_num,
                "next_page": bookmarkz.next_num,
                "has_next": bookmarkz.has_next,
                "has_prev":  bookmarkz.has_prev,
            }

    return jsonify(
        {"data":data, "meta": meta}
    ), 200
     
    



@bookmarks.get("/<int:id>")
@jwt_required()
def get_bookmark(id):
    current_user = get_jwt_identity()

    bookmark = Bookmark.query.filter_by(user_id=current_user, id=id).first()

    if not bookmark:
        return jsonify({'message': 'Item not found'}), 404

    return jsonify({
        'id': bookmark.id,
        'url': bookmark.url,
        'short_url': bookmark.short_url,
        'visit': bookmark.visits,
        'body': bookmark.body,
        'created_at': bookmark.created_at,
        'updated_at': bookmark.updated_at,
    }),200 


@bookmarks.put('/<int:id>')

@bookmarks.patch('/<int:id>')
@jwt_required()
def handle_edit_bookmars(id):
    current_user = get_jwt_identity()

    bookmark = Bookmark.query.filter_by(user_id=current_user, id=id).first()

    if not bookmark:
        return jsonify({'message': 'Item not found'}), 404

    body = request.get_json().get('body', '')
    url = request.get_json().get('url', '')

    if not validators.url(url):
        return jsonify({
        "error" : "enter a valid url"}),400

    bookmark.url = url
    bookmark.body = body

    db.session.commit()

    return jsonify({
        'id': bookmark.id,
        'url': bookmark.url,
        'short_url': bookmark.short_url,
        'visit': bookmark.visits,
        'body': bookmark.body,
        'created_at': bookmark.created_at,
        'updated_at': bookmark.updated_at,
    }),200  


@bookmarks.delete("/<int:id>")
@jwt_required()
def delete_bookmark(id):
    current_user = get_jwt_identity()

    bookmark = Bookmark.query.filter_by(user_id=current_user, id=id).first()

    if not bookmark:
        return jsonify({'message': 'Item not found'}), 404

    db.session.delete(bookmark)
    db.session.commit()

    return jsonify({
        "message" : "item deleted"
    })


@bookmarks.get("/stats")
@jwt_required()
@swag_from("./docs/bookmarks/stats.yaml")
def get_stats():
    current_user = get_jwt_identity()
    data = []
    items  = Bookmark.query.filter_by(user_id=current_user).all()

    for item in items:
        new_link={
            "visits" : item.visits,
            "url": item.url,
            "id" : item.id,
            "short_url" : item.short_url
        } 

        data.append(new_link)

    return jsonify({"data" : data})