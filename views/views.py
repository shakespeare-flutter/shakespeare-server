from flask import Blueprint, request, Response, redirect, jsonify
from app import db
from models import Book, Music
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
    return jsonify(record.result)

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
        return '', 201
    else:
        if record.result is None:
            if record.content is None:
                record.content = request.json['content']
            book_analysis.analyze(record)
        return '', 201

@bp.route('/music', methods=['GET'])
def get_music():    
    id = request.args.get('id')
    # invalid get
    if id is None:
        return 'NO IDENTIFIER', 400
    # check if record exist
    record = Music.query.get(id)
    if record is None:
        return 'INVALID ID', 404
    path = 'music/' + record.path
    if not os.path.isfile(path):
        return 'NO FILE', 404
    def generate():
        with open(path, "rb") as fwav:
            data = fwav.read(1024)
            while data:
                yield data
                data = fwav.read(1024)
    return Response(generate(), mimetype="audio/mp3")

@bp.route('/music', methods=['POST'])
def post_music():    
    if not request.is_json:
        return 'NEED JSON', 400
    if not 'emotion' in request.json:
        return 'NO \'emotion\' IN JSON', 400
    
    emotion = request.json['emotion']
    color = request.json['color']
    weather = request.json['weather']

    result = music_recommend.get_music(emotion, color, weather)
    return redirect('/music?id=' + result)