from flask import Flask, request, jsonify, send_from_directory
from flask_cors import CORS
import requests
import os
import json

app = Flask(__name__, static_folder='.')
CORS(app)  # Active CORS pour ce proxy

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

@app.route('/proxy/predict/text', methods=['POST'])
def proxy_text():
    """Proxy pour l'API texte"""
    try:
        data = request.get_json()
        print(f"📤 Sending to text API: {APIS['text']}")
        print(f"📦 Data: {data}")
        
        response = requests.post(
            APIS['text'], 
            json=data, 
            timeout=300,  # 5 minutes pour le cold start
            headers={'Content-Type': 'application/json'}
        )
        
        print(f"📥 Response status: {response.status_code}")
        print(f"📄 Response text: {response.text[:200]}")  # Premiers 200 caractères
        
        # Vérifier si la réponse est vide
        if not response.text:
            return jsonify({'error': 'API returned empty response. The service may be starting up.'}), 503
        
        # Essayer de parser le JSON
        try:
            result = response.json()
            return jsonify(result), response.status_code
        except json.JSONDecodeError:
            return jsonify({
                'error': 'Invalid JSON response from API',
                'raw_response': response.text[:500]
            }), 502
            
    except requests.exceptions.Timeout:
        return jsonify({
            'error': 'API timeout. The service may be waking up. Please try again in 30 seconds.'
        }), 504
    except requests.exceptions.RequestException as e:
        return jsonify({'error': f'Request failed: {str(e)}'}), 500
    except Exception as e:
        print(f"❌ Error: {str(e)}")
        return jsonify({'error': str(e)}), 500

@app.route('/proxy/predict/fibro', methods=['POST'])
def proxy_fibro():
    """Proxy pour l'API fibroscopie"""
    try:
        files = {'image': request.files['image']} if 'image' in request.files else {'file': request.files['file']}
        print(f"📤 Sending to fibro API: {APIS['fibro']}")
        
        response = requests.post(
            APIS['fibro'], 
            files=files, 
            timeout=300
        )
        
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
            
    except requests.exceptions.Timeout:
        return jsonify({
            'error': 'API timeout. The service may be waking up. Please try again in 30 seconds.'
        }), 504
    except requests.exceptions.RequestException as e:
        return jsonify({'error': f'Request failed: {str(e)}'}), 500
    except Exception as e:
        print(f"❌ Error: {str(e)}")
        return jsonify({'error': str(e)}), 500

@app.route('/proxy/predict/irm', methods=['POST'])
def proxy_irm():
    """Proxy pour l'API IRM"""
    try:
        files = {'image': request.files['image']} if 'image' in request.files else {'file': request.files['file']}
        print(f"📤 Sending to IRM API: {APIS['irm']}")
        
        response = requests.post(
            APIS['irm'], 
            files=files, 
            timeout=300
        )
        
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
            
    except requests.exceptions.Timeout:
        return jsonify({
            'error': 'API timeout. The service may be waking up. Please try again in 30 seconds.'
        }), 504
    except requests.exceptions.RequestException as e:
        return jsonify({'error': f'Request failed: {str(e)}'}), 500
    except Exception as e:
        print(f"❌ Error: {str(e)}")
        return jsonify({'error': str(e)}), 500

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port, debug=True)
