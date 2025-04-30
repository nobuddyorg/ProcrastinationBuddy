from flask import Flask, jsonify, request
from procrastination.procrastination import procrastinate, get_tasks
from config.config import get_config
import requests

app = Flask(__name__)

app.config['EXCUSE_API_URL'] = get_config()

@app.route('/procrastinate', methods=['GET'])
def procrastinate_endpoint():
    url = request.args.get('url', app.config['EXCUSE_API_URL'])
    try:
        task = procrastinate(url)
        return jsonify({'task': task})
    except requests.exceptions.RequestException as e:
        return jsonify({'error': str(e)}), 500

@app.route('/tasks', methods=['GET'])
def get_tasks_endpoint():
    skip = request.args.get('skip', 0, type=int)
    limit = request.args.get('limit', 10, type=int)
    tasks = get_tasks(skip=skip, limit=limit)
    
    return jsonify(tasks)

if __name__ == "__main__":
    app.run(host='0.0.0.0', port=5000)
