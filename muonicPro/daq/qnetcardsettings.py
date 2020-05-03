"""
Class object for application settings store
"""
from __future__ import print_function
from datetime import datetime
import numpy as np
import time
import sys
import os
import json

from .exceptions import DAQIOError, DAQMissingDependencyError


class  QnetCardSettings():
    '''
    Utils:
    ======
        get_thresholds_from_msg
        get_channels_from_msg

    Setup Functions:
    ================
        enable_status_report
        disable_status_report
        enable_write_pulses
        disable_write_pulses
        change_thresholds
        set_channel_config


    Read Functions:
    ===============
        get_threshold_from_card
            Return: bool if succesfully

    '''
    _default_settings = {
            "write_pulses": False,         # 1
            "scalar_data": False,          # 2
            "reset_counter": False,        # 3
            "write_daq_status": 0,         # 4
            "time_window": 5.0,            # 5  OLD Variable
            "gate_width": 100.0,           # 6  coincedence time
            "veto": False,                 # 7
            "veto_ch0": False,             # 8
            "veto_ch1": False,             # 9
            "veto_ch2": False,             # 10
            "active_ch0": True,            # 11
            "active_ch1": True,            # 12
            "active_ch2": True,            # 13
            "active_ch3": True,            # 14
            "coincidence0": True,          # 15
            "coincidence1": False,         # 16
            "coincidence2": False,         # 17
            "coincidence3": False,         # 18
            "threshold_ch0": 300,          # 19
            "threshold_ch1": 300,          # 20
            "threshold_ch2": 300,          # 21
            "threshold_ch3": 300           # 22
        }


    def __init__(self, daq, logger, multiprocessing_mananger, path_to_save=None, default=False, status_report=False):
        '''
        daq: Daq Provider to communicate with hardware
        logger:
        multiprocessing_mananger: Multiprocessing-manager to generate dictionary
            which can be accessed by mutiple threads
        '''
        self.daq = daq
        self.logger = logger
        self.path_to_save = path_to_save
        self._settings = multiprocessing_mananger.dict()

        if default:
            self.apply_default_settings()
        else:
            self.get_configuration_from_daq_card()
            self.disable_write_pulses()
        if status_report:
            self.enable_status_report()
        else:
            self.disable_status_report()

    def save(self, name=None):
        '''
        Saves the settings in a json file only
        if path to save is defined by init of the qnetsettings.

        If settings folder is not in ~/muonic_data it will
        be created.

        Parameter:
        ==========
            name: string
                name of the data file without suffix
                default: None -> current date
        '''
        if self.path_to_save is None:
            self.logger.info('No path defined.')
            return
        if not os.path.isdir(self.path_to_save):
            self.logger.info('Did not found muonic\'s settings folder.')
            os.path.mkdir(self.path_to_save)
            self.logger.info('Created: %s'%muonic.path_to_save)

        if name is None:
            name = datetime.today().strftime('%Y-%m-%d')
        dir = self.path_to_save + '/' + name + '.qnet'
        with open(dir, 'w') as f:  # writing JSON object
            json.dump(self._settings, f)
        self.logger.info('Saved the Qnet settings into %s'%name)

    def load(self, name=None):
        '''
        Load a qnet settings json file from settings folder in
        ~/muonic_data/settings. If name is None, it will print
        available setting files without suffix.

        Parameter:
        ==========
            name: string
                name of the data file without suffix
                default: None -> show list of files
        '''
        if name is None:
            l = []
            for e in os.listdir(self.path_to_save):
                if e.endswith('.qnet'): l.append(e[:-5])
            print('Available settings are: \n'+str(l))
            return
        dir = self.path_to_save + '/' + name + '.qnet'
        with open(dir, 'r') as f:
            self._settings = json.load(f)
        self.logger.info('Loaded the Qnet settings from %s'%name)

        self.apply_settings(self._settings)

    def update_setting(self, key, value):
        """
        Update value for settings key.

        Raises KeyError if key is None.

        :param key: settings key
        :type key: str
        :param value: setting value
        :type value: object
        :raises: KeyError
        :returns: None
        """

        if key is None:
            raise KeyError("key must not be of 'None-Type'")

        self._settings[key] = value

    def update_settings_from_msg(self, msg):
        '''
        Use input msg from card and update the settings

        Kann der Thread die variablen verändern?
        '''
        pass


    def have_setting(self, key):
        """
        Returns true if settings key exists, False otherwise.

        :param key: settings key
        :type key: str
        :returns: bool
        """
        return key in self._settings


    def get_setting(self, key, default=None):
        """
        Retrieves the settings value for given key.

        :param key: settings key
        :type key: str
        :param default: the default value if setting is not found
        :type default: mixed
        :returns: object
        """
        return self._settings.get(key, default)



    def apply_settings(self, newsettings):
        """
        Take dictionary and apply settings on the card.

        :param newsettings: settings dictionary
        :type settings: dict
        :param clear: clear settings store before updating settings
        :type clear: bool
        :returns: None
        """
        if newsettings is None:
            return
        if isinstance(newsettings, dict):
            keys = self._settings.keys()
            # set channel configuration
            active_ch = [newsettings['active_ch%d'%i] for i in range(4)]
            coincidence_config = [newsettings['coincidence%d'%i]
                                   for i in range(4)]
            veto = newsettings['veto']
            veto_config = [newsettings['veto_ch%d'%i] for i in range(3)]
            self.set_channel_config(active_ch, coincidence_config,
                      veto, veto_config)

            # set Thresholds
            threshold = [newsettings['threshold_ch%d'%i] for i in range(4)]
            self.set_thresholds(threshold)

            # set gate witdh
            self.set_gate_width(newsettings['gate_width'])

            # set status report
            if newsettings['write_daq_status']:
                self.enable_status_report(
                        scalar_data=newsettings['scalar_data'],
                        reset_counter=newsettings['reset_counter']
                        )
            else:
                self.disable_status_report()

            # write pulses
            if newsettings['write_pulses']:
                self.enable_write_pulses()
            else:
                self.disable_write_pulses()
        else:
            raise TypeError("Argument has to be a dict")

    def apply_default_settings(self, clear=False):
        """
        Apply default settings. If 'clear' is False settings keys
        different from the default settings will retain.

        :param clear: clear settings store before applying default settings
        :type clear: bool
        :returns: None
        """
        self.apply_settings(self._default_settings)


    def dump_settings(self):
        """
        Prints the current settings.

        :returns: None
        """
        # active channels
        active_ch = {i:self._settings['active_ch%d'%i] for i in range(4)}
        print("Active channels:\n"+"="*16+"\n%s\n"%str(active_ch))
        # coincedence
        coincidence_mask = np.array([self._settings['coincidence%d'%i]
                               for i in range(4)])
        print('Coincidence: ' + np.array(['Set off', 'Twofold',
                  'Threefold', 'Fourfold'])[coincidence_mask][0])
        # set gate witdh
        print('Gate width for coincendent events: ',
                self._settings['gate_width'], '\n')

        # veto
        veto = self._settings['veto']
        veto_mask = np.array([self._settings['veto_ch%d'%i]
                               for i in range(3)])
        veto_config = {(i+1):self._settings['veto_ch%d'%i] for i in range(3)}
        print('Veto is ' + ('active.' if veto else 'inactive.') )
        print('Veto channel is:', np.array(['1', '2',
                  '3'])[veto_mask], '\n')

        # Thresholds
        threshold = {'Ch%d'%i:self._settings['threshold_ch%d'%i]
                        for i in range(4)}
        print("Thresholds:\n"+"="*11+"\n%s\n"%str(threshold))

        # Status report
        wds = self._settings['write_daq_status']
        sd = self._settings['scalar_data']
        rc = self._settings['reset_counter']
        print('Automatic status report is '+('enabled.' if wds > 0 else
                'disabled.'))
        if wds > 0:
            print('Report every %d min.'%wds)
            if sd: print('Counts will be shown.')
            if rc: print('Counters will be reseted at each report.')

        # written pulses
        wp = self._settings['write_pulses']
        print('QnetCard sends informations (TMC) of detected pulses.' if wp else
                'QnetCard does not send pulse informations (TMC).')

    def get_thresholds_from_msg(self, msg):
        """
        Explicitly scan message for threshold information.

        Return True if found, False otherwise.

        :param msg: daq message
        :type msg: str
        :returns: bool
        """
        if msg.startswith('TL') and len(msg) > 9:
            msg = msg.split('=')
            self.update_setting("threshold_ch0", int(msg[1][:-2]))
            self.update_setting("threshold_ch1", int(msg[2][:-2]))
            self.update_setting("threshold_ch2", int(msg[3][:-2]))
            self.update_setting("threshold_ch3", int(msg[4]))
            self.logger.debug("Got Thresholds %d %d %d %d" %
                              tuple([self.get_setting("threshold_ch%d" % i)
                                     for i in range(4)]))
            return True
        else:
            self.logger.debug("Was not able to interprete:\n%s"%msg)
            return False

    def get_channels_from_msg(self, msg):
        """
        Explicitly scan message for channel information.

        Return True if found, False otherwise.

        DC gives:

        DC C0=23 C1=71 C2=0A C3=00

        Which has the meaning:

        MM - 00 -> 8bits for channel enable/disable, coincidence and veto

        +---------------------------------------------------------------------+
        |                              bits                                   |
        +====+====+===========+===========+========+========+========+========+
        |7   |6   |5          |4          |3       |2       |1       |0       |
        +----+----+-----------+-----------+--------+--------+--------+--------+
        |veto|veto|coincidence|coincidence|channel3|channel2|channel1|channel0|
        +----+----+-----------+-----------+--------+--------+--------+--------+

        +-----------------+
        |Set bits for veto|
        +=================+
        |00 - ch0 is veto |
        +-----------------+
        |01 - ch1 is veto |
        +-----------------+
        |10 - ch2 is veto |
        +-----------------+
        |11 - ch3 is veto |
        +-----------------+

        +------------------------+
        |Set bits for coincidence|
        +========================+
        |00 - singles            |
        +------------------------+
        |01 - twofold            |
        +------------------------+
        |10 - threefold          |
        +------------------------+
        |11 - fourfold           |
        +------------------------+

        :param msg: daq message
        :type msg: str
        :returns: bool
        """
        if msg.startswith('DC ') and len(msg) > 25:
            msg = msg.split(' ')

            coincidence_time = msg[4].split('=')[1] + msg[3].split('=')[1]
            msg = bin(int(msg[1][3:], 16))[2:].zfill(8)
            veto_config = msg[0:2]
            coincidence_config = msg[2:4]
            active_ch = msg[4:8]

            self.update_setting("gate_width", int(coincidence_time, 16) * 10)

            # set default veto config
            for i in range(4):
                if i == 0:
                    self.update_setting("veto", True)
                else:
                    self.update_setting("veto_ch%d" % (i - 1), False)

            # update channel config
            for i in range(4):
                self.update_setting("active_ch%d" % i,
                               active_ch[3 - i] == '1')

            # update coincidence config
            for i, seq in enumerate(['00', '01', '10', '11']):
                self.update_setting("coincidence%d" % i,
                               coincidence_config == seq)

            # update veto config
            for i, seq in enumerate(['00', '01', '10', '11']):
                if veto_config == seq:
                    if i == 0:
                        self.update_setting("veto", False)
                    else:
                        self.update_setting("veto_ch%d" % (i - 1), True)

            self.logger.debug('gate width timew indow %d ns' %
                              self.get_setting("gate_width"))
            self.logger.debug("Got channel configurations: %d %d %d %d" %
                              tuple([self.get_setting("active_ch%d" % i)
                                     for i in range(4)]))
            self.logger.debug("Got coincidence configurations: %d %d %d %d" %
                              tuple([self.get_setting("coincidence%d" % i)
                                     for i in range(4)]))
            self.logger.debug("Got veto configurations: %d %d %d %d" %
                              tuple([self.get_setting("veto")] +
                                    [self.get_setting("veto_ch%d" % i)
                                     for i in range(3)]))

            return True
        else:
            self.logger.debug("Was not able to interprete:\n%s"%msg)
            return False



