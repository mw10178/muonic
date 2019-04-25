"""
Class object for application settings store
"""
from __future__ import print_function

#__all__ = ["update_setting", "have_setting", "get_setting",
#           "remove_setting", "update_settings",
#           "apply_default_settings", "dump_settings"]
class  DAQCardSettings():
    '''
    enable_status_reporting
    disable_status_reporting
    enable_write_pulses
    disable_write_pulses
    get_thresholds_from_msg
    get_channels_from_msg
    get_threshold_from_card
    '''
    _default_settings = {
            "write_pulses": False,#
            "scalar_data": False,#
            "reset_counter": False,#
            "write_daq_status": False,#
            "time_window": 5.0,
            "gate_width": 0.0,

            "veto": False,          #       ######
            "veto_ch0": False,      #       #
            "veto_ch1": False,      #       #
            "veto_ch2": False,      #       # Read out with
            "active_ch0": True,             # get_configuration_from_daq_card
            "active_ch1": True,             #
            "active_ch2": True,             #
            "active_ch3": True,             #
            "coincidence0": True,   #       #
            "coincidence1": False,  #       #
            "coincidence2": False,  #       #
            "coincidence3": False,  #       #
            "threshold_ch0": 300,           #
            "threshold_ch1": 300,           #
            "threshold_ch2": 300,           #
            "threshold_ch3": 300            #####
        }

    _settings = dict()

    def __init__(daq):
        self.daq = daq


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


    def remove_setting(self, key):
        """
        Remove setting with key.

        :param key: settings key
        :type key: str
        :returns: removed object
        """
        return self._settings.pop(key)


    def clear_settings(self):
        """
        Clears the settings store

        :returns: None
        """
        self._settings.clear()


    def update_settings(self, newsettings, clear=False):
        """
        Add settings from dict.

        :param newsettings: settings dictionary
        :type settings: dict
        :param clear: clear settings store before updating settings
        :type clear: bool
        :returns: None
        """
        if self.newsettings is None:
            return
        if isinstance(self.newsettings, dict):
            if clear:
                self.clear_settings()
            for key, value in list(settings.items()):
                self.update_setting(key, value)
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
        self.update_settings(self._default_settings, clear)


    def dump_settings(self):
        """
        Prints the current settings.

        :returns: None
        """
        for key, value in sorted(self._settings.items()):
            print("%-20s = %s" % (key, value))


#############################################################
#-----------------------------------------------------------#
#############################################################


    def get_configuration_from_daq_card(self):
        """
        Get the initial threshold and channel configuration
        from the DAQ card.

        :returns: None
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

        # get the channel config
        self.daq.put('DC')
        # give the daq some time to react
        time.sleep(0.5)

        while self.daq.data_available():
            try:
                msg = self.daq.get(0)
                self.get_channels_from_msg(msg)

            except DAQIOError:
                self.logger.debug("Queue empty!")

    def change_thresholds(thresholds):
        '''
        Changes thresholds
        List must have a maximal length of 4.
        :thresholds: list
        '''
        if len(thresholds) <= 4:
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


    def enable_status_reporting(self, scalar_data=False, reset_counter=False):
        '''
        Show status line: channels & coincidence.
        Important: run this command for each data session.

        Parameter
        =========
            scalar_data: bool
                default=False

            reset_counter: bool
                default=False
        '''

        if (scalar_data and reset_counter) or reset_counter:
            msg = 'ST 3'
            self.update_setting('scalar_data', True)
            self.update_setting('reset_counter', True)
        elif scalar_data:
            msg = 'ST 2'
            self.update_setting('scalar_data', True)
        else:
            msg = 'ST 1'
        self.update_setting('write_pulses', True)
        self.daq.put(msg)


    def disable_status_reporting(self):
        '''
        Disable status reporting
        '''
        self.update_setting('write_pulses', False)
        self.update_setting('scalar_data', False)
        self.update_setting('reset_counter', False)
        self.daq.put('ST 0')


    def enable_write_pulses(self):
        '''
        TMC Counter Enable
        Writes event lines on the PC monitor. This
        command has the opposite effect of the CD command.
        '''
        self.daq.put('CE')

    def disable_write_pulses(self):
        '''
        TMC Counter Disable
        Does not write event lines on the PC monitor
        even though the scalars will still increment. This is useful when you do
        not want to “see” all the data coming in.
        '''
        self.daq.put('CD')

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
                              tuple([get_setting("threshold_ch%d" % i)
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
            channel_config = msg[4:8]

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
                               channel_config[3 - i] == '1')

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
                              get_setting("gate_width"))
            self.logger.debug("Got channel configurations: %d %d %d %d" %
                              tuple([get_setting("active_ch%d" % i)
                                     for i in range(4)]))
            self.logger.debug("Got coincidence configurations: %d %d %d %d" %
                              tuple([get_setting("coincidence%d" % i)
                                     for i in range(4)]))
            self.logger.debug("Got veto configurations: %d %d %d %d" %
                              tuple([get_setting("veto")] +
                                    [get_setting("veto_ch%d" % i)
                                     for i in range(3)]))

            return True
        else:
            self.logger.debug("Was not able to interprete:\n%s"%msg)
            return False

    def get_threshold_from_card(self):
                """
        Explicitly scan message for threshold information.

        Return True if found, False otherwise.

        :param msg: daq message
        :type msg: str
        :returns: bool
        """
        if msg.startswith('TL') and len(msg) > 9:
            msg = msg.split('=')
            update_setting("threshold_ch0", int(msg[1][:-2]))
            update_setting("threshold_ch1", int(msg[2][:-2]))
            update_setting("threshold_ch2", int(msg[3][:-2]))
            update_setting("threshold_ch3", int(msg[4]))
            self.logger.debug("Got Thresholds %d %d %d %d" %
                              tuple([get_setting("threshold_ch%d" % i)
                                     for i in range(4)]))
            return True
        else:
            self.logger.debug("Was not able to interprete:\n%s"%msg)
            return False
