from flask import Flask, request, jsonify, render_template
from flask_socketio import SocketIO, emit
import sqlite3

app = Flask(__name__)
app.config['SECRET_KEY'] = 'secret!'
socketio = SocketIO(app, cors_allowed_origins="*")

def connect_db():
    return sqlite3.connect('events.db')

@app.route('/')
def home():
    return render_template('index.html')

@app.route('/add_event', methods=['POST'])
def add_event():
    try:
        data = request.get_json()
        name = data['name']
        category_id = data['category_id']
        start_time = data['start_time']
        end_time = data['end_time']
        description = data['description']

        print(f"Received data: {data}")

        conn = connect_db()
        c = conn.cursor()

        # Verify category ID exists and get category name
        c.execute('SELECT name FROM categories WHERE id = ?', (category_id,))
        category = c.fetchone()
        if not category:
            conn.close()
            return jsonify({"error": "Invalid category ID"}), 400

        category_name = category[0]

        # Insert event
        c.execute('''
        INSERT INTO events (name, category_id, start_time, end_time, description)
        VALUES (?, ?, ?, ?, ?)
        ''', (name, category_id, start_time, end_time, description))
        conn.commit()
        event_id = c.lastrowid
        conn.close()

        event = {
            "id": event_id,
            "name": name,
            "category_name": category_name,
            "start_time": start_time,
            "end_time": end_time,
            "description": description
        }

        # Emit the event to all connected clients
        socketio.emit('new_event', event)

        return jsonify({"status": "Event added"}), 201

    except Exception as e:
        print(f"Error: {e}")
        return jsonify({"error": str(e)}), 400

@socketio.on('connect')
def handle_connect():
    print('Client connected')

@socketio.on('new_event')
def handle_new_event(data):
    print(f"Received new event: {data}")
    emit('new_event', data)

@app.route('/events', methods=['GET'])
def get_events():
    conn = connect_db()
    c = conn.cursor()
    c.execute('''
    SELECT events.id, categories.name as category_name, events.name, events.start_time, events.end_time, events.description
    FROM events
    JOIN categories ON events.category_id = categories.id
    ORDER BY events.id DESC
    ''')
    events = c.fetchall()
    conn.close()

    event_list = []
    for event in events:
        event_list.append({
            "id": event[0],
            "category_name": event[1],
            "name": event[2],
            "start_time": event[3],
            "end_time": event[4],
            "description": event[5]
        })
    
    return jsonify(event_list)

@app.route('/add_event_form')
def add_event_form():
    return render_template('add_event.html')

@app.route('/get_categories', methods=['GET'])
def get_categories():
    conn = connect_db()
    c = conn.cursor()
    c.execute('SELECT id, name FROM categories')
    categories = c.fetchall()
    conn.close()
    return jsonify({"categories": categories})

if __name__ == '__main__':
    socketio.run(app, debug=True)
