from flask import Flask, request, jsonify, send_from_directory
from flask_cors import CORS
import requests
import os
import json
import time

app = Flask(__name__, static_folder='.')
CORS(app)  # Active CORS pour ce proxy

# URLs de vos APIs Render
APIS = {
    'text': 'https://gastrocsv-flask-api.onrender.com/predict',
    'fibro': 'https://gastrofibro-api-1.onrender.com/predict',
    'irm': 'https://gastroirm-flask-api-4.onrender.com/predict'
}

def retry_request(api_url, method='POST', json_data=None, files=None, max_retries=3):
    """
    Fonction pour réessayer les requêtes en cas d'erreur 429
    """
    retry_delay = 2  # Commence avec 2 secondes
    
    for attempt in range(max_retries):
        try:
            if files:
                response = requests.post(api_url, files=files, timeout=300)
            else:
                response = requests.post(
                    api_url, 
                    json=json_data, 
                    timeout=300,
                    headers={'Content-Type': 'application/json'}
                )
            
            # Si on reçoit un 429, on attend et on réessaye
            if response.status_code == 429:
                if attempt < max_retries - 1:
                    print(f"⏳ Rate limit atteint, attente de {retry_delay} secondes... (tentative {attempt + 1}/{max_retries})")
                    time.sleep(retry_delay)
                    retry_delay *= 2  # Augmente le délai (backoff exponentiel)
                    continue
                else:
                    # Dernier essai échoué
                    return None, 429, "Service temporairement surchargé. Réessayez dans quelques instants."
            
            # Succès ou autre erreur
            return response, response.status_code, None
            
        except requests.exceptions.Timeout:
            if attempt < max_retries - 1:
                print(f"⏳ Timeout, nouvelle tentative dans {retry_delay} secondes...")
                time.sleep(retry_delay)
                retry_delay *= 2
                continue
            return None, 504, "API timeout. Le service démarre peut-être. Réessayez dans 30 secondes."
        
        except requests.exceptions.RequestException as e:
            return None, 500, f"Erreur de requête: {str(e)}"
    
    return None, 500, "Échec après plusieurs tentatives"

@app.route('/')
def index():
    """Sert votre fichier HTML"""
    return send_from_directory('.', 'index.html')

@app.route('/proxy/predict/text', methods=['POST'])
def proxy_text():
    """Proxy pour l'API texte"""
    try:
        data = request.get_json()
        print(f"📤 Sending to text API: {APIS['text']}")
        print(f"📦 Data: {data}")
        
        response, status_code, error_msg = retry_request(APIS['text'], json_data=data)
        
        if response is None:
            return jsonify({'error': error_msg}), status_code
        
        print(f"📥 Response status: {response.status_code}")
        print(f"📄 Response text: {response.text[:200]}")
        
        if not response.text:
            return jsonify({'error': 'API returned empty response. The service may be starting up.'}), 503
        
        try:
            result = response.json()
            return jsonify(result), response.status_code
        except json.JSONDecodeError:
            return jsonify({
                'error': 'Invalid JSON response from API',
                'raw_response': response.text[:500]
            }), 502
            
    except Exception as e:
        print(f"❌ Error: {str(e)}")
        return jsonify({'error': str(e)}), 500

@app.route('/proxy/predict/fibro', methods=['POST'])
def proxy_fibro():
    """Proxy pour l'API fibroscopie"""
    try:
        files = {'image': request.files['image']} if 'image' in request.files else {'file': request.files['file']}
        print(f"📤 Sending to fibro API: {APIS['fibro']}")
        
        response, status_code, error_msg = retry_request(APIS['fibro'], files=files)
        
        if response is None:
            return jsonify({'error': error_msg}), status_code
        
        print(f"📥 Response status: {response.status_code}")
        print(f"📄 Response text: {response.text[:200]}")
        
        if not response.text:
            return jsonify({'error': 'API returned empty response. The service may be starting up.'}), 503
        
        try:
            result = response.json()
            return jsonify(result), response.status_code
        except json.JSONDecodeError:
            return jsonify({
                'error': 'Invalid JSON response from API',
                'raw_response': response.text[:500]
            }), 502
            
    except Exception as e:
        print(f"❌ Error: {str(e)}")
        return jsonify({'error': str(e)}), 500

@app.route('/proxy/predict/irm', methods=['POST'])
def proxy_irm():
    """Proxy pour l'API IRM"""
    try:
        files = {'image': request.files['image']} if 'image' in request.files else {'file': request.files['file']}
        print(f"📤 Sending to IRM API: {APIS['irm']}")
        
        response, status_code, error_msg = retry_request(APIS['irm'], files=files)
        
        if response is None:
            return jsonify({'error': error_msg}), status_code
        
        print(f"📥 Response status: {response.status_code}")
        print(f"📄 Response text: {response.text[:200]}")
        
        if not response.text:
            return jsonify({'error': 'API returned empty response. The service may be starting up.'}), 503
        
        try:
            result = response.json()
            return jsonify(result), response.status_code
        except json.JSONDecodeError:
            return jsonify({
                'error': 'Invalid JSON response from API',
                'raw_response': response.text[:500]
            }), 502
            
    except Exception as e:
        print(f"❌ Error: {str(e)}")
        return jsonify({'error': str(e)}), 500

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port, debug=True)
