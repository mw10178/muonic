from .provider import DAQClient, DAQProvider
import logging

class DAQCard():
    '''
    DAQCard object class for communication with
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

    _help_str = 'Quarknet Scintillator Card,  Qnet2.5  Vers 1.12  Compiled Sep 10 2014  HE=Help\n\\
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

    def __init__(daq=None, logger=None, port=None, sim=False, verbose=False):
        if logger is None:
            # set up logging
            formatter = logging.Formatter("%(levelname)s:%(process)d:%(module)s:" +
                                          "%(funcName)s:%(lineno)d:%(message)s")
            ch = logging.StreamHandler()
            ch.setLevel(logging.DEBUG if verbose else logging.INFO)
            ch.setFormatter(formatter)

            logger = logging.getLogger()
            logger.setLevel(logging.DEBUG if verbose else logging.INFO)
            logger.addHandler(ch)
        self.logger = logger

        if daq is not None:
            self.daq = daq
        elif port is not None and not sim:
            self.daq = DAQClient(port=port, logger=logger)
            logger.info('Client with zmq socket has started.\n\\
                with port %s'%port)
        else:
            self.daq = DAQProvider(sim=sim, logger=logger)
            if sim and port is not None:
                logger.info('Client with zmq does not support a simulation.\n\\
                    Provider with with multiprocessing.Queue \n\\
                    has started instead.')
            else:
                logger.info('Provider with with multiprocessing.Queue \n\\
                    has started.')

    def help_com(self, print=False):
        '''
        Help containing a list of all ASCII commands for the DAQ Card.
        print: bool
            if True help-string is plotted
        Returns help string
        '''

        print(self._help_str)
        return self._help_str
