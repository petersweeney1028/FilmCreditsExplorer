import os
from flask import Flask, render_template, request, jsonify
import requests

app = Flask(__name__)

# TMDB API configuration
TMDB_API_KEY = os.environ.get('TMDB_API_KEY', 'your_tmdb_api_key_here')
TMDB_BASE_URL = 'https://api.themoviedb.org/3'

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/search', methods=['POST'])
def search():
    person_name = request.json.get('name')
    if not person_name:
        return jsonify({'error': 'No name provided'}), 400

    # Search for the person
    search_url = f"{TMDB_BASE_URL}/search/person"
    params = {
        'api_key': TMDB_API_KEY,
        'query': person_name
    }
    response = requests.get(search_url, params=params)
    if response.status_code != 200:
        return jsonify({'error': 'Failed to fetch data from TMDB API'}), 500

    data = response.json()
    if not data['results']:
        return jsonify({'error': 'Person not found'}), 404

    person_id = data['results'][0]['id']

    # Fetch person's credits
    credits_url = f"{TMDB_BASE_URL}/person/{person_id}/combined_credits"
    params = {'api_key': TMDB_API_KEY}
    response = requests.get(credits_url, params=params)
    if response.status_code != 200:
        return jsonify({'error': 'Failed to fetch credits data from TMDB API'}), 500

    credits_data = response.json()

    # Process and format the credits data
    formatted_credits = []
    for credit in credits_data.get('cast', []) + credits_data.get('crew', []):
        formatted_credit = {
            'title': credit.get('title') or credit.get('name'),
            'type': 'TV Show' if credit.get('media_type') == 'tv' else 'Movie',
            'role': credit.get('character') if 'character' in credit else credit.get('job'),
            'description': credit.get('overview'),
            'trailer': None,
            'streaming_platforms': None
        }
        
        # Fetch additional details for the movie/TV show
        details_url = f"{TMDB_BASE_URL}/{credit['media_type']}/{credit['id']}"
        details_params = {
            'api_key': TMDB_API_KEY,
            'append_to_response': 'videos,watch/providers'
        }
        details_response = requests.get(details_url, params=details_params)
        if details_response.status_code == 200:
            details_data = details_response.json()
            
            # Get trailer
            videos = details_data.get('videos', {}).get('results', [])
            trailer = next((v for v in videos if v['type'] == 'Trailer' and v['site'] == 'YouTube'), None)
            if trailer:
                formatted_credit['trailer'] = f"https://www.youtube.com/watch?v={trailer['key']}"
            
            # Get streaming platforms
            providers = details_data.get('watch/providers', {}).get('results', {}).get('US', {})
            if providers:
                formatted_credit['streaming_platforms'] = [p['provider_name'] for p in providers.get('flatrate', [])]

        formatted_credits.append(formatted_credit)

    return jsonify(formatted_credits)

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)
