from flask import Flask, render_template, request
import requests

app = Flask(__name__)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/set_state')
def set():
    return render_template('set_state.html')

@app.route('/sky_search')
def search():
    return render_template('sky_search.html')
@app.route('/get_state')
def update():
    return render_template('get_state.html')
@app.route('/get_stellarium_state', methods=['POST'])
def get_stellarium_state():
    try:
        # Call to /api/main/status
        # Initial call with parameters -2 for StelAction and StelProperty
        status_response = requests.get('http://localhost:8090/api/main/status?actionId=-2&propId=-2')
        status_data = status_response.json() if status_response.status_code == 200 else None

        # Call to /api/main/view
        view_response = requests.get('http://localhost:8090/api/main/view')
        view_data = view_response.json() if view_response.status_code == 200 else None

        # Combine the responses
        combined_data = {
            'status': status_data,
            'view': view_data
        }
        return combined_data

    except requests.exceptions.RequestException as e:
        return {'error': str(e)}



@app.route('/update_stellarium_state', methods=['POST'])
def update_stellarium_state():
    action_id = request.args.get('actionId')
    prop_id = request.args.get('propId')

    try:
        # Call to /api/main/status
        # Initial call with parameters -2 for StelAction and StelProperty
        status_response = requests.get(f'http://localhost:8090/api/main/status?actionId={action_id}&propId={prop_id}')
        status_data = status_response.json() if status_response.status_code == 200 else None

        # Call to /api/main/view
        view_response = requests.get('http://localhost:8090/api/main/view')
        view_data = view_response.json() if view_response.status_code == 200 else None

        # Combine the responses
        combined_data = {
            'status': status_data,
            'view': view_data
        }
        return combined_data

    except requests.exceptions.RequestException as e:
        return {'error': str(e)}

if __name__ == '__main__':
    app.run(debug=True)
