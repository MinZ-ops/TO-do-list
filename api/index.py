from flask import Flask, request, jsonify
from flask_cors import CORS
import os
import json

app = Flask(__name__)
CORS(app)

# 使用内存中的数据结构代替 SQLite
todos = []
categories = []
todo_id_counter = 1
category_id_counter = 1

@app.route('/api/todos', methods=['GET'])
def get_todos():
    try:
        status = request.args.get('status', 'all')
        category_id = request.args.get('category_id')
        
        filtered_todos = todos
        if status == 'active':
            filtered_todos = [t for t in todos if not t['completed']]
        elif status == 'completed':
            filtered_todos = [t for t in todos if t['completed']]
        
        if category_id:
            filtered_todos = [t for t in filtered_todos if t['category_id'] == int(category_id)]
            
        return jsonify(filtered_todos)
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/api/todos', methods=['POST'])
def add_todo():
    try:
        global todo_id_counter
        data = request.json
        new_todo = {
            'id': todo_id_counter,
            'title': data['title'],
            'completed': False,
            'priority': data.get('priority', 0),
            'category_id': data.get('category_id')
        }
        todos.append(new_todo)
        todo_id_counter += 1
        return jsonify(new_todo)
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/api/categories', methods=['GET'])
def get_categories():
    try:
        return jsonify(categories)
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/api/categories', methods=['POST'])
def add_category():
    try:
        global category_id_counter
        data = request.json
        new_category = {
            'id': category_id_counter,
            'name': data['name']
        }
        categories.append(new_category)
        category_id_counter += 1
        return jsonify(new_category)
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/api/todos/<int:todo_id>', methods=['PUT'])
def update_todo(todo_id):
    try:
        data = request.json
        for todo in todos:
            if todo['id'] == todo_id:
                if 'title' in data:
                    todo['title'] = data['title']
                if 'completed' in data:
                    todo['completed'] = data['completed']
                return jsonify(todo)
        return jsonify({"error": "Todo not found"}), 404
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/api/todos/<int:todo_id>', methods=['DELETE'])
def delete_todo(todo_id):
    try:
        global todos
        todos = [t for t in todos if t['id'] != todo_id]
        return jsonify({"success": True})
    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == '__main__':
    app.run(debug=True)