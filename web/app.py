from flask import Flask, render_template, jsonify
from ..api.fronius import FroniusClient
from ..automations.manager import AutomationManager

app = Flask(__name__)

# Initialize components
fronius = FroniusClient(host="localhost")  # Update with your inverter's IP
automation_manager = AutomationManager()

@app.route('/')
def index():
    """Render the main dashboard page."""
    return render_template('index.html')

@app.route('/api/status')
def get_status():
    """Get current system status."""
    power_data = fronius.get_power_data()
    automation_status = automation_manager.get_status()
    
    return jsonify({
        'power_data': power_data,
        'automation': automation_status
    })

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000) 