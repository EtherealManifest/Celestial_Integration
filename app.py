from flask import Flask, render_template, request, redirect, flash, url_for
import requests, json, base64
from astropy.time import Time
import Planet_Position_Graph as Plot
from io import BytesIO
import matplotlib.pyplot as plt
import numpy as np
from datetime import datetime


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

@app.route('/focus', methods=['POST','GET'])
def set_selection():
    query = request.args.get('name', 'none')
    data = {'target': query}
    response = requests.post('http://localhost:8090/api/main/focus', data=data)
    if response.status_code == 200:
        flash(f'Stellarium is now focusing {query}', 'success')
        return render_template('sky_search.html', name = query)

    else:
        # Handle unsuccessful responses
        flash('Error Unfocusing', 'error')
        return redirect(url_for('set'))

'''allows the user to set the time by providing a time and date. stellarium uses algorithms to generate the positions of
 planets and other celestial objects, so the dates can be far in the past or future.'''
@app.route('/set_time_action', methods=['POST'])
def set_time_action():
    #get the current date-time
    current_datetime = datetime.now()
    #if the user supplies the date and time, great! if not, use the recently acquired data
    date = request.form.get('date') or current_datetime.strftime('%Y-%m-%d')
    time = request.form.get('time') or current_datetime.strftime('%H:%M')
    #default to a 1:1 time rate
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
    #interesting interaction where if the user does not enter anything, the system actually
    #searches the string none. and actually returns a result!
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


'''look at all of stellarium's properties.'''
@app.route('/view_stel_properties', methods=['GET'])
def get_stel_properties():
    response = requests.get('http://localhost:8090/api/stelproperty/list')
    if response.status_code == 200:
        response_data = response.json()
        return render_template('stel_properties.html', response_data=response_data)


'''modify stellariums properties'''
@app.route("/set_stel_property", methods=["POST"])
def set_Property():
    property = request.form.get('property_name', 'none')
    value = request.form.get('property_value', 'none')
    # make sure that Stel knows that they are booleans, not strings
    print(f'Property: {property}, Value: {value}')
    data = {'property': property, 'value': value}
    json_data = json.dumps(data)
    response = requests.post("http://localhost:8090/api/stelproperty/set", data=json_data)
    if response.status_code == 200:
        # notify of success (always happens because I'm awesome :) )
        flash(f'{property} has been set to {value}', 'success')
    else:
        flash(f'Error: {property} was not set successfully', 'error')

    # fetch the current properties, to show them
    response = requests.get('http://localhost:8090/api/stelproperty/list')
    if response.status_code == 200:
        response_data = response.json()

    return render_template('stel_properties.html', response_data=response_data)

@app.route('/focus_properties', methods = ['POST', 'GET'])
def get_focused_info():
    query = request.args.get('target', '')
    status_response = requests.get('http://localhost:8090/api/main/status?actionId=-2&propId=-2')
    focused_data = status_response.json() if status_response.status_code == 200 else None
    print(focused_data['selectioninfo'])
    return render_template('focused_properties.html', response_data=focused_data['selectioninfo'])

@app.route('/info', methods=['POST', 'GET'])
def get_info():
    query = request.args.get('name', 'none')
    response = requests.get('http://localhost:8090/api/objects/info', params={'name': query, 'format': 'json'})
    if response.status_code == 200:
        response_data = response.json()
        #add the sky map here.
        #Attributes Needed: azi, alt, lat, lon, utc_time
        #get azi, alt from response
        alt = response_data['altitude']
        azi = response_data['azimuth']
        #get lat, lon, and utc_time from get_stel_state( just the get request)
        stel_status_response = requests.get('http://localhost:8090/api/main/status?actionId=-2&propId=-2')
        stel_status_data = stel_status_response.json() if stel_status_response.status_code == 200 else None
        utc = stel_status_data['time']['utc']
        # Remove milliseconds and 'Z' for UTC
        cleaned_string = utc.split('.')[0]
        # Convert it to a datetime object
        utc = datetime.fromisoformat(cleaned_string)
        lon = stel_status_data['location']['longitude']
        lat = stel_status_data['location']['latitude']
        #make a call to the adjacent file to actually form the plot, then grab it and show it.
        fig = Plot.plot_planet(azi, alt, lon, lat, utc, query)
        img = BytesIO()
        fig.savefig(img, format='png', bbox_inches='tight')
        img.seek(0)
        plot_url = base64.b64encode(img.getvalue()).decode('utf-8')
        # Render a template with response data
        #this includes the plot, which is basically a PNG with more steps.
        return render_template('search_index.html', name=query, response_data=response_data,
                               plot_url=plot_url)
    else:
        flash(f'Error: Returned {response}', 'error')
    # GET request or POST request with errors
    return render_template('sky_search.html')


if __name__ == '__main__':
    app.run(debug=True)

def local_sidereal_time(longitude, utc_time):
    """Calculate the Local Sidereal Time for a given longitude and UTC time."""
    # Convert UTC time to Julian Date
    jd = utc_time.toordinal() + 1721424.5 + utc_time.hour / 24.0 + utc_time.minute / 1440.0 + utc_time.second / 86400.0

    # Calculate the number of days since J2000.0
    jd2000 = jd - 2451545.0

    # Mean sidereal time in degrees
    mean_sidereal_time = 280.46061837 + 360.98564736629 * jd2000 + longitude

    # Normalize to 0-360 degrees
    mean_sidereal_time = mean_sidereal_time % 360

    # Convert to hours
    lst = mean_sidereal_time / 15.0

    return lst

def plot_planet(ra, dec, lat, lon, utc_time):
    """Plot the position of a planet on a sphere using right ascension and declination,
    with markers indicating both celestial and geographic North."""
    fig = plt.figure()
    ax = fig.add_subplot(111, projection='3d')

    # Sphere
    u, v = np.mgrid[0:2*np.pi:20j, 0:np.pi:10j]
    x = np.cos(u) * np.sin(v)
    y = np.sin(u) * np.sin(v)
    z = np.cos(v)
    ax.plot_wireframe(x, y, z, color="b", alpha=0.1)

    # Planet position
    x_p, y_p, z_p = sph2cart(ra, dec)
    ax.scatter(x_p, y_p, z_p, color="r", s=100)  # s is the size of the point

    # Celestial North (declination = 90 degrees)
    x_n, y_n, z_n = sph2cart(0, 90)
    ax.scatter(x_n, y_n, z_n, color="g", s=100, marker='^')  # Green triangle marker for celestial North

    # Geographic North
    lst = local_sidereal_time(lon, utc_time)
    geo_north_dec = 90 - lat  # Declination for geographic North
    x_gn, y_gn, z_gn = sph2cart(lst * 15, geo_north_dec)  # Convert LST from hours to degrees
    ax.scatter(x_gn, y_gn, z_gn, color="k", s=100, marker='$N$')  # Magenta 'N' marker for geographic North

    # Labels and title
    ax.set_xlabel('X')
    ax.set_ylabel('Y')
    ax.set_zlabel('Z')
    ax.set_title('Planet Position with North Markers')
    #May also need to return ax, standby
    return fig

def sph2cart(ra, dec):
    """Convert spherical coordinates (right ascension and declination) to Cartesian."""
    # Convert angles to radians
    ra_rad = np.deg2rad(ra)
    dec_rad = np.deg2rad(dec)

    # Spherical to Cartesian conversion
    x = np.cos(dec_rad) * np.cos(ra_rad)
    y = np.cos(dec_rad) * np.sin(ra_rad)
    z = np.sin(dec_rad)


