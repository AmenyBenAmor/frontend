from flask import Flask, request, jsonify, send_from_directory
from flask_cors import CORS
import requests
import os

app = Flask(__name__, static_folder='.')
CORS(app)  # Active CORS sur le proxy

# URLs de vos APIs Render (NE LES MODIFIE PAS)
APIS = {
    'text': 'https://gastrocsv-flask-api.onrender.com/predict',
    'fibro': 'https://gastrofibro-api-1.onrender.com/predict',
    'irm': 'https://gastroirm-flask-api-4.onrender.com/predict'
}

@app.route('/')
def index():
    """Sert votre page HTML"""
    return send_from_directory('.', 'index.html')

@app.route('/proxy/predict/text', methods=['POST', 'OPTIONS'])
def proxy_text():
    """Proxy pour l'API texte"""
    if request.method == 'OPTIONS':
        return '', 204
    
    try:
        data = request.get_json()
        print(f"📤 Forwarding to {APIS['text']}")
        print(f"📝 Data: {data}")
        
        response = requests.post(APIS['text'], json=data, timeout=60)
        
        print(f"📥 Response status: {response.status_code}")
        print(f"📄 Response: {response.text[:200]}")
        
        return jsonify(response.json()), response.status_code
    except requests.exceptions.RequestException as e:
        print(f"❌ Error: {str(e)}")
        return jsonify({'error': f'API request failed: {str(e)}'}), 500
    except Exception as e:
        print(f"❌ Error: {str(e)}")
        return jsonify({'error': str(e)}), 500

@app.route('/proxy/predict/fibro', methods=['POST', 'OPTIONS'])
def proxy_fibro():
    """Proxy pour l'API fibroscopie"""
    if request.method == 'OPTIONS':
        return '', 204
    
    try:
        # Essayer avec 'image' d'abord
        if 'image' in request.files:
            files = {'image': request.files['image']}
        elif 'file' in request.files:
            files = {'file': request.files['file']}
        else:
            return jsonify({'error': 'No image file provided'}), 400
        
        print(f"📤 Forwarding image to {APIS['fibro']}")
        
        response = requests.post(APIS['fibro'], files=files, timeout=120)
        
        print(f"📥 Response status: {response.status_code}")
        
        # Si échec avec 'image', réessayer avec 'file'
        if response.status_code == 400 and 'image' in request.files:
            print("🔄 Retrying with 'file' parameter...")
            request.files['image'].seek(0)  # Reset file pointer
            files = {'file': request.files['image']}
            response = requests.post(APIS['fibro'], files=files, timeout=120)
        
        return jsonify(response.json()), response.status_code
    except Exception as e:
        print(f"❌ Error: {str(e)}")
        return jsonify({'error': str(e)}), 500

@app.route('/proxy/predict/irm', methods=['POST', 'OPTIONS'])
def proxy_irm():
    """Proxy pour l'API IRM"""
    if request.method == 'OPTIONS':
        return '', 204
    
    try:
        # Essayer avec 'image' d'abord
        if 'image' in request.files:
            files = {'image': request.files['image']}
        elif 'file' in request.files:
            files = {'file': request.files['file']}
        else:
            return jsonify({'error': 'No image file provided'}), 400
        
        print(f"📤 Forwarding image to {APIS['irm']}")
        
        response = requests.post(APIS['irm'], files=files, timeout=120)
        
        print(f"📥 Response status: {response.status_code}")
        
        # Si échec avec 'image', réessayer avec 'file'
        if response.status_code == 400 and 'image' in request.files:
            print("🔄 Retrying with 'file' parameter...")
            request.files['image'].seek(0)  # Reset file pointer
            files = {'file': request.files['image']}
            response = requests.post(APIS['irm'], files=files, timeout=120)
        
        return jsonify(response.json()), response.status_code
    except Exception as e:
        print(f"❌ Error: {str(e)}")
        return jsonify({'error': str(e)}), 500

@app.route('/health', methods=['GET'])
def health():
    """Route de santé"""
    return jsonify({
        'status': 'ok',
        'proxy': 'enabled',
        'apis': APIS
    }), 200

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port, debug=False)