# Celestial Integration 
### SETUP
Celestial Integration is a web App that is connected to the free, open-source planetarium software
Stellarium. With it, the user can easily lookup and reference information about planets, galaxies,
and other celestial bodies in real time, or at any time period +-3000 Years, to the day. 
In order to use this software, you also need to download Stellarium, the download for which can be found 
here: https://stellarium.org/. Complete the installation, then open Stellarium. 

Once stellarium is opened, press [F2] or hover you mouse to the left side of the screen and open the 
*Configuration* menu. in this menu, there is a tab on the top-left labelled *plugins*. Select it
Scroll nearly to the bottom of this list, where there is a tab labelled *remote control.*
selecting this menu will open up the configuration menu for the remote control interface to 
stellarium. From here, there is another configure button, this time in the bottom right. Select it.
In this menu, there are two options that need to be selected. there is a checkbox in the top right
with the label 'Enable automatically at startup'. This makes sure that the information that is 
generated by stellarium is available to Celestial Integration when Stellarium is running. 
The other setting that needs confirmed is that the *port number* is listed as 8090. this is critical
to the performance of Celestial Integration. 

After downloading the .zip from the github, unzip the file to your local device. navigate to the 
folder holding the project, and right click the folder. from the menu, select *copy as path* to obtain 
absolute path to the project folder. With this path copied, open the command line: this can be done either
by searching 'cmd' from the windows program search. 
Once the command line is open, enter the command
> cd *path*

Where *path* is the copied path to the 
project directory. The *cd* indicates that you wish to change the current directory, and the path 
you supply tells the system the directory you wish to move to. After this navigation, you should see
the path you supplied, followed by >.

Now that you are in the right place, enter the command 
> python app.py

This calls on python to open the 
application in this folder called *app.py*. you should then see a few lines of text pop up: 
```
WARNING: This is a development server. Do not use it in a production deployment. Use a production WSGI server instead.
 * Running on http://127.0.0.1:5000
 * ...
 * [other lines of text]
 * ...
 ```
Click the http link to open your preferred web browser. Make sure stellarium is running in the background
with the remote control plugin set according to the process outlined above. At this point your app is ready to run, and you can begin searching for planets and discovering the 
status of the app. You can do many things with this app.
### USING THE APP
The *get state* page allows you to get a full, comprehensive list of all of the attributes of the 
app, at the time of the search. There is not much difference between the *get state* and *update status*,
but *update status* only returns information that has been changed since the last search. 

The *set state* page allows you to set some conditions of the app, including the time and the time rate. 
Explore these options. There are many interesting things that you can do here. The time is defaulted to 
the current time, and the time rate is currently set to sixy seconds per minute (real time). The time can also accept 
negative values to move time backwards. 

By far the most helpful page is the *SkySearch* page. here, you can enter the name of any celestial body,
and assuming correct spelling, it will return a list of results. Selecting any of these will show you
everything that stellarium knows about the planet, as it exists at the currently set time. It will also 
show where to look at the set time to see the celestial object. if you want to focus this object, select 
that option. When an object is Selected, going to the *get_state* page will return information about that
object as well, and the update state button return updates about the focused object. 

Happy Searching!