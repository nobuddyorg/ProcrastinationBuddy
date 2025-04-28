from flask import Flask, jsonify, request
from procrastination.procrastination import procrastinate
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

if __name__ == "__main__":
    app.run(host='0.0.0.0', port=5000)
