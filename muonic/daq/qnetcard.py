import multiprocessing
from .provider import DAQClient, DAQProvider
from .qnetcardsettings import QnetCardSettings
import logging
import time

class QnetCard():
    '''
    QnetCard object class for communication with
    Quarknet Scintillator Card

    Parameter:
    ==========
        daq: provider class object
            For basic communication on hardware level.
            Default: None --> starts an own provider by itself
        logger: logging class object
            For information about program's status on command line.
            Default: None --> init. an logging object by itself
        port: str
            Port for communication based on zmq socket.
            Default: None --> Communication via multiprocessing.Queue
        sim: bool
            Provider based on multiprocessing.Queue provides an simulation
            of a Quarknet Scintillator Card.
            Default: False, True --> Forces communication via multiprocessing.Queue
        verbose: bool
            Changes the level of the self initialized logger to "logging.DEBUG".
            Default: False

    Functions:
    ==========
        help_com
    '''


    def __init__(self, path_to_save=None, daq=None, logger=None, port=None, sim=False, verbose=False):
        # set up logger
        if logger is None:
            formatter = logging.Formatter("%(levelname)s:%(process)d:%(module)s:" +
                                          "%(funcName)s:%(lineno)d:%(message)s")
            ch = logging.StreamHandler()
            ch.setLevel(logging.DEBUG if verbose else logging.INFO)
            ch.setFormatter(formatter)

            logger = logging.getLogger()
            logger.setLevel(logging.DEBUG if verbose else logging.INFO)
            logger.addHandler(ch)
        self.logger = logger

        # set up providers for hardware near communication
        if daq is not None:
            self.daq = daq
        elif port is not None and not sim:
            self.daq = DAQClient(port=port, logger=logger)
            logger.info('Client with zmq socket has started.'+
                'with port %s'%port
                )
        else:
            self.daq = DAQProvider(sim=sim, logger=logger)
            if sim and port is not None:
                self.logger.info(
                    'Client with zmq does not support a simulation.'+
                    'Provider with with multiprocessing.Queue '+
                    'has started instead.'
                    )
            else:
                self.logger.info('Provider with with multiprocessing.Queue '+
                    'has started.'
                    )

        # set up settings class object to handle all settings
        self.settings = QnetCardSettings(self.daq, self.logger, path_to_save)
        self.settings.get_configuration_from_daq_card()

        # start multiprocessing manager for distribute incomming messages from 
        # QnetCard to multiprocessing lists and react for incomming 
        # settings like threshold and channel informations
        self.multiprocessing_mananger = multiprocessing.Manager()
        pulse_data = self.multiprocessing_mananger.list() 
        status_data = self.multiprocessing_mananger.list()
        gps_data = self.multiprocessing_mananger.list()
        counter_data = self.multiprocessing_mananger.list()
        self.data = {'pulse': pulse_data,
                     'status': status_data,
                     'gps': gps_data,
                     'counts': counter_data}
        # set up and start thread
        self.distribute_thread = multiprocessing.Process(target=self.distribute)
        self.distribute_thread.deamon = True
        self.distribute_thread.start()

    def distribute(self):
        '''
        Function which interpretes incomming messages
        from the multiprocessing output queue / zmq stack of the provider 
        and distribute those to the multiprocessing lists in the data dictionary.
         
        THE FOLLOWING FUNCTIONS IN QNETCARDSETTINGS NEEDS TO CHANGED:
        get_channel_configurations
        get_threshold_from_card
        get_configuration_from_daq_card
        
        Die Funktionen von settings dürfen nichts mehr aus dem Queue entfernen. Dies
        Übernimmt distribute und übergibt es an settings.update_settings_from_msg
        
        Kann der Thread die daten von settings verändern?
        Müssen die Daten (das dict) von settings auch ein multiprocessing object sein?   
        Vlt multiprocessing.manager.dict? Dann muss settings nach manager initialisiert 
        werden und manager dem settings übergeben werden.
        '''
        pass

    def help_card(self, page=None, show=True):
        '''
        Help containing a list of all ASCII commands from the DAQ Card.
        print: bool
            if True help-string is plotted
        Returns help string
        '''
        if page is None or not page in ['HE', 'H1', 'H2', 'HB', 'HS', 'HT']:
            print('Available help pages are: '+
            '"HE", "H1", "H2", "HB", "HS", "HT" \n'+
            'Please use one of these keys as argument.')
            return None
        self.daq.put(page)
        time.sleep(0.5)
        out = self.flush_output(val=False)
        if show:
            msg = ''
            for e in out: msg+=(e+'\n')
            print(str(msg))
            return
        else:
            return out

    def flush_output(self, val=True):
        '''
        Flushes the output queue or stack and returns it as a list.

        Return:
        =======
            output: list of string
                List of the elements from the output
        '''
        output = []
        try:
            while True:
                output.append(self.daq.get(val=val))
        except:
            pass
        self.logger.info('Output queue or zmq socked is flushed.')
        return output

    def flush_input(self):
        '''
        Flushes the input queue or stack.
        '''
        if self.daq.what() == 'DAQProvider':
            try:
                while True:
                    self.daq.in_queue.get_nowait()
            except:
                pass
            self.logger.info('mp input queue flushed.')
        elif self.daq.what() == 'DAQClient':
            try:
                while True:
                    self.daq.socket.recv_string()
            except:
                pass
            self.logger.info('Zmq stack flushed.')
        else:
            raise SystemError('Provider not recoginized.')

    def reset_counter(self):
        '''
        Resets the counters for all channels
        and the trigger.
        '''
        self.daq.put("RB")

    def send_command_and_retrieve(self, msg_str, force=False):
        '''
        Send a string to the QnetCard.
        Use help_card for command overview.

        Parameter:
        ==========
            msg_str: str

        Return:
        =======
            List of received strings from card.
        '''
        # there are commands user should not send manually
        unsecure = msg_str[:2] in ['TL', 'WC', 'ST', 'CE', 'CD']
        unsecure&= 2 < len(msg_str) # only if str is longer it is likely a command
        unsecure&= not force
        if unsecure:
            print('Please use the settings methode to ensure that the program '+
                    'logs the new settings.')
            return

        self.daq.put(msg_str)
        return self.flush_output()
        

