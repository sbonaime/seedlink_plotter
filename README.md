## Seedlink-Plotter

A python script to plot real time seismic data from a seedlink server

This version work with the latest stable ObsPy version (0.9.0).

On some linux box, the time zone must be set to UTC and not GMT

### Installation

    pip install https://github.com/bonaime/seedlink_plotter/archive/master.zip

### Usage examples

Drum plots (with longer time range):

    seedlink-plotter -s "G_FDF:00BHZ" --x_position 200 --y_position 50 --x_size 800 --y_size 600 -b 86400 --scale 20000 --seedlink_server "rtserver.ipgp.fr:18000" --x_scale 60

![Singlechannel](/img/Singlechannel.png)


Line plot with single station (with shorter time range):

    seedlink-plotter -s "G_IVI:00BHZ" -b 600 --seedlink_server "rtserver.ipgp.fr:18000"  --plot_line

![Plot_line](/img/plot_line.png)

Line plots with multiple stations (with shorter time range):

    seedlink-plotter -s "G_FDF:00BHZ,G_SSB:00BHZ" --x_position 200 --y_position 50 --x_size 800 --y_size 600 -b 1800 --seedlink_server "rtserver.ipgp.fr:18000" --update_time 2
    seedlink-plotter -s "G_FDF:00BHZ 00BHN 00BHE" --x_position 200 --y_position 50 --x_size 800 --y_size 600 -b 1800 --seedlink_server "rtserver.ipgp.fr:18000" --update_time 2

![Multichannel](/img/Multichannel.png)

### Keyboard Controls

Keyboard controls only work without option `--without-decoration`!

 - `f`: toggle fullscreen
 - `<Escape>`: close window

### Dependencies
 - Python 2.7
 - ObsPy (>= https://github.com/obspy/obspy/tree/05597e4642)
 - matplolib (>= 1.3.0)
 - scipy
 - numpy
