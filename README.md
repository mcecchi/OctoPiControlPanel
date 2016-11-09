## OctoPiControlPanel v0.1 ##

OctoPiControlPanel uses a Raspberry PI touchscreen to control 3D printers using OctoPrint API. <br/>
OctoPiControlPanel requires Pygame to be installed. Pygame can be downloaded from http://pygame.org. <br/>
OctoPiControlPanel is inspired by Colin Edwards OctoPiPanel mods https://github.com/DDRBoxman/OctoPiPanel.git. <br/>
OctoPiPanel is developed by Jonas Lorander (jonas@haksberg.net) https://github.com/jonaslorander/OctoPiPanel.<br/>

## Setup ##

### Requirements ###

* 1
* 2
* 3
* 4
* Python 2.7 (should already be installed)
* PyGame (should already be installed)
* requests Python module

OctoPiControlPanel can be run on Windows as well to ease development.

### Getting and installing OctoPiControlPanel ###
The setup is pretty basic. You'll be needing Python 2.7 which should be installed by default, Git, and pip.
```
cd ~
sudo apt-get install python-pip git
git clone https://github.com/mcecchi/OctoPiControlPanel.git
cd OctoPiControlPanel
sudo pip install -r requirements.txt
```

### Settings ###
* You need to activate the REST API in you OctoPrint settings and get your API-key with Octoprint Versions older then 1.1.1, otherwise you will be fine.
* Put the URL to you OctoPrint installation in the **baseurl**-property in the **OctoPiPanel.cfg** file. For instance `http://localhost:5000` or `http://192.168.0.111:5000`.
* Put your API-key in the **apikey**-property in the **OctoPiPanel.cfg** file.

### Running OctoPiPanel ###
Start OctoPiControlPanel by browsing to the folder of the Python-file and execute <br/>
`sudo python ./OctoPiControlPanel.py &` <br/>
In a screen session (auto start scripts will be coming later). Yes, `sudo` must be used for the time being.

### Automatic start up ###

Make OctoPiControlPanel.py executable and then copy the script files to their respective folders and make the init script executable:
```
chmod +x OctoPiControlPanel.py
sudo cp scripts/octopicontrolpanel.init /etc/init.d/octopicontrolpanel
sudo chmod +x /etc/init.d/octopicontrolpanel
sudo cp scripts/octopicontrolpanel.default /etc/default/octopicontrolpanel
```
Then add the script to autostart using `sudo update-rc.d octopicontrolpanel defaults`.

This will also allow you to start/stop/restart the OctoPiControlPanel daemon via

sudo service octopicontrolpanel {start|stop|restart}

## Attributions ##
PygButton courtesy of Al Sweigart (al@inventwithpython.com)

####Master branch build status: 
![](https://travis-ci.org/mcecchi/OctoPiControlPanel.svg?branch=master)
