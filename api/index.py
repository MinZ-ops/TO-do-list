from flask import Flask, request, jsonify
from flask_cors import CORS
import sqlite3
import datetime

app = Flask(__name__)
CORS(app)  # 启用跨域请求支持

# 创建数据库和表
def init_db():
    conn = sqlite3.connect('todos.db')
    c = conn.cursor()
    
    # 创建分类表
    c.execute('''
        CREATE TABLE IF NOT EXISTS categories
        (id INTEGER PRIMARY KEY AUTOINCREMENT,
         name TEXT NOT NULL UNIQUE)
    ''')
    
    # 创建待办事项表，添加category_id字段
    c.execute('''
        CREATE TABLE IF NOT EXISTS todos
        (id INTEGER PRIMARY KEY AUTOINCREMENT,
         title TEXT NOT NULL,
         completed BOOLEAN NOT NULL DEFAULT 0,
         priority INTEGER DEFAULT 0,
         category_id INTEGER,
         created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
         FOREIGN KEY (category_id) REFERENCES categories (id))
    ''')
    
    # 插入默认分类
    default_categories = ['工作', '生活', '学习', '其他']
    for category in default_categories:
        try:
            c.execute('INSERT INTO categories (name) VALUES (?)', (category,))
        except sqlite3.IntegrityError:
            pass  # 如果分类已存在，跳过
    
    conn.commit()
    conn.close()

# 初始化数据库
init_db()

# 获取所有分类
@app.route('/categories', methods=['GET'])
def get_categories():
    conn = sqlite3.connect('todos.db')
    c = conn.cursor()
    c.execute('SELECT * FROM categories')
    categories = [{'id': row[0], 'name': row[1]} for row in c.fetchall()]
    conn.close()
    return jsonify(categories)

# 添加新分类
@app.route('/categories', methods=['POST'])
def add_category():
    data = request.get_json()
    if not data or 'name' not in data:
        return jsonify({'error': 'Missing category name'}), 400
    
    conn = sqlite3.connect('todos.db')
    c = conn.cursor()
    try:
        c.execute('INSERT INTO categories (name) VALUES (?)', (data['name'],))
        conn.commit()
        category_id = c.lastrowid
        conn.close()
        return jsonify({'id': category_id, 'name': data['name']}), 201
    except sqlite3.IntegrityError:
        conn.close()
        return jsonify({'error': 'Category already exists'}), 400

# 获取所有待办事项
@app.route('/todos', methods=['GET'])
def get_todos():
    status = request.args.get('status', 'all')
    category_id = request.args.get('category_id')
    
    conn = sqlite3.connect('todos.db')
    c = conn.cursor()
    
    query = 'SELECT t.*, c.name as category_name FROM todos t LEFT JOIN categories c ON t.category_id = c.id WHERE 1=1'
    params = []
    
    if status == 'active':
        query += ' AND completed = 0'
    elif status == 'completed':
        query += ' AND completed = 1'
    
    if category_id:
        query += ' AND category_id = ?'
        params.append(category_id)
    
    query += ' ORDER BY priority DESC, created_at DESC'
    
    c.execute(query, params)
    todos = [{
        'id': row[0],
        'title': row[1],
        'completed': bool(row[2]),
        'priority': row[3],
        'category_id': row[4],
        'created_at': row[5],
        'category_name': row[6]
    } for row in c.fetchall()]
    
    conn.close()
    return jsonify(todos)

# 添加新的待办事项
@app.route('/todos', methods=['POST'])
def add_todo():
    data = request.get_json()
    if not data or 'title' not in data:
        return jsonify({'error': 'Missing title'}), 400
    
    priority = data.get('priority', 0)
    category_id = data.get('category_id')
    
    conn = sqlite3.connect('todos.db')
    c = conn.cursor()
    c.execute('INSERT INTO todos (title, priority, category_id) VALUES (?, ?, ?)',
             (data['title'], priority, category_id))
    conn.commit()
    todo_id = c.lastrowid
    conn.close()
    
    return jsonify({
        'id': todo_id,
        'title': data['title'],
        'completed': False,
        'priority': priority,
        'category_id': category_id
    }), 201

# 更新待办事项状态
@app.route('/todos/<int:todo_id>', methods=['PUT'])
def update_todo(todo_id):
    data = request.get_json()
    conn = sqlite3.connect('todos.db')
    c = conn.cursor()
    
    if 'completed' in data:
        c.execute('UPDATE todos SET completed = ? WHERE id = ?', 
                 (data['completed'], todo_id))
    if 'title' in data:
        c.execute('UPDATE todos SET title = ? WHERE id = ?', 
                 (data['title'], todo_id))
    
    conn.commit()
    conn.close()
    return jsonify({'success': True})

# 删除待办事项
@app.route('/todos/<int:todo_id>', methods=['DELETE'])
def delete_todo(todo_id):
    conn = sqlite3.connect('todos.db')
    c = conn.cursor()
    c.execute('DELETE FROM todos WHERE id = ?', (todo_id,))
    conn.commit()
    conn.close()
    return jsonify({'success': True})

# 清除已完成的待办事项
@app.route('/todos/clear-completed', methods=['DELETE'])
def clear_completed():
    conn = sqlite3.connect('todos.db')
    c = conn.cursor()
    c.execute('DELETE FROM todos WHERE completed = 1')
    conn.commit()
    conn.close()
    return jsonify({'success': True})

if __name__ == '__main__':
    app.run(debug=True, port=5001)