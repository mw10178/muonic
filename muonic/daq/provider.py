"""
Provides the public interfaces to read from and send to a DAQ card
"""

from __future__ import print_function
import abc
from future.utils import with_metaclass
import logging
import multiprocessing as mp
import re
import queue

try:
    import zmq
except ImportError:
    # DAQMissingDependencyError will be raised when trying to use zmq
    pass

# from exception.py
from .exceptions import DAQIOError, DAQMissingDependencyError 
# from simulation.py & connection.py 
from .simulation import DAQSimulationConnection
from .connection import DAQConnection

"""
#################################################################
"""

class BaseDAQProvider(with_metaclass(abc.ABCMeta, object)):
    """
    Base class defining the public API and helpers for the
    DAQ provider implementations
    
    Params:
    =======
        logger: logging.Logger, default=None
    
    Functions:
    ==========
        __init__(logger=None):
    
        get(*args):
            "Get something from the DAQ."
    
        put(*args):
            "Send something to the DAQ Card."
    
        data_available(*args):
            "Tests if data is available from the DAQ."
            
        _validate_line(line):
            "Controles the occurence of unwanted character."
            
    
    Attributes:
    ===========
        LINE_PATTERN: re (regular expression) object
            "To allow fast validation of the encoded input string from the 
            DAQ Card."
        
    """
    
    LINE_PATTERN = re.compile("^[a-zA-Z0-9+-.,:()=$/#?!%_@*|~' ]*[\n\r]*$")
    # ^ means all not listed characters in the '[ .. ]' are allowed, * means 
    # that the number those previous listed characters occure is not 
    # important for invalidity. Further \n and \r are allowed in arbitrary 
    # number. $ is defined as either the end of the string, or any location 
    # followed by a newline character

    def __init__(self, logger=None):
        if logger is None:
            logger = logging.getLogger()
        self.logger = logger

    @abc.abstractmethod
    def get(self, *args):
        """
        Get something from the DAQ.
        ABSTRACT METHOD, MUST BE OVERRITTEN!
        
        Params:
        =======
            *args: list
                Queue arguments

        Returns:
        ========
            string or None
        """
        return

    @abc.abstractmethod
    def put(self, *args):
        """
        Send information to the DAQ.
        ABSTRACT METHOD, MUST BE OVERRITTEN!
        
        
        Params:
        =======
            *args: list
                Queue arguments

        Returns:
        ========
            string or None
        """
        return

    @abc.abstractmethod
    def data_available(self):
        """
        Tests if data is available from the DAQ.
        ABSTRACT METHOD, MUST BE OVERRITTEN!

        Returns:
        ========
            int or Bool
        """
        return

    def _validate_line(self, line):
        """
        Validates line against pattern. Returns None if the provided line is
        invalid, or the line if it is valid.
        
        Params:
        =======
            line: string
                String to be validated.
                Following char are not allowed in arb. number:
                    'a-z', 'A-Z', '0-9' and +-.,:()=$/#?!%_@*|~'
                The appearance of '\n' and '\r' is irrelevant.     
        
        Returns:
        ========
            string (valid) or None (not valid string from DAQ)
        
        """
        if self.LINE_PATTERN.match(line) is None:
            # Do something more sensible here, like stopping the DAQ then
            # wait until service is restarted?
            self.logger.warning("Got garbage from the DAQ: %s" %
                                line.rstrip('\r\n'))
            return None
        return line


"""
#################################################################
"""

