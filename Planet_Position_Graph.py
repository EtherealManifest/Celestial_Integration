import matplotlib.pyplot as plt
import numpy as np
from mpl_toolkits.mplot3d import Axes3D

from datetime import datetime
import pytz

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
    ax.scatter(x_gn, y_gn, z_gn, color="m", s=100, marker='s')  # Magenta square marker for geographic North

    # Labels and title
    ax.set_xlabel('X')
    ax.set_ylabel('Y')
    ax.set_zlabel('Z')
    ax.set_title('Planet Position with North Markers')

    plt.show()

def sph2cart(ra, dec):
    """Convert spherical coordinates (right ascension and declination) to Cartesian."""
    # Convert angles to radians
    ra_rad = np.deg2rad(ra)
    dec_rad = np.deg2rad(dec)

    # Spherical to Cartesian conversion
    x = np.cos(dec_rad) * np.cos(ra_rad)
    y = np.cos(dec_rad) * np.sin(ra_rad)
    z = np.sin(dec_rad)

    return x, y, z

# Example values for RA, Dec, latitude, longitude, and UTC time
ra_example = 45
dec_example = 30
lat_example = 51.5  # Latitude for London, UK
lon_example = -0.12  # Longitude for London, UK
utc_time_example = datetime(2023, 11, 23, 12, 0, 0, tzinfo=pytz.utc)
# Plotting the planet with both celestial and geographic North
plot_planet(ra_example, dec_example, lat_example, lon_example, utc_time_example)

