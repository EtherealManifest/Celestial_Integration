from flask import Flask, render_template, request, redirect, flash, url_for
import requests
from datetime import datetime
from astropy.time import Time

app = Flask(__name__)
app.secret_key = 'Gaze_of_the_Skyborne_Warrior'

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



@app.route('/set_FOV', methods=['POST'])
def set_fov():
    new_fov = request.form.get('FOV')
    data = {}
    data['fov'] = new_fov
    response = requests.post('http://localhost:8090/api/main/fov', data=data)
    # Parse the success code
    if response.status_code == 200:
        if response.headers.get('Content-Type') == 'application/json':
            try:
                response_data = response.json()
                # Process JSON data
            except ValueError:
                # JSON parsing failed, handle the exception
                return {'status': 'error', 'message': 'Invalid JSON response'}
        else:
            # Response is not JSON, but the request was successful
            flash(f'FOV set to {new_fov}', 'success')
            return redirect(url_for('set'))
        # Assume you have a variable `time` that holds the set time value

    else:
        # Handle unsuccessful responses
        flash(('Error setting FOV, ' + str(response)), 'error')

        return redirect(url_for('set'))

    # Return an appropriate response
    return response

@app.route('/set_time_action', methods=['POST'])
def set_time_action():
    date = request.form.get('date')
    time = request.form.get('time')
    timeRate = request.form.get('timeRate')

    # Combine date and time strings
    datetime_str = f"{date} {time}"
    # Convert to datetime object
    datetime_obj = datetime.strptime(datetime_str, '%Y-%m-%d %H:%M')

    #now that the imput time is in the correct format, put it in JD form.
    data = {}
    if time and date:
        data['time'] = Time(datetime_obj).jd
    if timeRate:
        data['timerate'] = timeRate
    if time or timeRate:
        response = requests.post('http://localhost:8090/api/main/time', data=data)
    else:
        response = "Error, response not recognized by me, the interpreter. keep trying"

    #Parse the success code
    if response.status_code == 200:
        if response.headers.get('Content-Type') == 'application/json':
            try:
                response_data = response.json()
                # Process JSON data
            except ValueError:
                # JSON parsing failed, handle the exception
                return {'status': 'error', 'message': 'Invalid JSON response'}
        else:
            # Response is not JSON, but the request was successful
            flash(f'Time set to {datetime_str}', 'success')
            return redirect(url_for('set'))
        # Assume you have a variable `time` that holds the set time value

    else:
        # Handle unsuccessful responses
        flash('Error setting time', 'error')
        return redirect(url_for('set'))

    # Return an appropriate response
    return response

@app.route('/set_state_action', methods=['POST'])
def set_state_action():
    time = request.form.get('time')
    time_rate = request.form.get('timeRate')
    focused_object = request.form.get('focusedObject')
    view_direction = request.form.get('viewDirection')
    field_of_view = request.form.get('fieldOfView')

    # Logic to handle each field.
    # If a field is blank (None or ''), keep the original data
    data = {}
    if time:
        data['time'] = time
    if time_rate:
        data['timerate'] = time_rate
        #once this data is constructed, pass the payload to set the time.
    if(time or time_rate):
        response = requests.post('http://localhost:8090/api/main/time', data=data)

    data = {}
    if focused_object:
        data['target'] = focused_object
        response = requests.post('http://localhost:8090/api/main/focus', data=data)

    # Example:
    # if time:
    #     # Code to set time
    return

if __name__ == '__main__':
    app.run(debug=True)
