from flask import Flask, request, jsonify, send_from_directory
from flask_cors import CORS
import requests
import os

app = Flask(__name__, static_folder='.')
CORS(app)  # Active CORS pour ce proxy

# URLs de vos APIs Render (ne les modifie pas)
APIS = {
    'text': 'https://gastrocsv-flask-api.onrender.com/predict',
    'fibro': 'https://gastrofibro-api-1.onrender.com/predict',
    'irm': 'https://gastroirm-flask-api-4.onrender.com/predict'
}

@app.route('/')
def index():
    """Sert votre fichier HTML"""
    return send_from_directory('.', 'index.html')

@app.route('/proxy/predict/text', methods=['POST'])
def proxy_text():
    """Proxy pour l'API texte"""
    try:
        data = request.get_json()
        response = requests.post(APIS['text'], json=data, timeout=200)
        return jsonify(response.json()), response.status_code
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/proxy/predict/fibro', methods=['POST'])
def proxy_fibro():
    """Proxy pour l'API fibroscopie"""
    try:
        files = {'image': request.files['image']} if 'image' in request.files else {'file': request.files['file']}
        response = requests.post(APIS['fibro'], files=files, timeout=120)
        return jsonify(response.json()), response.status_code
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/proxy/predict/irm', methods=['POST'])
def proxy_irm():
    """Proxy pour l'API IRM"""
    try:
        files = {'image': request.files['image']} if 'image' in request.files else {'file': request.files['file']}
        response = requests.post(APIS['irm'], files=files, timeout=120)
        return jsonify(response.json()), response.status_code
    except Exception as e:
        return jsonify({'error': str(e)}), 500

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port, debug=True)