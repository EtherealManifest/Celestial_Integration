from flask import Flask, render_template, request, redirect, flash, url_for
import requests, json
from datetime import datetime
from astropy.time import Time

app = Flask(__name__)
app.secret_key = 'Gaze_of_the_Skyborne_Warrior'

'''the route for the index page'''
@app.route('/')
def index():
    return render_template('index.html')

'''the route for the set State page'''
@app.route('/set_state')
def set():
    return render_template('set_state.html')

'''the route for the page that shows stellariums roperties, and writes to them'''
@app.route('/stel_properties')
def viewProps():
    return render_template('stel_properties.html')

'''The route to the page that allows the user to search the Stellarium database for a celestial object'''
@app.route('/sky_search')
def search():
    return render_template('sky_search.html')

'''the route for the page that shows stellarium's current state'''
@app.route('/get_state')
def update():
    return render_template('get_state.html')

'''this route renders the above page with data fields filled in, getting stellariums current state and displaying it'''
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

'''similar to the above method/route, but this acounts for the updating of information, providing the user with a Delta 
Time and changes in FOV'''
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

'''the User can set the field of view in stellarium, though this does not do anything practical for the web user'''
@app.route('/set_FOV', methods=['POST'])
def set_fov():
    new_fov = request.form.get('FOV') or 65
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
            flash(f'FOV set to {new_fov}\N{DEGREE SIGN}', 'success')
            return redirect(url_for('set'))
        # Assume you have a variable `time` that holds the set time value

    else:
        # Handle unsuccessful responses
        flash(('Error setting FOV, ' + str(response)), 'error')

        return redirect(url_for('set'))

    # Return an appropriate response
    return response

'''Un-focuses the current selection. if a selection is un-focused, no information about it will be displayed'''
@app.route('/unfocus', methods=['POST'])
def clear_selection():
    response = requests.post('http://localhost:8090/api/main/focus')
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
            flash(f'Current Focus Cleared', 'success')
            return redirect(url_for('set'))
        # Assume you have a variable `time` that holds the set time value

    else:
        # Handle unsuccessful responses
        flash('Error Unfocusing (Im Autistic)', 'error')
        return redirect(url_for('set'))

    # Return an appropriate response
    return response

'''allows the user to set the time by providing a time and date. stellarium uses algorithms to generate the positions of
 planets and other celestial objects, so the dates can be far in the past or future.'''
@app.route('/set_time_action', methods=['POST'])
def set_time_action():
    current_datetime = datetime.now()
    date = request.form.get('date') or current_datetime.strftime('%Y-%m-%d')
    time = request.form.get('time') or current_datetime.strftime('%H:%M')
    timeRate = request.form.get('timeRate') or 1
    # Combine date and time strings
    datetime_str = f"{date} {time}"
    # Convert to datetime object
    datetime_obj = datetime.strptime(datetime_str, '%Y-%m-%d %H:%M')

    # now that the imput time is in the correct format, put it in JD form.
    data = {}
    data['time'] = Time(datetime_obj).jd
    data['timerate'] = int(timeRate) / 86400
    response = requests.post('http://localhost:8090/api/main/time', data=data)
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
            flash(f'Time set to {datetime_str}, Speed set to {timeRate}x', 'success')
            return redirect(url_for('set'))
        # Assume you have a variable `time` that holds the set time value

    else:
        # Handle unsuccessful responses
        flash('Error setting time', 'error')
        return redirect(url_for('set'))

    # Return an appropriate response
    return response

'''lookup and object by name, and return a list of potential matches. these mathches are rendered as a list of links
 that the user can select to show that object's current state'''
@app.route('/lookup', methods=['POST'])
def search_the_skies():
    query = request.form.get('object_to_search') or 'none'
    response = requests.get('http://localhost:8090/api/objects/find', params={'str': query})
    if response.status_code == 200:
        response_data = response.json()
        # Render a template with response data
        return render_template('results_page.html', response_data=response_data)
    else:
        flash(f'Error: Returned {response}', 'error')

    # GET request or POST request with errors
    return render_template('sky_search.html')

'''look at and modify some of stellarium's properties.'''
@app.route('/view_stel_properties', methods=['GET'])
def get_stel_properties():
    response = requests.get('http://localhost:8090/api/stelproperty/list')
    if response.status_code == 200:
        response_data = response.json()
        return render_template('stel_properties.html', response_data=response_data)

@app.route("/set_stel_property", methods = ["POST"])
def set_Property():
    property = request.form.get('property_name', 'none')
    value = request.form.get('property_value', 'none')
    #make sure that Stel knows that they are booleans, not strings
    print(f'Property: {property}, Value: {value}')
    data = {'property': property, 'value': value}
    json_data = json.dumps(data)
    response = requests.post("http://localhost:8090/api/stelproperty/set", data=json_data)
    if response.status_code == 200:
        #notify of success (always happens because I'm awesome :) )
        flash(f'{property} has been set to {value}', 'success')
    else:
        flash(f'Error: {property} was not set successfully', 'error')

    #fetch the current properties, to show them
    response = requests.get('http://localhost:8090/api/stelproperty/list')
    if response.status_code == 200:
        response_data = response.json()

    return render_template('stel_properties.html', response_data=response_data)

@app.route('/info', methods=['POST', 'GET'])
def get_info():
    query = request.args.get('name', 'none')
    response = requests.get('http://localhost:8090/api/objects/info', params={'name': query, 'format': 'json'})
    if response.status_code == 200:
        response_data = response.json()
        # Render a template with response data
        return render_template('search_index.html', name=query, response_data=response_data)
    else:
        flash(f'Error: Returned {response}', 'error')

    # GET request or POST request with errors
    return render_template('sky_search.html')


if __name__ == '__main__':
    app.run(debug=True)
