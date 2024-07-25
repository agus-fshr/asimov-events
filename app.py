from flask import Flask, request, jsonify, render_template, redirect, url_for, session
from flask_socketio import SocketIO, emit
import sqlite3

app = Flask(__name__)
app.config['SECRET_KEY'] = 'secret!'
socketio = SocketIO(app)

PASSWORD = 'fernandocasas'

def connect_db():
    return sqlite3.connect('events.db')

@app.route('/')
def home():
    return render_template('index.html')

@app.route('/add_event', methods=['POST'])
def add_event():
    try:
        data = request.get_json()
        print(f"Received data: {data}")  # Debugging line
        name = data.get('name')
        category_id = data.get('category_id')
        start_time = data.get('start_time')
        end_time = data.get('end_time')
        description = data.get('description')

        if not all([name, category_id, start_time, end_time, description]):
            print("Missing data in request")
            return jsonify({"error": "Missing data in request"}), 400

        conn = connect_db()
        c = conn.cursor()

        # Verify category ID exists and get category name
        c.execute('SELECT name FROM categories WHERE id = ?', (category_id,))
        category = c.fetchone()
        print(f"Category query result: {category}")  # Debugging line
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
        print(f"Error: {e}")  # Debugging line
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
    ORDER BY events.start_time DESC
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
    if not session.get('authenticated'):
        return redirect(url_for('login', next=request.url))
    return render_template('add_event.html')

@app.route('/delete_event_form', methods=['GET', 'POST'])
def delete_event_form():
    if request.method == 'POST':
        password = request.form['password']
        if password == PASSWORD:
            session['authenticated'] = True
            return redirect(url_for('delete_event_form'))
        else:
            return render_template('login.html', error='Invalid password')
    
    if not session.get('authenticated'):
        return render_template('login.html')
    
    return render_template('delete_event.html')

@app.route('/delete_event/<int:event_id>', methods=['DELETE'])
def delete_event(event_id):
    try:
        conn = connect_db()
        c = conn.cursor()
        c.execute('DELETE FROM events WHERE id = ?', (event_id,))
        conn.commit()
        conn.close()

        # Emit the event deletion to all connected clients
        socketio.emit('delete_event', {'id': event_id})

        return jsonify({"status": "Event deleted"}), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 400

@app.route('/get_categories', methods=['GET'])
def get_categories():
    conn = connect_db()
    c = conn.cursor()
    c.execute('SELECT id, name FROM categories')
    categories = c.fetchall()
    conn.close()
    return jsonify({"categories": categories})

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        password = request.form['password']
        if password == PASSWORD:
            session['authenticated'] = True
            next_url = request.args.get('next')
            return redirect(next_url or url_for('home'))
        else:
            return render_template('login.html', error='Invalid password')
    
    return render_template('login.html')

@app.route('/velocistas')
def velocistas():
    return render_template('velocistas.html')

@app.route('/sumo')
def sumo():
    return render_template('sumo.html')

@app.route('/minisumo')
def minisumo():
    return render_template('minisumo.html')

@app.route('/futbol')
def futbol():
    return render_template('futbol.html')

@app.route('/links')
def links():
    return render_template('links.html')

if __name__ == '__main__':
    socketio.run(app, debug=True)
