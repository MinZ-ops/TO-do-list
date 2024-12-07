from flask import Flask, request, jsonify
from flask_cors import CORS
import sqlite3
import os

app = Flask(__name__)
CORS(app)

# 数据库初始化
def init_db():
    conn = sqlite3.connect('todos.db')
    c = conn.cursor()
    c.execute('''CREATE TABLE IF NOT EXISTS categories
                 (id INTEGER PRIMARY KEY AUTOINCREMENT,
                  name TEXT NOT NULL)''')
    c.execute('''CREATE TABLE IF NOT EXISTS todos
                 (id INTEGER PRIMARY KEY AUTOINCREMENT,
                  title TEXT NOT NULL,
                  completed BOOLEAN NOT NULL DEFAULT 0,
                  priority INTEGER DEFAULT 0,
                  category_id INTEGER,
                  FOREIGN KEY (category_id) REFERENCES categories (id))''')
    conn.commit()
    conn.close()

# 初始化数据库
init_db()

# 获取所有待办事项
@app.route('/api/todos', methods=['GET'])
def get_todos():
    conn = sqlite3.connect('todos.db')
    c = conn.cursor()
    status = request.args.get('status', 'all')
    category_id = request.args.get('category_id')
    
    query = '''
        SELECT t.*, c.name as category_name 
        FROM todos t 
        LEFT JOIN categories c ON t.category_id = c.id
        WHERE 1=1
    '''
    if status == 'active':
        query += ' AND completed = 0'
    elif status == 'completed':
        query += ' AND completed = 1'
    if category_id:
        query += f' AND category_id = {category_id}'
    
    c.execute(query)
    todos = [{'id': row[0], 'title': row[1], 'completed': bool(row[2]), 
              'priority': row[3], 'category_id': row[4], 'category_name': row[5]}
             for row in c.fetchall()]
    conn.close()
    return jsonify(todos)

# 添加新的待办事项
@app.route('/api/todos', methods=['POST'])
def add_todo():
    data = request.json
    conn = sqlite3.connect('todos.db')
    c = conn.cursor()
    c.execute('INSERT INTO todos (title, priority, category_id) VALUES (?, ?, ?)',
              (data['title'], data.get('priority', 0), data.get('category_id')))
    conn.commit()
    todo_id = c.lastrowid
    conn.close()
    return jsonify({'id': todo_id, 'title': data['title'], 'completed': False})

# 更新待办事项
@app.route('/api/todos/<int:todo_id>', methods=['PUT'])
def update_todo(todo_id):
    data = request.json
    conn = sqlite3.connect('todos.db')
    c = conn.cursor()
    updates = []
    values = []
    if 'title' in data:
        updates.append('title = ?')
        values.append(data['title'])
    if 'completed' in data:
        updates.append('completed = ?')
        values.append(data['completed'])
    values.append(todo_id)
    
    query = f'UPDATE todos SET {", ".join(updates)} WHERE id = ?'
    c.execute(query, values)
    conn.commit()
    conn.close()
    return jsonify({'success': True})

# 删除待办事项
@app.route('/api/todos/<int:todo_id>', methods=['DELETE'])
def delete_todo(todo_id):
    conn = sqlite3.connect('todos.db')
    c = conn.cursor()
    c.execute('DELETE FROM todos WHERE id = ?', (todo_id,))
    conn.commit()
    conn.close()
    return jsonify({'success': True})

# 清除已完成的待办事项
@app.route('/api/todos/clear-completed', methods=['DELETE'])
def clear_completed():
    conn = sqlite3.connect('todos.db')
    c = conn.cursor()
    c.execute('DELETE FROM todos WHERE completed = 1')
    conn.commit()
    conn.close()
    return jsonify({'success': True})

# 获取所有分类
@app.route('/api/categories', methods=['GET'])
def get_categories():
    # ... 代码内容 