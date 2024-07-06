from flask import Flask, request, make_response, jsonify
from flask_cors import CORS
from flask_migrate import Migrate

from models import db, Message

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///app.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.json.compact = False

CORS(app)
migrate = Migrate(app, db)

db.init_app(app)

@app.route('/messages', methods=['GET', 'POST'])
def messages():
    if request.method == 'GET':
        messages = Message.query.order_by(Message.created_at.asc()).all()
        messages_serialized = [m.to_dict() for m in messages]
        return make_response(messages_serialized, 200)
    elif request.method == 'POST':
        body = request.json.get('body')
        username = request.json.get('username')

        if not body or not username:
            return make_response({'error': 'Missing body or username'}, 400)

        message = Message(body=body, username=username)
        db.session.add(message)
        db.session.commit()

        return make_response(message.to_dict(), 201)
    

@app.route('/messages/<int:id>', methods=['GET','PATCH', 'DELETE'])
def messages_by_id(id):
    message = Message.query.filter_by(id=id).first() 
    if request.method == 'PATCH': 

        if not message:
            return make_response({'error': 'Message not found'}, 404)

        body = request.json.get('body')
        username = request.json.get('username')

        if body:
            message.body = body
        if username:
            message.username = username

        db.session.commit()

        return make_response(message.to_dict(), 200)
    elif request.method == 'DELETE':
        db.session.delete(message)
        db.session.commit()

        response_body = {
            "delete_message": True,
            "message": "Message delted."
        }
        return make_response(response_body, 200)

if __name__ == '__main__':
    app.run(port=5555)