#!/usr/bin/env python

import matplotlib
# Set the backend for matplotlib.
matplotlib.use("TkAgg")

from obspy.core import Stream
import Tkinter
from obspy.seedlink.slpacket import SLPacket
from obspy.seedlink.slclient import SLClient
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from matplotlib.figure import Figure
from obspy.core import UTCDateTime
from argparse import ArgumentParser
from math import sin
from progressbar import BouncingBar, FormatLabel, ProgressBar, RotatingMarker


class Seedlink_plotter(SLClient):
    """
    This module plots realtime seismic data from a Seedlink server
    """

    def __init__(self, figure, canvas, interval, backtrace, args):

        # Set the log level to display minimal info
        super(Seedlink_plotter, self).__init__(loglevel='CRITICAL')
        self.figure = figure
        self.stream = Stream()
        self.interval = interval
        self.backtrace = backtrace
        self.canvas = canvas
        self.flip = 0
        self.scale = args.scale
        self.args = args
        self.initial_update_rate = 800
        self.update_rate = 2
        # Plot after geting the penultimate line of data
        self.print_max = (self.backtrace-60.0*self.interval)
        widgets = [FormatLabel('Receiving Data: - '), BouncingBar(
            marker=RotatingMarker())]
        self.pbar = ProgressBar(maxval=self.print_max, widgets=widgets).start()

        # Colors
        if args.rainbow:
            # Rainbow colors !
            self.color = self.rainbow_color_generator(
                int(args.nb_rainbow_colors))
        else:
            # Regular colors
            self.color = ('#000000', '#ff0000', '#0000ff', '#56a83c')

        # converter for the colors gradient
    def rgb_to_hex(self, r, g, b):
        return '#%02X%02X%02X' % (r, g, b)

        # Rainbow color generator
    def rainbow_color_generator(self, max_color):
        color_list = []
        frequency = 0.3
        for compteur_lignes in xrange(max_color):
            red = sin(frequency*compteur_lignes*2 + 0)*127+128
            green = sin(frequency*compteur_lignes*2 + 2)*127+128
            blue = sin(frequency*compteur_lignes*2 + 4)*127+128

            color_list.append(self.rgb_to_hex(red, green, blue))

        return tuple(color_list)

    def plot_graph(self):

        #######################################################################
        # filter section
        #######################################################################
        self.local_stream = self.stream.copy()
        # Filter example
#         self.local_stream.filter('bandpass', freqmin=0.001, freqmax=0.5,corners=2, zerophase=True)
        #######################################################################

        self.local_stream.plot(
            fig=self.figure, type='dayplot', interval=self.interval,
            number_of_ticks=13, tick_format='%d/%m %Hh',
            size=(args.x_size, args.y_size ),
            x_labels_size=8, y_labels_size=8,
            title=self.title, title_size=14,
            linewidth=0.5, right_vertical_labels=False,
            vertical_scaling_range=self.scale,
            subplots_adjust_left=0.03, subplots_adjust_right=0.99,
            subplots_adjust_top=0.95, subplots_adjust_bottom=0.1,
            one_tick_per_line=True,
            # noir  Rouge bleu vert
            color = self.color,
            show_y_UTC_label=False)

    def packetHandler(self, count, slpack):
        """
        Processes each packet received from the SeedLinkConnection.
        :type count: int
        :param count:  Packet counter.
        :type slpack: :class:`~obspy.seedlink.SLPacket`
        :param slpack: packet to process.
        :return: Boolean true if connection to SeedLink server should be
            closed and session terminated, false otherwise.
        """

        # check if not a complete packet
        if slpack is None or (slpack == SLPacket.SLNOPACKET) or \
                (slpack == SLPacket.SLERROR):
            return False

        # get basic packet info
        type = slpack.getType()

        # process INFO packets here
        if (type == SLPacket.TYPE_SLINF):
            return False
        if (type == SLPacket.TYPE_SLINFT):
