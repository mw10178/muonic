from .qnetcard import QnetCard
import muonic
import os
import logging

class MuonicPro():
    def __init__(self, daq=None, logger=None, port=None, sim=False, verbose=False):
        # set loggger
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
        # define path to save files and
        # generate folder if data folder is not created
        self.path_to_save_data = muonic.DATA_PATH
        self.path_to_save_settings = self.path_to_save_data+'/settings'
        for p in [self.path_to_save_data, self.path_to_save_settings]:
            if not os.path.isdir(p):
                self.logger.info('Did not found muonic\'s ' + p.split('/')[-1] +
                                    ' folder.')
                os.mkdir(p)
                self.logger.info('Created: %s'%p)

        # start communication with Qnet Card
        self.qnetcard = QnetCard(path_to_save=self.path_to_save_settings,
                daq=daq, logger=self.logger, port=port, sim=sim, verbose=verbose)
