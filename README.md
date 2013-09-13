## Seedlink-Plotter

A python script to plot real time seismic data from a seedlink server

This version does not work with the latest stable ObsPy version.
If you have ObsPy 0.8.3 or earlier, you need to update to a more recent unstable version (at least 26/03/2013, e.g. https://github.com/obspy/obspy/tree/05597e4642).

On some linux box, the time zone must be set to UTC and not GMT

### Installation

    pip install https://github.com/bonaime/seedlink_plotter/archive/master.zip

### Usage examples

Singlechannel plots (with longer time range):

    seedlink-plotter -s "G_FDF:00BHZ" --x_position 200 --y_position 50 --x_size 800 --y_size 600 -b 24 --scale 20000 --seedlink_server "rtserver.ipgp.fr:18000" --x_scale 60
    seedlink-plotter -s "G_SSB:00BHZ" --x_position 200 --y_position 50 --x_size 800 --y_size 600 -b 24 --scale 20000 --seedlink_server "rtserver.ipgp.fr:18000" --with_decoration --rainbow --x_scale 60 --nb_rainbow_colors 15

Multichannel plots (with shorter time range):

    seedlink-plotter -s "G_FDF:00BHZ,G_SSB:00BHZ" --x_position 200 --y_position 50 --x_size 800 --y_size 600 -b 0.5 --seedlink_server "rtserver.ipgp.fr:18000" --update_time 2

### Keyboard Controls

Keyboard controls only work with option `--with-decoration`!

 - `f`: toggle fullscreen
 - `<Escape>`: close window

### Dependencies
 - Python 2.7
 - ObsPy (>= https://github.com/obspy/obspy/tree/05597e4642)
 - matplolib (>= 1.3.0)
 - scipy
 - numpy
