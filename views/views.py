from flask import Blueprint, request, Response, redirect
import json
from models import Book
import book_analysis
from book_analysis import processing, join
import music_recommend
import os.path
import traceback
import uuid
from app import db

bp = Blueprint('main', __name__, url_prefix='/')

BOOK_PATH = 'books/'

@bp.route('/book', methods=['GET'])
def get_book():
    id = request.args.get('id')
    # invalid get
    if id is None:
        return 'NO IDENTIFIER', 400
    id = int(id)
    # check if record exist
    record:Book = Book.query.get(id)
    if record is None:
        return 'NO RECORD', 404
    
    # no result
    if not record.result_exists():
        if not processing(id):
            return 'LOST CONTENT', 404
        join(id)
        db.session.refresh(record)

    with open(record.result, 'r', encoding='utf-8') as f:
        s = f.read()
    if s is None:
        os.remove(record.result)
        return 'LOST CONTENT', 404
    return Response(json.dumps(s, ensure_ascii=False), content_type='application/json')

@bp.route('/book', methods=['POST'])
def post_book():
    if not 'book' in request.files:
        return 'NO FILE', 400
    file = request.files['book']    
    if file is None:
        return 'NO FILE', 400
    
    os.makedirs('processing', exist_ok=True)
    path = os.path.join('processing', ''.join((str(uuid.uuid1()), '.epub')))
    print(path)
    file.save(path)
    
    try:
        id = book_analysis.handle_post(path)
        return Response(json.dumps({'id':id}, ensure_ascii=False), content_type='application/json')
    except Exception as e:
        traceback.print_exc()
        return str(e), 400

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