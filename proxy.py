from flask import Flask, request, jsonify, send_from_directory
from flask_cors import CORS
import requests
import os
import json

app = Flask(__name__, static_folder='.')
CORS(app)

# URLs de vos APIs Render
APIS = {
    'text': 'https://gastrocsv-flask-api.onrender.com/predict',
    'fibro': 'https://gastrofibro-api-1.onrender.com/predict',
    'irm': 'https://gastroirm-flask-api-4.onrender.com/predict'
}

@app.route('/')
def index():
    """Sert votre fichier HTML"""
    return send_from_directory('.', 'index.html')

@app.route('/proxy/predict/text', methods=['POST', 'OPTIONS'])
def proxy_text():
    """Proxy pour l'API texte"""
    if request.method == 'OPTIONS':
        return '', 204
    
    try:
        data = request.get_json()
        
        if not data:
            return jsonify({'error': 'Aucune donnée reçue'}), 400
        
        print(f"Envoi vers API text: {data}")  # Debug
        
        # Appel à l'API avec timeout étendu pour réveiller Render
        response = requests.post(
            APIS['text'], 
            json=data, 
            timeout=300,  # 5 minutes pour le réveil
            headers={'Content-Type': 'application/json'}
        )
        
        print(f"Status code: {response.status_code}")  # Debug
        print(f"Response text: {response.text[:200]}")  # Debug (premiers 200 chars)
        
        # Vérifier si la réponse est vide
        if not response.text or response.text.strip() == '':
            return jsonify({'error': 'Réponse vide de l\'API', 'details': 'L\'API est peut-être en train de se réveiller'}), 503
        
        # Essayer de parser le JSON
        try:
            result = response.json()
            return jsonify(result), response.status_code
        except json.JSONDecodeError as je:
            return jsonify({
                'error': 'Réponse invalide de l\'API',
                'details': response.text[:500],
                'status_code': response.status_code
            }), 500
            
    except requests.exceptions.Timeout:
        return jsonify({'error': 'L\'API met trop de temps à répondre (timeout)', 'details': 'L\'API Render est peut-être en veille'}), 504
    except requests.exceptions.ConnectionError:
        return jsonify({'error': 'Impossible de se connecter à l\'API', 'details': 'Vérifiez que l\'API est déployée'}), 503
    except Exception as e:
        return jsonify({'error': f'Erreur: {str(e)}', 'type': type(e).__name__}), 500

@app.route('/proxy/predict/fibro', methods=['POST', 'OPTIONS'])
def proxy_fibro():
    """Proxy pour l'API fibroscopie"""
    if request.method == 'OPTIONS':
        return '', 204
    
    try:
        if 'image' not in request.files and 'file' not in request.files:
            return jsonify({'error': 'Aucun fichier image fourni'}), 400
        
        files = {'image': request.files.get('image') or request.files.get('file')}
        
        print(f"Envoi image vers API fibro")  # Debug
        
        response = requests.post(
            APIS['fibro'], 
            files=files, 
            timeout=300
        )
        
        print(f"Status code fibro: {response.status_code}")  # Debug
        
        if not response.text or response.text.strip() == '':
            return jsonify({'error': 'Réponse vide de l\'API fibroscopie'}), 503
        
        try:
            result = response.json()
            return jsonify(result), response.status_code
        except json.JSONDecodeError:
            return jsonify({
                'error': 'Réponse invalide de l\'API fibroscopie',
                'details': response.text[:500]
            }), 500
            
    except requests.exceptions.Timeout:
        return jsonify({'error': 'Timeout API fibroscopie'}), 504
    except Exception as e:
        return jsonify({'error': str(e), 'type': type(e).__name__}), 500

@app.route('/proxy/predict/irm', methods=['POST', 'OPTIONS'])
def proxy_irm():
    """Proxy pour l'API IRM"""
    if request.method == 'OPTIONS':
        return '', 204
    
    try:
        if 'image' not in request.files and 'file' not in request.files:
            return jsonify({'error': 'Aucun fichier image fourni'}), 400
        
        files = {'image': request.files.get('image') or request.files.get('file')}
        
        print(f"Envoi image vers API IRM")  # Debug
        
        response = requests.post(
            APIS['irm'], 
            files=files, 
            timeout=300
        )
        
        print(f"Status code IRM: {response.status_code}")  # Debug
        
        if not response.text or response.text.strip() == '':
            return jsonify({'error': 'Réponse vide de l\'API IRM'}), 503
        
        try:
            result = response.json()
            return jsonify(result), response.status_code
        except json.JSONDecodeError:
            return jsonify({
                'error': 'Réponse invalide de l\'API IRM',
                'details': response.text[:500]
            }), 500
            
    except requests.exceptions.Timeout:
        return jsonify({'error': 'Timeout API IRM'}), 504
    except Exception as e:
        return jsonify({'error': str(e), 'type': type(e).__name__}), 500

@app.route('/health')
def health():
    """Endpoint de santé"""
    return jsonify({'status': 'ok', 'message': 'Proxy is running'}), 200

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port, debug=True)
