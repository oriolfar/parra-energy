#!/usr/bin/env python3

print("🔧 CONSUMPTION BUTTON DEBUG TEST")
print("="*50)

# Simple test server
from flask import Flask, render_template, request, jsonify
import os

app = Flask(__name__, template_folder='web/templates')

@app.route('/')
def home():
    return render_template('index.html')

@app.route('/api/mock/set-consumption', methods=['POST'])
def set_consumption():
    print("\n🎯 SUCCESS! set-consumption endpoint hit!")
    data = request.get_json()
    watts = data.get('watts', 0)
    print(f"🔧 Received watts: {watts}")
    return jsonify({
        'status': 'success',
        'message': f'Consumption set to {watts}W',
        'watts': watts
    })

@app.route('/api/status')
def status():
    return jsonify({
        'production': 1000,
        'consumption': 500,
        'net_power': 500,
        'status': 'ok'
    })

# Mock other endpoints to prevent errors
@app.route('/api/analytics/tips')
def tips():
    return jsonify({'tips': []})

@app.route('/api/analytics/daily-report')
def daily_report():
    return jsonify({'report': 'mock'})

@app.route('/api/analytics/weekly-forecast')
def weekly_forecast():
    return jsonify({'forecast': 'mock'})

@app.route('/api/analytics/historical')
def historical():
    return jsonify({'analysis': 'mock'})

@app.route('/api/weather/best-hours')
def best_hours():
    return jsonify({'hours': []})

@app.route('/api/weather/forecast')
def forecast():
    return jsonify({'forecast': 'mock'})

@app.route('/api/weather/enhanced-forecast')
def enhanced_forecast():
    return jsonify({'forecast': 'mock'})

@app.route('/history5min/<date>')
def history(date):
    return jsonify({'data': []})

if __name__ == '__main__':
    print("🌟 Starting consumption button debug server...")
    print("🎯 Test plan:")
    print("   1. Open browser to http://127.0.0.1:5001")
    print("   2. Open browser console (F12)")
    print("   3. Try typing: setConsumption()")
    print("   4. Try clicking the consumption Aplicar button")
    print("   5. Look for debug messages in both console and terminal")
    print("")
    
    app.run(host='0.0.0.0', port=5001, debug=False) 