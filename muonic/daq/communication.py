



class communication():
    '''
    Quarknet Scintillator Card,  Qnet2.5  Vers 1.12  Compiled Sep 10 2014  HE=Help
    Serial#=6901     uC_Volts=3.32      GPS_TempC=0.0     mBar=1113.1

    CE     - TMC Counter Enable.
    CD     - TMC Counter Disable.
    DC     - Display Control Registers, (C0-C3).
    WC a d - Write   Control Registers, addr(0-6) data byte(H).
    DT     - Display TMC Reg, 0-3, (1=PipeLineDelayRd, 2=PipeLineDelayWr).
    WT a d - Write   TMC Reg, addr(1,2) data byte(H), if a=4 write delay word.
    DG     - Display GPS Info, Date, Time, Position and Status.
    DS     - Display Scalar, channel(S0-S3), trigger(S4), time(S5).
    RE     - Reset complete board to power up defaults.
    RB     - Reset only the TMC and Counters.
    SB p d - Set Baud,password, 1=19K, 2=38K, 3=57K ,4=115K, 5=230K, 6=460K, 7=920K
    SA n   - Save setup, 0=(TMC disable), 1=(TMC enable), 2=(Restore Defaults).
    TH     - Thermometer data display (@ GPS), -40 to 99 degrees C.
    TL c d - Threshold Level, signal ch(0-3)(4=setAll), data(0-4095mV), TL=read.
    Veto   - Veto select, Off='VE 0', On='VE 1', Gate='VG c', 0-255(D) 10ns/cnt.
    View   - View setup registers. Setup=V1, Voltages(V2), GPS LOCK(V3).
    HELP   - HE,H1=Page1, H2=Page2, HB=Barometer, HS=Status, HT=Trigger.
    Barometer      Qnet Help Page 2
    BA     - Display Barometer trim setting in mVolts and pressure as mBar.
    BA d   - Calibrate Barometer by adj. trim DAC ch in mVlts (0-4095mV).
    Flash
    FL p   - Load Flash with Altera binary file(*.rbf), p=password.
    FR     - Read FPGA setup flash, display sumcheck.
    FMR p  - Read page 0-3FF(h), (264 bytes/page)
    Page 100h= start fpga *.rbf file, page 0=saved setup.
    GPS
    NA 0   - Append NMEA GPS data Off,(include 1pps data).
    NA 1   - Append NMEA GPS data On, (Adds GPS to output).
    NA 2   - Append NMEA GPS data Off, no 1pps data,GPS needed for ST Line timing.
    NM 0   - NMEA GPS display, Off, (default), GPS port speed 38400, locked.
    NM 1   - NMEA GPS display (RMC + GGA + GSV) data.
    NM 2   - NMEA GPS display (ALL) data, use with GPS display applications.
    Test Pulser
    TE m   - Enable run mode,  0=Off, 1=One cycle, 2=Continuous.
    TD m   - Load sample trigger data list, 0=Reset, 1=Singles, 2=Majority.
    TV m   - Voltage level at pulse DAC, 0-4095mV, TV=read.
    Serial #
    SN p n - Store serial # to flash, p=password, n=(0-65535 BCD).
    SN     - Display serial number (BCD).
    Status
    ST     - Send status line now.  This resets the minute timer.
    ST 0   - Status line, disabled.
    ST 1 m - Send status line every (m) minutes.(m=1-30, def=5).
    ST 2 m - Include scalar data line, chs S0-S4 after each status line.
    ST 3 m - Include scalar data line, plus reset counters on each timeout.
    TI n    - Timer (day hr:min:sec.msec), TI=display time, (TI n=0 clear).
    U1 n    - Display Uart error counter, (U1 n=0 to zero counters).
    VM 1    - View mode, 0x80=Event_Demarcation_Bit outputs a blank line.
    - View mode returns to normal after 'CD','CE','ST' or 'RE'.
    '''
    def __init__(daq, logger):
        self.daq = daq

    def help_com(self, print=False):
        '''
        Help containing a list of all ASCII commands for the DAQ Card.
        print: bool
            if True help-string is plotted
        Returns help string
        '''
        str = 'Quarknet Scintillator Card,  Qnet2.5  Vers 1.12  Compiled Sep 10 2014  HE=Help\n\\
            Serial#=6901     uC_Volts=3.32      GPS_TempC=0.0     mBar=1113.1\n\\
            \n\\
            CE     - TMC Counter Enable.\n\\
            CD     - TMC Counter Disable.\n\\
            DC     - Display Control Registers, (C0-C3).\n\\
            WC a d - Write   Control Registers, addr(0-6) data byte(H).\n\\
            DT     - Display TMC Reg, 0-3, (1=PipeLineDelayRd, 2=PipeLineDelayWr).\n\\
            WT a d - Write   TMC Reg, addr(1,2) data byte(H), if a=4 write delay word.\n\\
            DG     - Display GPS Info, Date, Time, Position and Status.\n\\
            DS     - Display Scalar, channel(S0-S3), trigger(S4), time(S5).\n\\
            RE     - Reset complete board to power up defaults.\n\\
            RB     - Reset only the TMC and Counters.\n\\
            SB p d - Set Baud,password, 1=19K, 2=38K, 3=57K ,4=115K, 5=230K, 6=460K, 7=920K\n\\
            SA n   - Save setup, 0=(TMC disable), 1=(TMC enable), 2=(Restore Defaults).\n\\
            TH     - Thermometer data display (@ GPS), -40 to 99 degrees C.\n\\
            TL c d - Threshold Level, signal ch(0-3)(4=setAll), data(0-4095mV), TL=read.\n\\
            Veto   - Veto select, Off="VE 0", On="VE 1", Gate="VG c", 0-255(D) 10ns/cnt.\n\\
            View   - View setup registers. Setup=V1, Voltages(V2), GPS LOCK(V3).\n\\
            HELP   - HE,H1=Page1, H2=Page2, HB=Barometer, HS=Status, HT=Trigger.\n\\
            Barometer      Qnet Help Page 2\n\\
            BA     - Display Barometer trim setting in mVolts and pressure as mBar.\n\\
            BA d   - Calibrate Barometer by adj. trim DAC ch in mVlts (0-4095mV).\n\\
            Flash\n\\
            FL p   - Load Flash with Altera binary file(*.rbf), p=password.\n\\
            FR     - Read FPGA setup flash, display sumcheck.\n\\
            FMR p  - Read page 0-3FF(h), (264 bytes/page)\n\\
            Page 100h= start fpga *.rbf file, page 0=saved setup.\n\\
            GPS\n\\
            NA 0   - Append NMEA GPS data Off,(include 1pps data).\n\\
            NA 1   - Append NMEA GPS data On, (Adds GPS to output).\n\\
            NA 2   - Append NMEA GPS data Off, no 1pps data,GPS needed for ST Line timing.\n\\
            NM 0   - NMEA GPS display, Off, (default), GPS port speed 38400, locked.\n\\
            NM 1   - NMEA GPS display (RMC + GGA + GSV) data.\n\\
            NM 2   - NMEA GPS display (ALL) data, use with GPS display applications.\n\\
            Test Pulser\n\\
            TE m   - Enable run mode,  0=Off, 1=One cycle, 2=Continuous.\n\\
            TD m   - Load sample trigger data list, 0=Reset, 1=Singles, 2=Majority.\n\\
            TV m   - Voltage level at pulse DAC, 0-4095mV, TV=read.\n\\
            Serial #\n\\
            SN p n - Store serial # to flash, p=password, n=(0-65535 BCD).\n\\
            SN     - Display serial number (BCD).\n\\
            Status\n\\
            ST     - Send status line now.  This resets the minute timer.\n\\
            ST 0   - Status line, disabled.\n\\
            ST 1 m - Send status line every (m) minutes.(m=1-30, def=5).\n\\
            ST 2 m - Include scalar data line, chs S0-S4 after each status line.\n\\
            ST 3 m - Include scalar data line, plus reset counters on each timeout.\n\\
            TI n    - Timer (day hr:min:sec.msec), TI=display time, (TI n=0 clear).\n\\
            U1 n    - Display Uart error counter, (U1 n=0 to zero counters).\n\\
            VM 1    - View mode, 0x80=Event_Demarcation_Bit outputs a blank line.\n\\
            - View mode returns to normal after "CD","CE","ST" or "RE".\n'
        print(str)
        return str

    def disable_status_reporting(self):
        '''
        Disable status reporting
        '''
        self.daq.put('ST 0')

    def enable_status_reporting(self, scalar_data=False, reset_counter=False):
        '''
        Show status line: channels & coincidence.
        Important: run this command for each data session.
        '''

        if (scalar_data and reset_counter) or reset_counter:
            msg = 'ST 3'
        elif scalar_data:
            msg = 'ST 2'
        else:
            msg = 'ST 1'
        self.daq.put(msg)

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

            update_setting("gate_width", int(coincidence_time, 16) * 10)

            # set default veto config
            for i in range(4):
                if i == 0:
                    update_setting("veto", True)
                else:
                    update_setting("veto_ch%d" % (i - 1), False)

            # update channel config
            for i in range(4):
                update_setting("active_ch%d" % i,
                               channel_config[3 - i] == '1')

            # update coincidence config
            for i, seq in enumerate(['00', '01', '10', '11']):
                update_setting("coincidence%d" % i,
                               coincidence_config == seq)

            # update veto config
            for i, seq in enumerate(['00', '01', '10', '11']):
                if veto_config == seq:
                    if i == 0:
                        update_setting("veto", False)
                    else:
                        update_setting("veto_ch%d" % (i - 1), True)

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
