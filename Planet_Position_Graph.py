import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import numpy as np


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


def plot_planet(azi, alt, lat, lon, utc_time, name):
    """Plot the position of a planet on a sphere using right ascension and declination,
    with markers indicating both celestial and geographic North."""
    fig = plt.figure()
    ax = fig.add_subplot(111, projection='3d')

    # Sphere
    u, v = np.mgrid[0:2 * np.pi:20j, 0:np.pi:10j]
    x = np.cos(u) * np.sin(v)
    y = np.sin(u) * np.sin(v)
    z = np.cos(v)
    ax.plot_wireframe(x, y, z, color="b", alpha=0.2)

    # horizon position
    horizon_u = np.linspace(0, 2 * np.pi, 100)
    horizon_v = np.pi / 2  # Horizon at declination 0 (equator)
    horizon_x = np.cos(horizon_u)
    horizon_y = np.sin(horizon_u)
    horizon_z = np.zeros_like(horizon_x)
    ax.plot(horizon_x, horizon_y, horizon_z, color="black", linewidth=2)

    # Planet position
    x_p, y_p, z_p = sph2cart(azi, alt)
    ax.scatter(x_p, y_p, z_p, color="red", s=100, marker="*", label="Planet Position")  # s is the size of the point

    # Celestial North (declination = 90 degrees)
    x_n, y_n, z_n = sph2cart(0, 90)
    ax.scatter(x_n, y_n, z_n, color="g", s=100, marker='$CN$',
               label="Celestial North")  # Green 'CN' for celestial North

    # North
    x_gn, y_gn, z_gn = sph2cart(0, 0)
    ax.scatter(x_gn, y_gn, z_gn, color="m", s=100, marker='$N$')

    # South
    x_gs, y_gs, z_gs = sph2cart(180, 0)
    ax.scatter(x_gs, y_gs, z_gs, color="m", s=100, marker='$S$')

    # East
    x_ge, y_ge, z_ge = sph2cart(90, 0)
    ax.scatter(x_ge, y_ge, z_ge, color="m", s=100, marker='$E$')

    # West
    x_gw, y_gw, z_gw = sph2cart(-90, 0)
    ax.scatter(x_gw, y_gw, z_gw, color="m", s=100, marker='$W$')

    # Viewer's position at the center
    ax.scatter(0, 0, 0, color="c", s=100, marker='$(o)$', label='Viewer')  # Viewer's position with label

    # Remove external axis marks
    ax.set_xticks([])
    ax.set_yticks([])
    ax.set_zticks([])
    ax.set_title(f'{name} -- Relative Position')

    # Create the legend
    ax.legend(loc='lower right')

    # May also need to return ax, standby
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

    return x, y, z
