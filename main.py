from flask import Flask,request,jsonify
from flask_sqlalchemy import SQLAlchemy
from flask_marshmallow import Marshmallow
from datetime import datetime
import redis
from flask_caching import Cache

app = Flask(__name__)

app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///crud.db"
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

#Used caching using redis
cache  = Cache(config={"CACHE_TYPE": "RedisCache","CACHE_REDIS_HOST":"0.0.0.0",
"CACHE_REDIS_PORT":6379})


db = SQLAlchemy(app)
ma = Marshmallow(app)

class TodoList(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    public_id = db.Column(db.String(50),unique=True)
    title = db.Column(db.String(200))
    description = db.Column(db.String(300), nullable = False)
    date_created = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)


class TodoListSchema(ma.Schema):
    class Meta:
        fields = ('id', 'title', 'description', 'date_created')


# instantiate schema objects for todolist and todolists
todolist_schema = TodoListSchema(many=False)
todolists_schema = TodoListSchema(many=True)

@app.route('/todolist',methods=["POST"])
@cache.cached(timeout=3000)
def create_task():
    try:
        title = request.json['title']
        description = request.json['description']

        new_todo = TodoList(title = title,description = description)

        db.session.add(new_todo)
        db.session.commit()

        return todolist_schema.jsonify(new_todo)

    except Exception as e:
        return jsonify({"Error" : "Invalid Request"})

@app.route('/')
@cache.cached(timeout=5000)
def get_tasks():
    todos = TodoList.query.all()
    result_set = todolists_schema.dump(todos)
    return jsonify(result_set)


@app.route('/todolist/<int:id>',methods=["PUT"])
@cache.cached(timeout=36000)
def update_task(id):
    todo = TodoList.query.get_or_404(int(id))
    try:
        title = request.json['title']
        description = request.json['description']

        todo.title = title
        todo.description = description

        db.session.commit()
    except Exception as e:
        return jsonify({"Error": "Invalid request, please try again."})
        
    return todolist_schema.jsonify(todo)



@app.route("/todolist/<int:id>", methods=["DELETE"])
@cache.cached(timeout=50000)
def delete_todo(id):
    todo = TodoList.query.get_or_404(int(id))
    db.session.delete(todo)
    db.session.commit()
    return jsonify({"Success" : "Todo deleted."})


if __name__ == "__main__":
    app.run('0.0.0.0',debug=True,port=8080)