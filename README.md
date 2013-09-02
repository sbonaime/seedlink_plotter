## Seedlink-Plotter

A python script to plot real time seismic data from a seedlink server

This version does not work with the latest stable ObsPy version.
If you have ObsPy 0.8.3 or earlier, you need to update to a more recent unstable version (at least 26/03/2013, e.g. https://github.com/obspy/obspy/tree/05597e4642).

On some linux box, the time zone must be set to UTC and not GMT

### Installation

    pip install https://github.com/bonaime/seedlink_plotter/archive/master.zip

### Usage examples

    seedlink-plotter -s FDF -n G -c BHZ -l 00 --x_position 200 --y_position 50 --x_size 800 --y_size 600 -b 24 --scale 20000 --seedlink_server "rtserver.ipgp.fr:18000" --x_scale 60 

    seedlink-plotter -s SSB -n G -c BHZ -l 00 --x_position 200 --y_position 50 --x_size 800 --y_size 600 -b 24 --scale 20000 --seedlink_server "rtserver.ipgp.fr:18000" --with_decoration --rainbow --x_scale 60 --nb_rainbow_colors 15

### Keyboard Controls

Keyboard controls only work with option `--with-decoration`!

 - `f`: toggle fullscreen
 - `<Escape>`: close window

### Dependencies
 - Python 2.7
 - ObsPy (>= https://github.com/obspy/obspy/tree/05597e4642)
 - matplolib
 - scipy
 - numpy