class DAQProvider(BaseDAQProvider):
    """
    DAQProvider Initializes queue object from multiprocessor class and 
    assembles connection with the DAQConnection class object. 
    
    Params:
    =======
        logger: logging.Logger, default=None
        sim: bool, default=False
            Starts a simulated DAQ Card using saved data.
             
    Functions:
    ==========
        __init__(logger=None, sim=False):
    
        get(*args):
            "Get something from the DAQ."
        
        put(*args):
            "Send something to the DAQ Card."
    
        data_available(*args):
            "Tests if data is available from the DAQ."
            
        _validate_line(line):
            "Controles the occurence of unwanted character."
            
    
    Attributes:
    ===========
        logger: logger object
        
        LINE_PATTERN: re (regular expression) object
            "To allow fast validation of the encoded input string from the 
            DAQ Card."

        daq: DAQConnection class object
            Provides basic communication functions.

        out_queue: multiprocess.Queue
            Queue for Data from DAQ Card. 
        
        in_queue: multiprocess.Queue
            Queue for Data for DAQ Card.
            
        read_thread: multiprocess.Process
            Object to allow execution of muli process. 
            With daq.read as target. 
        
        write_thread: multiprocess.Process
            Object to allow execution of muli process. 
            With daq.write as target. 

    """

    def __init__(self, logger=None, sim=False):
        BaseDAQProvider.__init__(self, logger)
        self.out_queue = mp.Queue()
        self.in_queue = mp.Queue()

        if sim:
            self.daq = DAQSimulationConnection(self.in_queue, self.out_queue,
                                               self.logger)
        else:
            self.daq = DAQConnection(self.in_queue, self.out_queue,
                                     self.logger)
        
        # Set up the thread to do asynchronous I/O. More can be made if
        # necessary. Set daemon flag so that the threads finish when the main
        # app finishes
        self.read_thread = mp.Process(target=self.daq.read, name="pREADER")
        self.read_thread.daemon = True
        self.read_thread.start()

        if not sim:
            self.write_thread = mp.Process(target=self.daq.write,
                                           name="pWRITER")
            self.write_thread.daemon = True
            self.write_thread.start()
        
    def get(self, *args):
        """
        Get something from the DAQ.
        It accesses the queue object. And returns valid string.
        
        Params:
        =======
            args: list
                Queue arguments
        
        Returns:
        ========
            str or None -- next item from the queue
            
        RAISES:
        =======
            
             DAQIOError if the queue is empty.

        """
        try:
            line = self.out_queue.get(*args)
        except queue.Empty:
            raise DAQIOError("Queue is empty")

        return self._validate_line(line)

    def put(self, *args):
        """
        Send information to the DAQ. 
        By puttning the args to the queue object.
        
        Params:
        =======
            args: list
                  Queue arguments        
        
        Returns:
        ========
            None
            
        """
        self.in_queue.put(*args)

    def data_available(self):
        """
        Tests if data is available from the DAQ.

        :returns: int or bool
        """
        try:
            size = self.out_queue.qsize()
        except NotImplementedError:
            self.logger.debug("Running Mac version of muonic.")
            size = not self.out_queue.empty()
        return size


"""
#################################################################
"""

class DAQClient(BaseDAQProvider):
    """
    DAQProvider Initializes zmq.Context().socket and 
    assembles connection with the DAQConnection class object. 
    
    Params:
    =======
        address: str, default='127.0.0.1'
            address to connect to
        port: int, default=5556
            TCP port to connect to
        logger: logging.Logger, default=None
             
    Functions:
    ==========
        __init__(address='127.0.0.1', port=5556, logger=None):
    
        get(*args):
            "Get something from the DAQ."
        
        put(*args):
            "Send something to the DAQ Card."
    
        data_available(*args):
            "Tests if data is available from the DAQ."
            
        _validate_line(line):
            "Controles the occurence of unwanted character."
            
    
    Attributes:
    ===========
        logger: logger object
        
        LINE_PATTERN: re (regular expression) object
            "To allow fast validation of the encoded input string from the 
            DAQ Card."

        socket: zmq.Context().socket
            Provides basic communication functions.

    Raises:
    =======
        DAQMissingDependencyError: if zmq is not installed.
    """
    
    def __init__(self, address='127.0.0.1', port=5556, logger=None):
        BaseDAQProvider.__init__(self, logger)
        try:
            self.socket = zmq.Context().socket(zmq.PAIR)
            self.socket.connect("tcp://%s:%d" % (address, port))
        except NameError:
            raise DAQMissingDependencyError("no zmq installed...")

    def get(self, *args):
        """
        Get something from the DAQ.
        It accesses the zmq-socket object. And returns valid string.
        
        Params:
        =======
            args: list
                Redundant for queue arguments to fit the syntax 
                of DAQProvider.get. Arguments not used in this function.
        
        Returns:
        ========
            str or None -- next item from socket
            
        RAISES:
        =======
             DAQIOError if the socket is empty or else.
        """
        try:
            line = self.socket.recv_string()
        except Exception:
            raise DAQIOError("Socket error")
        
        return self._validate_line(line)

    def put(self, *args):
        """
        Send information to the DAQ.
        By accessing the zmq-socket object.
        
        Params:
        =======
            args: list
                  Socket arguments        
        
        Returns:
        ========
            None
            
        """
        self.socket.send_string(*args)

    def data_available(self):
        """
        Tests if data is available from the DAQ.

        Returns:
        ========
            int or bool
        """
        return self.socket.poll(200)
