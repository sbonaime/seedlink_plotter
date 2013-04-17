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
from obspy.core.event import Catalog
from obspy.neries import Client
from argparse import ArgumentParser
from math import sin
import threading
import time
import warnings
import sys
from urllib2 import URLError


class SeedlinkPlotter(Tkinter.Tk):
    """
    This module plots realtime seismic data from a Seedlink server
    """
    def __init__(self, stream=None, events=None, myargs=None, lock=None, *args, **kwargs):
        Tkinter.Tk.__init__(self, *args, **kwargs)
        args = myargs
        self.lock = lock
        ### size and position
        self.geometry(str(args.x_size)+'x'+str(args.y_size)+'+'+str(
            args.x_position)+'+'+str(args.y_position))
        # hide the window decoration
        if not args.with_decoration:
            self.wm_overrideredirect(True)

        # main figure
        self.figure = Figure()
        canvas = FigureCanvasTkAgg(self.figure, master=self)

        canvas.show()
        canvas.get_tk_widget().pack(fill=Tkinter.BOTH, expand=1)

        self.interval = args.x_scale
        self.backtrace = args.backtrace_time
        self.canvas = canvas
        self.scale = args.scale
        self.args = args
        self.stream = stream
        self.events = events

        # Colors
        if args.rainbow:
            # Rainbow colors !
            self.color = self.rainbow_color_generator(
                int(args.nb_rainbow_colors))
        else:
            # Regular colors
            self.color = ('#000000', '#ff0000', '#0000ff', '#56a83c')

        self.plot_graph()

    def plot_graph(self):

        with self.lock:
            stream = self.stream.copy()
        try:
            title = stream[0].id + ' scale: '+str(self.scale) + " - non filtre"
            self.figure.clear()
            stream.plot(
                fig=self.figure, type='dayplot', interval=self.args.x_scale,
                number_of_ticks=13, tick_format='%d/%m %Hh',
                size=(self.args.x_size, self.args.y_size),
                x_labels_size=8, y_labels_size=8,
                title=title, title_size=14,
                linewidth=0.5, right_vertical_labels=False,
                vertical_scaling_range=self.args.scale,
                subplots_adjust_left=0.03, subplots_adjust_right=0.99,
                subplots_adjust_top=0.95, subplots_adjust_bottom=0.1,
                one_tick_per_line=True,
                # noir  Rouge bleu vert
                color=self.color,
                show_y_UTC_label=False,
                events=self.events)
        except:
            pass
        self.after(int(self.args.update_time*1000), self.plot_graph)

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


class SeedlinkUpdater(SLClient):
    def __init__(self, stream, myargs=None, lock=None):
        # Set the log level to display minimal info
        super(SeedlinkUpdater, self).__init__(loglevel='CRITICAL')
        self.stream = stream
        self.lock = lock

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

        #limit the length of main stream buffer
        now = UTCDateTime()
        stop_time = UTCDateTime(now.year, now.month, now.day, now.hour, 0, 0)+3600
        start_time = stop_time-args.backtrace_time

        # new samples add to the main stream which is then trimmed
        with self.lock:
            self.stream += trace
            self.stream.merge()
            self.stream.trim(start_time, stop_time, nearest_sample=False)
        return False


class EventUpdater():
    def __init__(self, stream, events, myargs=None, lock=None):
        self.stream = stream
        self.events = events
        self.args = myargs
        self.lock = lock
        warn_msg = "The resource identifier already exists and points to " + \
                   "another object. It will now point to the object " + \
                   "referred to by the new resource identifier."
        warnings.filterwarnings("ignore", warn_msg)

    def run(self):
        """
        Endless execution to update events. Does not terminate, to be run in a
        (daemon) thread.
        """
        while True:
            # no stream, reschedule event update in 10 seconds
            if not self.stream:
                time.sleep(10)
                continue
            try:
                events = self.get_events()
            except URLError, e:
                msg = "%s: %s\n" % (e.__class__.__name__, e)
                sys.stderr.write(msg)
            except Exception, e:
                msg = "%s: %s\n" % (e.__class__.__name__, e)
                sys.stderr.write(msg)
            else:
                self.update_events(events)
            time.sleep(self.args.events_update_time * 60)

    def get_events(self):
        """
        Method to fetch updated list of events to use in plot.
        """
        with self.lock:
            start = self.stream[0].stats.starttime
            end = self.stream[0].stats.endtime
        c = Client()
        events = c.getEvents(min_datetime=start, max_datetime=end,
                             format="catalog",
                             min_magnitude=self.args.events)
        return events

    def update_events(self, events):
        """
        Method to insert new events into list of events shared with the GUI.
        """
        with self.lock:
            self.events.clear()
            self.events.extend(events)


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
        '--scale', type=int, help='the scale to apply on data ex:50000', required=False)

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
    parser.add_argument(
        '--update_time', help='time in seconds between each graphic update', required=False, default=10, type=float)
    parser.add_argument('--events', required=False, default=None, type=float,
        help='plot events using obspy.neries, specify minimum magnitude')
    parser.add_argument('--events_update_time', required=False, default=10, type=float,
        help='time in minutes between each event data update')
    # parse the arguments
    args = parser.parse_args()

    # backtrace is now in second
    args.backtrace_time = 3600 * args.backtrace_time

    now = UTCDateTime()
    round_end = UTCDateTime(now.year, now.month, now.day, now.hour + 1, 0, 0)
    round_start = round_end-args.backtrace_time

    # main window
    stream = Stream()
    events = Catalog()
    lock = threading.Lock()
    master = SeedlinkPlotter(stream=stream, events=events, myargs=args, lock=lock)

    # cl is the seedlink client
    cl = SeedlinkUpdater(stream, myargs=args, lock=lock)
    cl.parseCmdLineArgs(["", "-S", str(args.network_code)+'_'+str(args.station_name)+':'+str(
        args.location_id)+str(args.channel), "-t", round_start, args.seedlink_server])
    cl.initialize()
    thread = threading.Thread(target=cl.run)
    thread.setDaemon(True)
    thread.start()

    # start another thread for event updating if requested
    if args.events is not None:
        eu = EventUpdater(stream=stream, events=events, myargs=args, lock=lock)
        thread = threading.Thread(target=eu.run)
        thread.setDaemon(True)
        thread.start()

    master.mainloop()