#############################################################
#-----------------------------------------------------------#
#############################################################


    def get_threshold_from_card(self):
        """
        Explicitly scan message for threshold information.

        Return True if found, False otherwise.

        :param msg: daq message
        :type msg: str
        :returns: bool
        """
        # get the thresholds
        self.daq.put('TL')
        # give the daq some time to react
        time.sleep(0.5)

        while self.daq.data_available():
            try:
                msg = self.daq.get(0)
                self.get_thresholds_from_msg(msg)

            except DAQIOError:
                self.logger.debug("Queue empty!")

    def get_configuration_from_daq_card(self):
        """
        Get the initial threshold and channel configuration
        as well as the gate width from the DAQ card.
        """
        # get the thresholds
        self.get_threshold_from_card()

        # get the channel config
        self.daq.put('DC')
        # give the daq some time to react
        time.sleep(0.2)

        while self.daq.data_available():
            try:
                msg = self.daq.get(0)
                self.get_channels_from_msg(msg)

            except DAQIOError:
                self.logger.debug("Queue empty!")

    def get_channel_configurations(self):
        '''
        Return:
        =======
            Channel configurations.
        '''
        self.get_configuration_from_daq_card()

        active_ch = [self._settings['active_ch%d'%i]
                               for i in range(4)]
        coincidence_config = [self._settings['coincidence%d'%i]
                               for i in range(4)]
        veto = self._settings['veto']
        veto_config = [self._settings['veto_ch%d'%i]
                               for i in range(3)]
        return active_ch, coincidence_config, veto, veto_config


    def set_thresholds(self, thresholds):
        '''
        Changes thresholds
        List must have a maximal length of 4.
        :thresholds: list
        '''
        if len(thresholds) <= 4:
            commands = []
            # update thresholds config
            for ch, val in enumerate(thresholds):
                self.update_setting("threshold_ch%d" % ch, val)
                commands.append("TL %d %s" % (ch, val))

            # apply new thresholds to daq card
            for cmd in commands:
                self.daq.put(cmd)
                self.logger.info("Set threshold of channel %s to %s" %
                                 (cmd.split()[1], cmd.split()[2]))
        else:
            self.logger.info('List must have a maximal length of 4. ')

    def set_active_channels(self, channels):
        '''
        Change state of the channels.

        Parameters:
        ===========
            channels: list or tuple of integer from 0 to 3
                Channels which shall be active.
        '''
        (active_ch, coincidence_config,
            veto, veto_config) = self.get_channel_configurations()

        active_ch = [i in channels for i in range(4)]

        self.set_channel_config(active_ch, coincidence_config,
                              veto, veto_config)
        self.logger.info('New active channels are %s'%str(channels))


    def set_coincidence(self, n):
        '''
        Change the number of channels which need to be coincident
        to generate a trigger.

        Parameter:
        ==========
            n: int 1 to 4
        
        Set off: [True, False, False, False]
        Twofold: [False, True, False, False]
        Threefold: [False, False, True, False]
        Fourfold: [False, False, False, True]
        '''
        if not in range(1,5):
            print('Argument needs to be between 1 and 4.')
            return

        (active_ch, coincidence_config,
            veto, veto_config) = self.get_channel_configurations()

        coincidence_config = [False for i in range(4)]
        coincidence_config[n-1] = True

        self.set_channel_config(active_ch, coincidence_config,
                              veto, veto_config)
        coincidence_mask = np.array([self._settings['coincidence%d'%i]
                               for i in range(4)])
        self.logger.info('New coincedence is %s'%str(np.array(['Set off',
            'Twofold', 'Threefold', 'Fourfold'])[coincidence_mask][0]))

    def enable_veto(self):
        '''
        Enable vetoing.
        '''
        (active_ch, coincidence_config,
            veto, veto_config) = self.get_channel_configurations()
        self.set_channel_config(active_ch, coincidence_config,
                              True, veto_config)
        if self._settings['veto']:
            self.logger.info('Vetoing has been enabled')
        else:
            raise SystemError("Something went wrong.")

    def disable_veto(self):
        '''
        Enable vetoing.
        '''
        (active_ch, coincidence_config,
            veto, veto_config) = self.get_channel_configurations()
        self.set_channel_config(active_ch, coincidence_config,
                              False, veto_config)
        if not self._settings['veto']:
            self.logger.info('Vetoing has been enabled')
        else:
            raise SystemError("Something went wrong.")

    def set_veto_channel(self, n):
        '''
        Set the channels which shall work as veto.
        Only channel on of 1,2 or 3 can be used as veto.

        Parameter:
        ==========
            n: int 1 to 3
        '''
        (active_ch, coincidence_config,
            veto, veto_config) = self.get_channel_configurations()

        veto_config = [False for i in range(3)]
        veto_config[n-1] = True

        self.set_channel_config(active_ch, coincidence_config,
                              True, veto_config)
        veto_mask = np.array([self._settings['veto_ch%d'%i]
                               for i in range(3)])
        self.logger.info('New veto is channel %s'%str(np.array(['1',
            '2', '3'])[veto_mask][0]))

    def set_channel_config(self, active_ch, coincidence_config,
                          veto, veto_config):
        '''
        Change the channel configuration of the QnetCard:
        Which channels are active: 0,1,2,3?
        How many coincident signals are needed for the trigger?
        Are there a channel which works as veto? --> para: veto
        Which channel works as veto: 1,2 or 3

        Parameters:
        ===========
            active_ch: list of bool, len = 4
                Active channels
                default=None
            coincidence_config: list of bool, len = 4
                single, twofold, threefold, fourfold
                default=None
            veto: bool
                Veto is active or not
                default=None
            veto_config: list of bool, len = 3
                Veto on Channel 1, 2 or 3
                default=None
        '''

        # active_ch and veto_config input with respect to unambiguity
        if sum(coincidence_config) > 1:
            self.logger.info("I have got an ambiguous input for"+
                "coincidence_config: \n%s "%str(coincidence_config)+
                "and used the default instead.")
            for i in range(4):
                active_ch[i] = self.get_setting("coincidence%d" % i)
        elif sum(coincidence_config) == 0:
                active_ch[0] = True

        if sum(veto_config) > 1:
            self.logger.info("I have got an ambiguous input for"+
                "veto_config: \n%s "%str(veto_config)+
                "and used the default instead.")
            for i in range(3):
                veto_config[i] = self.get_setting("veto_ch%d" % i)

        # update the settings dictionary with resp. active channels,
        # veto state and veto channel
        for i in range(4):
            self.update_setting("active_ch%d" % i, active_ch[i])
            self.update_setting("coincidence%d" % i, coincidence_config[i])
        self.update_setting("veto", veto)
        for i in range(3):
            self.update_setting("veto_ch%d" % i,
                veto_config[i] if veto else False)

        # build daq message to apply the new config to the card
        tmp_msg = ""

        if veto:
            if veto_config[0]:
                tmp_msg += "01"
            elif veto_config[1]:
                tmp_msg += "10"
            elif veto_config[2]:
                tmp_msg += "11"
            else:
                tmp_msg += "00"
        else:
            tmp_msg += "00"

        # singles, twofold, threefold, fourfold
        if sum(coincidence_config) <= 1:
            for i, coincidence in enumerate(["00", "01", "10", "11"]):
                if coincidence_config[i]:
                    tmp_msg += coincidence

        # now calculate the correct expression for the first
        # four bits
        self.logger.debug("The first four bits are set to %s" % tmp_msg)
        msg = "WC 00 %s" % hex(int(''.join(tmp_msg), 2))[-1].capitalize()

        channel_set = False
        enable = ['0', '0', '0', '0']

        for i, active in enumerate(reversed(active_ch)):
            if active:
                enable[i] = '1'
                channel_set = True

        if channel_set:
            msg += hex(int(''.join(enable), 2))[-1].capitalize()
        else:
            msg += '0'

        # send the message to the daq card
        self.daq.put(msg)

        self.logger.info("The following message was sent to DAQ: %s" % msg)

        for i in range(4):
            self.logger.debug("channel%d selected %s" %
                              (i, active_ch[i]))

        for i, name in enumerate(["singles", "twofold",
                                  "threefold", "fourfold"]):
            self.logger.debug("coincidence %s %s" %
                              (name, coincidence_config[i]))


    def enable_status_report(self, dt=1, scalar_data=False, reset_counter=False):
        '''
        Show status line: channels & coincidence.
        Important: run this command for each data session.

        Parameter
        =========
            dt: int
                Period for status report in full minutes.
                Between [1 min, 30 min]. default=1
            scalar_data: bool
                default=False

            reset_counter: bool
                default=False
        '''

        if (scalar_data and reset_counter) or reset_counter:
            msg = 'ST 3 %d'%dt
            self.update_setting('scalar_data', True)
            self.update_setting('reset_counter', True)
            scalar_data = True
        elif scalar_data:
            msg = 'ST 2 %d'%dt
            self.update_setting('scalar_data', True)
        else:
            msg = 'ST 1 %d'%dt
        self.update_setting('write_daq_status', dt)
        self.daq.put(msg)
        self.logger.info("Enabled status report with: \n"+
            "scalar_data: %s\n"%str(bool(scalar_data))+
            "reset_counter: %s\n"%str(bool(reset_counter))+
            "Report is every %d min."%dt)

    def disable_status_report(self):
        '''
        Disable status reporting
        '''
        self.update_setting('write_daq_status', 0)
        self.update_setting('scalar_data', False)
        self.update_setting('reset_counter', False)
        self.daq.put('ST 0')
        self.logger.info("Disabled status report.")


    def enable_write_pulses(self):
        '''
        TMC Counter Enable
        Send all pulses to buffer. This
        command has the opposite effect of the CD command.
        '''
        self.update_setting('write_pulses', True)
        self.daq.put('CE')


    def disable_write_pulses(self):
        '''
        TMC Counter Disable
        Does not send all pulses to buffer.
        even though the scalars will still increment. This is useful when you do
        not want to “see” all the data coming in.
        '''
        self.update_setting('write_pulses', False)
        self.daq.put('CD')

    def set_gate_width(self, gate_width):
        '''
        Set maximal time difference for sequentially measured events
        to be coincident. In ns.
        '''
        gate_width = int(gate_width)
        #self.update_setting("gate_width", gate_width)

        # transform gate width for daq msg
        gate_width_b = bin(gate_width // 10).replace('0b', '').zfill(16)
        gate_width_03 = format(int(gate_width_b[0:8], 2), 'x').zfill(2)
        gate_width_02 = format(int(gate_width_b[8:16], 2), 'x').zfill(2)

        # set gate widths
        self.daq.put("WC 03 %s" % gate_width_03)
        self.daq.put("WC 02 %s" % gate_width_02)
        self.logger.info("Changed gate window for coincedence to "+
                "%d"%gate_width)
