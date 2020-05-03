"""
Provide a connection to the QNet DAQ cards via python-serial. For software
testing and development, (very) dumb DAQ card simulator is available.
"""

# import the needed self written exceptions
from .exceptions import DAQIOError, DAQMissingDependencyError

# import the q-net card object
from .qnetcard import QnetCard

__all__ = ["exceptions", "qnetcard"]
