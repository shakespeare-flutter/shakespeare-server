from flask import Blueprint, request, Response, redirect, jsonify, make_response
import json
from app import db
from models import Book
import book_analysis
import music_recommend
import os.path
import time

bp = Blueprint('main', __name__, url_prefix='/')

BOOK_PATH = 'books/'

@bp.route('/book', methods=['GET'])
def get_book():
    id = request.args.get('id')
    # invalid get
    if id is None:
        return 'NO IDENTIFIER', 400
    # check if record exist
    record = Book.query.filter_by(identifier=id).first()
    if record is None:
        return 'NO RECORD', 404
    
    if record.result is None:
        if record.content is None:
            return 'LOST CONTENT', 404
        if not record.processing:
            book_analysis.analyze(record)

    while record.processing:
        print('waiting...' + id)
        time.sleep(1)

    return Response(json.dumps(record.result, ensure_ascii=False), content_type='application/json')

@bp.route('/book', methods=['POST'])
def post_book():
    id = request.args.get('id')
    # invalid post
    if id is None:
        return 'NO IDENTIFIER', 400
    if not request.is_json:
        return 'NEED JSON', 400
    if not 'content' in request.json:
        return 'NO \'content\' IN JSON', 400
    
    # check if record exists
    record = Book.query.filter_by(identifier=id).first()
    if record is None:
        record = Book(identifier=id, content=request.json['content'])
        db.session.add(record)
        book_analysis.analyze(record)
        return 'NEW RECORD ADDED', 201
    else:
        if record.result is None:
            if record.content is None:
                record.content = request.json['content']
                book_analysis.analyze(record)
                return 'NEW CONTENT ADDED', 201
            else:
                book_analysis.analyze(record)
                return 'ANALYZED', 201
        else:
            return 'ANALYZED ALREADY', 201

@bp.route('/music', methods=['GET'])
def get_music():    
    id = request.args.get('id')
    # invalid get
    if id is None:
        return 'NO IDENTIFIER', 400
    
    # check if data exist
    try:
        path = music_recommend.get_path(id)
    except Exception as e:
        return str(e), 400
    if path is None:
        return 'INVALID ID', 404
    path = 'music/' + path
    if not os.path.isfile(path):
        return 'NO FILE', 404
    def generate():
        with open(path, "rb") as fwav:
            data = fwav.read(1024)
            while data:
                yield data
                data = fwav.read(1024)
    return Response(generate(), mimetype="audio/mp3")

@bp.route('/music_info', methods=['GET'])
def get_music_info():
    id = request.args.get('id')
    # invalid get
    if id is None:
        return 'NO IDENTIFIER', 400
    # check if data exist
    try:
        result = music_recommend.get_info(id)
    except Exception as e:
        return str(e), 400
    if result is None:
        return 'INVALID ID', 404
    return Response(json.dumps(result, ensure_ascii=False), content_type='application/json')

@bp.route('/music', methods=['POST'])
def post_music():
    if not request.is_json:
        return 'NEED JSON', 400
    if not 'emotion' in request.json:
        return 'NO \'emotion\' IN JSON', 400
    
    emotion = request.json['emotion']
    color = request.json['color']
    weather = request.json['weather']

    try:
        result = music_recommend.get_music(emotion, color, weather)
    except Exception as e:
        return str(e), 400

    return redirect('/music?id=' + result)