#             print "Complete INFO:\n" + self.slconn.getInfoString()
            if self.infolevel is not None:
                return True
            else:
                return False

        # process packet data
        trace = slpack.getTrace()
        if trace is None:
            print self.__class__.__name__ + ": blockette contains no trace"
            return False

        # new samples add to the main stream
        self.stream += trace
        self.stream.merge()

        now = UTCDateTime()

        # Stop time will be the next round date
        stop_time = UTCDateTime(
            now.year, now.month, now.day, now.hour, 0, 0)+3600
        start_time = stop_time-self.backtrace

        # Limit the stream size
        self.stream = self.stream.slice(start_time, stop_time)
        self.stream.trim(start_time, stop_time)

        self.title = self.stream.traces[0].stats.station+" "+self.stream.traces[0].stats.network+" "+self.stream.traces[
            0].stats.location+" "+self.stream.traces[0].stats.channel+' scale: '+str(self.scale) + " - non filtre"

        stream_time_length = self.stream.traces[
            0].stats.endtime - self.stream.traces[0].stats.starttime

        # Before we reach  print_max  we plot each initial_update_rate we
        # received
        if stream_time_length <= self.print_max:
            self.flip += 1
            self.pbar.update(stream_time_length)

            if (self.flip > self.initial_update_rate):
                self.flip = 0
                self.figure.clear()
                self.plot_graph()

        # Real time plotting
        # We plot each update_rate packet we received
        if ((stream_time_length)) > (self.print_max):
            self.flip += 1
            if (self.flip > self.update_rate):
                self.figure.clear()
                self.plot_graph()
                self.flip = 0

        return False

if __name__ == '__main__':

    parser = ArgumentParser(prog='seedlink_plotter',
                            description='Plot a realtime seismogram drum of a station')

    parser.add_argument('-s', '--station_name', type=str,
                        help='the name of the station to plot', required=True)
    parser.add_argument('-n', '--network_code', type=str,
                        help='the name of the station to plot', required=True)
    parser.add_argument('-l', '--location_id', type=str,
                        help='the location id of the channel to plot', required=False, default='')
    parser.add_argument('-c', '--channel', type=str,
                        help='the name of the channel to plot', required=True)
    parser.add_argument(
        '--scale', type=int, help='the scale to apply on data ex:50000', required=False, default=1)

    # Real-time parameters
    parser.add_argument('--seedlink_server', type=str,
                        help='the seedlink server to connect to with port. ex: rtserver.ipgp.fr:18000 ', required=True)
    parser.add_argument(
        '--x_scale', type=int, help='the number of minute to plot per line', default=60)
    parser.add_argument('-b', '--backtrace_time', type=int,
                        help='the number of hours to plot', required=True)
    parser.add_argument('--x_position', type=int,
                        help='the x position of the graph', required=False, default=0)
    parser.add_argument('--y_position', type=int,
                        help='the y position of the graph', required=False, default=0)
    parser.add_argument(
        '--x_size', type=int, help='the x size of the graph', required=False, default=800)
    parser.add_argument(
        '--y_size', type=int, help='the y size of the graph', required=False, default=600)
    parser.add_argument(
        '--with_decoration', help='the graph window will have decorations', required=False, action='store_true')
    parser.add_argument(
        '--rainbow', help='', required=False, action='store_true')
    parser.add_argument(
        '--nb_rainbow_colors', help='numbers of colors for rainbow mode', required=False, default=10)

    # parse the arguments
    args = parser.parse_args()

    # main window
    master = Tkinter.Tk()

    ### size and position
    master.geometry(str(args.x_size)+'x'+str(args.y_size)+'+'+str(
        args.x_position)+'+'+str(args.y_position))

    # backtrace is now in second
    backtrace = 3600*args.backtrace_time

    # hide the window decoration
    if not args.with_decoration:
        master.wm_overrideredirect(True)

    # main figure
    main_figure = Figure()
    canvas = FigureCanvasTkAgg(main_figure, master=master)

    canvas.show()
    canvas.get_tk_widget().pack(fill=Tkinter.BOTH, expand=1)

    now = UTCDateTime()
    round_end = UTCDateTime(now.year, now.month, now.day, now.hour + 1, 0, 0)
    round_start = round_end-backtrace

    # cl is the seedlink client
    cl = Seedlink_plotter(main_figure, canvas=canvas,
                          interval=args.x_scale, backtrace=backtrace, args=args)
    cl.parseCmdLineArgs(["", "-S", str(args.network_code)+'_'+str(args.station_name)+':'+str(
        args.location_id)+str(args.channel), "-t", round_start, args.seedlink_server])

    cl.initialize()

    master.after(1, cl.run)
    master.mainloop()
