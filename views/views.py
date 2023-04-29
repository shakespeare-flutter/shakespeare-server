from flask import Blueprint, request, Response
from app import db
from models import Book, Music
import book_analysis
import os.path

bp = Blueprint('main', __name__, url_prefix='/')

@bp.route('/book', methods=['GET'])
def get_book():
    id = request.args.get('id')
    # invalid get
    if id is None:
        return '', 400
    
    # check if record exist
    record = Book.query.filter_by(identifier=id).first()
    if record is None:
        # client must post book
        return '', 204
    if record.content is None:
        # analyzing book
        return '', 205
    return record.content

@bp.route('/book', methods=['POST'])
def post_book():
    id = request.args.get('id')
    # invalid post
    if id is None:
        return '', 400
    
    # check if record exists
    record = Book.query.filter_by(identifier=id).first()
    if record is not None:
        # already analyzed/analyzing ... try get
        return '', 205
    
    # invalid post
    if not 'content' in request.json:
        return '', 400
    
    # add record
    record = Book(identifier=id)
    db.session.add(record)
    db.session.commit()
    # anlayze
    book_analysis.analyze(record, request.json['content'])

    return '', 200

@bp.route('/music', methods=['GET'])
def get_music():    
    id = request.args.get('id')
    # invalid get
    if id is None:
        return '', 400    
    # check if record exist
    record = Music.query.get(id)
    if record is None:
        return 'no record', 404
    path = 'music/' + record.path
    if not os.path.isfile(path):
        return 'no file', 404
        
    def generate():
        with open(path, "rb") as fwav:
            data = fwav.read(1024)
            while data:
                yield data
                data = fwav.read(1024)
    return Response(generate(), mimetype="audio/mp3")

"""
@bp.route('/music', methods=['GET'])
def get_music():
    id = request.args.get('id')
    # invalid get
    if id is None:
        return '', 400    
    # check if record exist
    record = Music.query.get(id)
    if record is None:
        return 'no record', 404
    path = 'music/' + record.path
    if not os.path.isfile(path):
        return 'no file', 404
    
    
    return send_file(path, mimetype="audio/mp3", as_attachment=True)
    
    with open(path, 'rb') as fd:
        bytes = fd.read()
    return jsonify({'msg': 'success', 'size': [img.width, img.height], 'bytes': bytes})
    """