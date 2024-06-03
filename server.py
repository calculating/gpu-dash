from flask import Flask, request, jsonify
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///gpu_data.db'
db = SQLAlchemy(app)

class GPUData(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    gpu_id = db.Column(db.String(100), nullable=False)
    gpu_watts = db.Column(db.Integer, nullable=True)
    gpu_mem = db.Column(db.Integer, nullable=True)
    timestamp = db.Column(db.DateTime, default=datetime.utcnow)

@app.route('/log', methods=['POST'])
def log_data():
    try:
        data = request.get_json()
        if 'gpu_id' not in data or not isinstance(data['gpu_id'], str):
            return jsonify({'message': 'Invalid gpu_id'}), 400
        
        new_entry = GPUData(
            gpu_id=data['gpu_id'],
            gpu_watts=data.get('gpu_watts'),
            gpu_mem=data.get('gpu_mem')
        )
        db.session.add(new_entry)
        db.session.commit()
        return jsonify({'message': 'Data logged'}), 200
    except Exception as e:
        return jsonify({'message': str(e)}), 500

@app.route('/data', methods=['POST'])
def get_data():
    try:
        data = request.get_json()
        start_timestamp = datetime.strptime(data['start_timestamp'], '%Y-%m-%d %H:%M:%S')
        logs = GPUData.query.filter(GPUData.timestamp >= start_timestamp).all()
        
        result = {}
        for log in logs:
            if log.gpu_id not in result:
                result[log.gpu_id] = []
            result[log.gpu_id].append({
                'timestamp': log.timestamp.strftime('%Y-%m-%d %H:%M:%S'),
                'gpu_watts': log.gpu_watts,
                'gpu_mem': log.gpu_mem
            })
        
        return jsonify(result), 200
    except Exception as e:
        return jsonify({'message': str(e)}), 500

if __name__ == '__main__':
    with app.app_context():
        db.create_all()
    app.run(host='0.0.0.0', port=5000)
