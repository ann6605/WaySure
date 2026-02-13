from flask import Flask, render_template, request, jsonify
import sqlite3
from datetime import datetime, timedelta

app = Flask(__name__)

# Database_helper
def get_db():
    conn = sqlite3.connect('waysure.db')
    conn.row_factory = sqlite3.Row  # Return rows as dictionaries
    return conn

# Safety_score_calculation
def calculate_safety_score(route_id):
    conn = get_db()
    
    # Get incidents from last 30 days
    thirty_days_ago = datetime.now() - timedelta(days=30)
    
    incidents = conn.execute('''
        SELECT incident_type, severity, 
               julianday('now') - julianday(reported_at) as days_ago
        FROM incidents
        WHERE route_id = ? AND reported_at > ?
    ''', (route_id, thirty_days_ago)).fetchall()
    
    conn.close()
    
    # If no incidents, high safety score
    if not incidents:
        return 95
    
    weighted_count = 0
    severity_sum = 0
    severity_map = {'low': 1, 'medium': 2, 'high': 3}
    
    for inc in incidents:
        # Time decay - recent incidents matter more
        days = inc['days_ago']
        if days <= 7:
            weight = 1.0
        elif days <= 14:
            weight = 0.7
        else:
            weight = 0.4
        
        weighted_count += weight
        severity_sum += severity_map[inc['severity']]
    
    # Calculate average severity
    severity_avg = severity_sum / len(incidents)
    
    # Time of day risk (simple version)
    current_hour = datetime.now().hour
    time_risk = 1.5 if (current_hour >= 20 or current_hour <= 6) else 1.0
    
    # Final score calculation
    score = 100 - (15 * weighted_count + 10 * severity_avg + 5 * time_risk)
    
    # Clamp between 0 and 100
    return max(0, min(100, int(score)))

# Routes
@app.route('/')
def index():
    return render_template('index.html')

@app.route('/api/routes/search', methods=['GET'])
def search_routes():
    origin = request.args.get('origin', '')
    destination = request.args.get('destination', '')
    
    conn = get_db()
    
    # Search routes
    query = '''
        SELECT * FROM routes 
        WHERE start_location LIKE ? OR end_location LIKE ?
        OR route_name LIKE ? OR route_number LIKE ?
    '''
    search_term = f'%{origin if origin else destination}%'
    routes = conn.execute(query, (search_term, search_term, search_term, search_term)).fetchall()
    
    conn.close()
    
    # Calculate safety scores
    results = []
    for route in routes:
        score = calculate_safety_score(route['route_id'])
        
        # Determine status
        if score >= 70:
            status = 'safe'
        elif score >= 50:
            status = 'caution'
        else:
            status = 'unsafe'
        
        results.append({
            'route_id': route['route_id'],
            'route_number': route['route_number'],
            'route_name': route['route_name'],
            'start': route['start_location'],
            'end': route['end_location'],
            'distance': route['distance_km'],
            'duration': route['avg_duration_mins'],
            'safety_score': score,
            'status': status
        })
    
    # Sort by safety score (highest first)
    results.sort(key=lambda x: x['safety_score'], reverse=True)
    
    return jsonify(results)

@app.route('/api/routes/<int:route_id>/details', methods=['GET'])
def route_details(route_id):
    conn = get_db()
    
    # Get route info
    route = conn.execute('SELECT * FROM routes WHERE route_id = ?', (route_id,)).fetchone()
    
    # Get recent incidents (last 7 days)
    seven_days_ago = datetime.now() - timedelta(days=7)
    incidents = conn.execute('''
        SELECT * FROM incidents 
        WHERE route_id = ? AND reported_at > ?
        ORDER BY reported_at DESC
    ''', (route_id, seven_days_ago)).fetchall()
    
    conn.close()
    
    if not route:
        return jsonify({'error': 'Route not found'}), 404
    
    # Format incidents
    incident_list = []
    for inc in incidents:
        incident_list.append({
            'type': inc['incident_type'],
            'severity': inc['severity'],
            'description': inc['description'],
            'date': inc['reported_at'],
            'location': {'lat': inc['latitude'], 'lng': inc['longitude']}
        })
    
    return jsonify({
        'route': dict(route),
        'safety_score': calculate_safety_score(route_id),
        'recent_incidents': incident_list
    })

@app.route('/api/incidents/report', methods=['POST'])
def report_incident():
    data = request.json
    
    # Validate required fields
    required = ['route_id', 'incident_type', 'severity', 'latitude', 'longitude']
    if not all(field in data for field in required):
        return jsonify({'error': 'Missing required fields'}), 400
    
    conn = get_db()
    cursor = conn.cursor()
    
    cursor.execute('''
        INSERT INTO incidents (route_id, incident_type, severity, 
                              latitude, longitude, description, reported_at)
        VALUES (?, ?, ?, ?, ?, ?, ?)
    ''', (data['route_id'], data['incident_type'], data['severity'],
          data['latitude'], data['longitude'], 
          data.get('description', ''), datetime.now()))
    
    incident_id = cursor.lastrowid
    conn.commit()
    conn.close()
    
    return jsonify({
        'success': True,
        'incident_id': incident_id,
        'message': 'Incident reported successfully'
    })

@app.route('/api/panic', methods=['POST'])
def panic_alert():
    data = request.json
    
    # Validate
    if 'latitude' not in data or 'longitude' not in data:
        return jsonify({'error': 'Location required'}), 400
    
    conn = get_db()
    cursor = conn.cursor()
    
    # Store panic_alert
    cursor.execute('''
        INSERT INTO panic_alerts (user_id, latitude, longitude, alert_time)
        VALUES (?, ?, ?, ?)
    ''', (data.get('user_id', 1), data['latitude'], 
          data['longitude'], datetime.now()))
    
    alert_id = cursor.lastrowid
    conn.commit()
    conn.close()
    
    # Generate Google Maps link
    maps_link = f"https://maps.google.com/?q={data['latitude']},{data['longitude']}"
    
    # In production: Send SMS/Email here
    
    return jsonify({
        'success': True,
        'alert_id': alert_id,
        'maps_link': maps_link,
        'message': 'Emergency alert activated'
    })

@app.route('/api/stats', methods=['GET'])
def get_stats():
    conn = get_db()
    
    
    total_routes = conn.execute('SELECT COUNT(*) FROM routes').fetchone()[0]
    
    # Total incidents (last 30 days)
    thirty_days = datetime.now() - timedelta(days=30)
    total_incidents = conn.execute(
        'SELECT COUNT(*) FROM incidents WHERE reported_at > ?', 
        (thirty_days,)
    ).fetchone()[0]
    
    # Most dangerous route
    cursor = conn.cursor()
    routes = cursor.execute('SELECT route_id, route_number FROM routes').fetchall()
    
    worst_route = None
    lowest_score = 100
    
    for route in routes:
        score = calculate_safety_score(route['route_id'])
        if score < lowest_score:
            lowest_score = score
            worst_route = route['route_number']
    
    conn.close()
    
    return jsonify({
        'total_routes': total_routes,
        'total_incidents': total_incidents,
        'most_dangerous_route': worst_route,
        'lowest_safety_score': lowest_score
    })

@app.route('/report')
def report_page():
    return render_template('report.html')

if __name__ == '__main__':
    print("🚀 Starting WaySure server...")
    print("📍 Open browser at: http://127.0.0.1:5000")
    app.run(debug=True, port=5000)