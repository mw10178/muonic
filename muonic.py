#!/usr/bin/env python
#
# This file is part of muonic, a program to work with the QuarkDAQ cards
# Copyright (C) 2009  Robert Franke (robert.franke@desy.de)
#
# muonic is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# muonic is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with muonic. If not, see <http://www.gnu.org/licenses/>.
#
# The way of the communication between the serial port and the GUI is based on
# the receipt presented at http://code.activestate.com/recipes/82965/
# Created by Jacob Hallen, AB Strakt, Sweden. 2001-10-17
# Adapted by Boudewijn Rempt, Netherlands. 2002-04-15
# It is licenced under the Python licence, http://www.python.org/psf/license/

from __future__ import print_function
from argparse import ArgumentParser, RawTextHelpFormatter
import logging
import signal
import sys

from PyQt4 import QtGui

from muonic import __version__, DATA_PATH
from muonic.daq import DAQClient, DAQProvider
from muonic.gui import Application
from muonic.util.helpers import set_data_directory, setup_data_directory


def main(args, logger):
    """
    Application entry point

    :param args: arguments
    :param logger: logger object
    """
    # Defines path to data as global variable
    set_data_directory(args.data_path)
    # Tries to create the data directory if it is not present
    setup_data_directory(args.data_path)

    # QApplication manages the GUI application's control flow and main settings
    # there is always one QApplication object
    root = QtGui.QApplication(sys.argv)
    # Shall the program be closed if the last window will be closed?
    root.setQuitOnLastWindowClosed(True)

    if args.port is not None:
        # client works with zmq socket
        daq = DAQClient(port=args.port, logger=logger)
        logger.info('''Client with zmq socket has started.
                with port %s'''%port)
    else:
        # provider works with multiprocessing.Queue
        daq = DAQProvider(sim=args.sim, logger=logger)
        if args.sim and args.port is not None:
            logger.info('''Client with zmq does not support a simulation.
                Provider with with multiprocessing.Queue
                has started instead.''')
        else:
            logger.info('''Provider with with multiprocessing.Queue
                has started.''')
    # Both works multiprocessing and the read and write function are executed
    # in an endless loop.
    # daq provides get and put functions to communicate with the DAQ Card


    # Set up the GUI part
    gui = Application(daq, logger, args)
    gui.show()
    root.exec_()


#---------------------------
if __name__ == '__main__':
    # handle ctrl+c
    signal.signal(signal.SIGINT, signal.SIG_DFL)

    description = """
This program is dedicated for the use with QNet DAQ cards.
YOURINITIALS are two letters indicating your name.
All files will be stored in (if --data-path is not provided):
  %s
Files are named by the following scheme:
  YYYY-MM-DD_HH-MM-SS_X_Y_YOURINITIALS
where X is the data type of the file:
  R:   Rate plot
  P:   Extracted pulses
  RAW: Raw daq data
  L:   Muon decay times
  G:   Muon velocity measurement
and Y will be the total measurement time""" % DATA_PATH

    parser = ArgumentParser(description=description,
                            formatter_class=RawTextHelpFormatter)

    parser.add_argument('user', metavar='YOURINITIALS',
                        help='your initials',
                        type=str, nargs=1)
    parser.add_argument("-s", "--sim", dest="sim",
                        help="use simulation mode for testing without " +
                             "hardware",
                        action="store_true", default=False)
    parser.add_argument("--port", dest="port",
                        help="listen to daq on port ", default=None)
    parser.add_argument("-t", "--timewindow", dest="time_window",
                        help="time window for the measurement in s " +
                             "(default 5s)",
                        type=float, default=5.0)
    parser.add_argument("-d", "--debug", dest="log_level",
                        help="switch to loglevel debug",
                        action="store_const", const=logging.DEBUG,
                        default=logging.INFO)
    parser.add_argument("-p", "--writepulses", dest="write_pulses",
                        help="write a file with extracted pulses",
                        action="store_true", default=False)
    parser.add_argument("-n", "--nostatus", dest="write_daq_status",
                        help="do not write DAQ status messages to RAW " +
                             "data files",
                        action="store_false", default=True)
    parser.add_argument("-v", "--version", dest="version",
                        help="show current version",
                        action="store_true", default=False)
    parser.add_argument("-P", "--data-path", dest="data_path",
                        help="directory to store measurement data in",
                        type=str, default=DATA_PATH)

    args = parser.parse_args()

    if args.version:
        print(__version__)
        sys.exit(0)

    args.user = args.user[0]

    if len(args.user) != 2:
        parser.error("Incorrect number of arguments, you have to specify " +
                     "just the initials of your name for the file names.\n" +
                     "Initials must be two letters!")

    # set up logging
    formatter = logging.Formatter("%(levelname)s:%(process)d:%(module)s:" +
                                  "%(funcName)s:%(lineno)d:%(message)s")
    ch = logging.StreamHandler()
    ch.setLevel(args.log_level)
    ch.setFormatter(formatter)

    logger = logging.getLogger()
    logger.setLevel(args.log_level)
    logger.addHandler(ch)

    # run
    main(args, logger)