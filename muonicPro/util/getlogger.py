

def get_configured_logger()
    '''
    A function that provides the configuration for the logging object.
    '''
    import logging
    
    formatter = logging.Formatter("%(levelname)s:%(process)d:%(module)s:" +
                                    "%(funcName)s:%(lineno)d:%(message)s")
    ch = logging.StreamHandler()
    ch.setLevel(logging.DEBUG if verbose else logging.INFO)
    ch.setFormatter(formatter)

    logger = logging.getLogger()
    logger.setLevel(logging.DEBUG if verbose else logging.INFO)
    logger.addHandler(ch)
    return logger