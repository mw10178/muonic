# Muonic - QT5 Upgrade

Benjamin Bastian-Querner, 03.05.2020 

### Aim of the Upgrade

The graphical user interface (GUI) of the current software runs with pyqt4. It was decided to migrate muonic to run with pyqt5.

### Problems by the migration

The current software architecture of [release number 2](https://github.com/CosmicLabDESY/muonic/tree/release2/) does not allow a simple migration to QT5. The ``muonic.gui.application.Application`` run by ``<path to muonic>/muonic.py`` does the data collection from the QnetDAQcard as well as it's configuration. The defined functions to make measurements and analyses of the data, manage the QT-Widgets of the GUI, as well. As QT5 has changed some of its syntaxes, a replacement of the lines with the new functions are not possible. The architecture of the program does not allow us to understand side-effects without a reverse-engineering of the complete software.  The comments do not provide any information about the motivation for these structures. Most of the algorithms are not explained by the comments and must be understood from the code. As the functions in ``muonic.gui.application.Application`` manage multiple program-layers, the algorithms for different layers are mixed. The used programming paradigm is chosen to be object-oriented in its syntax, but the structure of the program is often chosen to be "pragmatic". Sometimes a self made inheritance is used like allocating an attribute called "parent" mixed with python's inheritance (see ``muonic.gui.widgets.BaseWidget``). The "parent" is passed as an argument to this class during it's initialization. Without comments / motivation for this it is in-transparent which class is actually inherited.

### Chosen solution

The software architecture needs to be re-designed. It is important to introduce different layers which combine abstract entities like:

* Subclass for communication with the QnetDAQcard
  * Subsubclass for low level API (available from release2)
  * Subsubclass or function for sorting the received strings as settings information and raw data 
  * Subsubclass for managing and storing the settings of the card
* Subclass for analyses/interpretation of raw data 
* Subclass for the measurements
  * Subsubclass for the measurement algorithms
  * Subsubclass for the analyses of the raw data in terms of the measurements
* (optional) Subclass for plotting which provides a suitable visualization of the data with ``matplotlib`` without GUI
* An overall class which gets inherited all this classes 

All subclasses shall be inherited such that the overall class has all the functionalities the user needs. The method must be importable to allow writing individual measurement scripts with the hardware to extend the functionality beyond the implemented measurement scripts. In the case of release 2, an extension was only possible by hacking the software to get the needed data from the background. 
After the muonic program runs with all its functionality without GUI, the GUI can be set on the top. This will allow to use different kinds of GUI implementations.

### Incomplete overview of the program structure release2

* ``muonic.py`` runs ``muonic.gui.application.Application`` (the overall program)
  * ``muonic.analysis.PulseExtractor`` (Class to analyze the pulse-data)
    * ``muonic.util``
  * ``muonic.daq.exceptions`` (Self made exceptions)
  * ``muonic.gui.dialogs`` (Dialogs/windows of the GUI)
  * ``muonic.gui.widgets`` (Widgets for the windows, some of the analyses might be done here, as well as, the low-level communication with the card)
    * ``muonic.daq.provider`` (Provides a socket client and a class which uses multiprocessing to run the deamon from ``connection`` in a seperated thread.)
      * ``muonic.daq.connection`` (Provides a zmq-socket-server and a daemon. Both work with a serial connection.)
    * ``muonic.gui.helpers`` 
    * ``muonic.gui.plot_canvases``
    * ``muonic.gui.dialogs``
    * ``muonic.analysis``
    * ``muonic.util`` 
  * ``muonic.util`` (Some functions e.g. to create folders and manage their permissions)

The ``muonic.py`` runs the ``Application`` method. ``Application`` imports the ``PulseExtractor``, ``Exceptions``, ``Dialogs``, and the ``widgets``. The ``PulseExtractor`` seems to do the raw-data analysis. The ``Dialogs`` are the windows itself, hardcoded. The ``widgets`` are the different sub-routines, which do the analysis and the visualization. The measurement algorithms are coded in the different ``widgets`` and the communication with the QnetDAQCard is done in a low-level manner with the ``Provider``. That means the string commands are hardcoded in the ``widgets``. The different ``widgets`` are doing the multiprocessing.
Furthermore it is not clear, why there are two implementations of daemons (multiprocessing daemon and the socket-server) to communicate with the card. Both can be chosen from the user, but only one is needed.

### Overview of the new package muonicPro ([``develop2``](https://github.com/CosmicLabDESY/muonic/tree/develop2))

Migration to python3 is mostly done.

- ``muonic.muonicPro``

  - ``muonic.daq.QnetCard``

    Thread1 (Hardware near communication), Thread2 (distributor of messages from queue in Thread1)

    - ``muonic.daq.api.Provider``  (Thread1)
    - ``muonic.analysis.distributor`` (Thread2) (A daemon to distribute the messages from the low-level communication. Belong this message to settings or to data.) 
    - ``muonic.daq.api.DAQClient``
    - ``muonic.daq.QnetCardSettings`` (Provides functions to set up the card, the low level commands shall be coded here and provide, functionality such that the user, does not need to look at the command table. It also manages the settings-storage in the background. If a setting is changed on the card for some reason it sends the new configuration. This will be passed into a queue in Thread1. A second thread Thread2 classifies the msg as a settings information and will update the settings-variable.)

  - ``muonic.analyses.<class>``:
    Depending on the needed analyses, most likely the ``PulseExtractor`` can be recycled here, a class is needed to interpret the data messages passed from the distributor thread Thread2. There is also GPS, temperature, and pressure data, which needs to be interpreted.

  - ``muonic.measurements.<class>``:

    Classes for different measurements like velocity, decay, and rate measurements. Every measurement needs to start it's own threat with multiprocessing.

In ``develop2`` there are now two modules. The "old one" muonic and this new one muonicPro. Both can be imported into pyhton3. The scripts in muonic have a bit more comments now. So if you wish to understand / reverse-engineer the old code use these scripts. The muonic program should still run with this comment, to python3 migrated code.

### Things needs to be done:

- The distributer daemon must be written. To start with this one has to understand all the possible outcome of the card and find criteria to distribute the different messages. 
- Heritage. The classes are not properly inherited, such that the upper class has got the "inherited" class as attribute, which was copied from the former version, but in-transparent. Please make sure that the individual threads are not initialized two times. That means proper inheritance will not be possible every time.
- It could be that the QnetCardSettings get its own thread, which get filled its queue from the distributer. An other option would be, that the distributer get the QnetCardSettings inheritated and calls the needed functions. This could blow up this class.
- Same for the pulse analyzing.
- Measurements needs to be written. (It is not recommended to reverse engineer the algorithms from ``release2``, as the measurements are described in the manuals.)
- Maybe a plotting class to provide visualization with ``matplotlib``. Could also be done with multiprocessing.
- Generating the new QT5-based GUI with the Graphical-IDE ``Qt Designer``. 
  [QT5 docs](https://doc.qt.io/qt-5/qtgui-index.html) [QT Designer](https://doc.qt.io/qt-5/qtdesigner-manual.html)
  - There is already a .ui file created by a collogue. Ask who. It might only be finished/modified.
- Building an upper layer for muonicPro, which connects the functionality of the stand-alone method with the GUI.

### The Idea of a web-based muonic

The advantage is that it could run platform independent without installation. If there is a new version available, the user does not need to worry. 
**Problems**:

- The Web-Browser needs access to the usb-ports and must send the messages to the server, which uses this as input. It is not clear, how the varying ping time affect the measurements. How the web-browser can have access to the usb-ports seems to me a non-trivial problem.
- There is no template for the GUI as it already exists for QT5.
- The server needs to provide python-sessions for different clients. If the data stream of some hundred students around the world could lower the systems speed in a manner, that it might effect the measurements, because timing resolution is important. It is not clear yet for me if the system time is used in the data analyzing part.
- What happens, if the connection is unstable for some milliseconds in a measurement which takes days? What is likely. Sub-routines must be implemented to catch that.

**Advantages by using the local machine**:

- No ping.
- No problem with resources.
- Stable connection over days.

The current way of installation is installing all dependencies like qt and the needed python packages, making a copy of the repository, and running setup.py. The is no automatized way for making updates. 
My suggestion is to go a step further and generate a python package, which can be provided by Pip. If one has a module like the above software (a folder with the scripts and a file called ``__init__.py``, it was called a package here but is only a module), creating a package for pip is straight forward  and explained here: [Packaging](https://packaging.python.org/).
It would also allow to install the dependencies and versioning, as well as doing updates with pip.
Everything the user would have to do is:

```python
pip3 install muonic
```

If python3 and its pip is installed. 

From my side I would suggest to finish the current update project to qt5, because I expect that there are no already solved problems, so far.