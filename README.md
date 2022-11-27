# pyLoconet

Python implementation of Digitrax Loconet bus protocol

Derived from Arduino [Loconet] library.

Main Python file is [pyLoconet.py] witch contain the base class for Loconet decode and manipolation.
As the original Arduino lib version, it hereditate callbacks notify methodology. A specific class implementation for throttle management is availble in [pyLoconetThrottle.py].

Phisical communication is performed via serial UART/USB protocol, thanks to python [pyserial] lib. Phisical hardware gateway is an Arduino [LocoLinx]/[LocoLinx32U4] or a Loconet [LocoBuffer], connected via RS232/USB.

Python side the communication is in charge of a [lnCom.py], where the main class is instanciated by the main LoconetClass in a secondary thread.

User side it is required to ovveride the default class LoconetClass or the throttle one LoconetThrottleClass, with your own. Inside your class you need to override "your_custome_code" method, entering all your required code there, and all callbacks "notify" methods that are required by your code. As "main" code you need only to instanciate you own class that override loconet default and simply call "run()" method. See [lnSensorMonitor.py] and [lnThrottleMonitor.py] for further info.

[Loconet]: https://github.com/mrrwa/LocoNet
[pyLoconet.py]: .../../pyLoconet.py
[pyLoconetThrottle.py]: .../../pyLoconetThrottle.py
[pyserial]: https://pypi.org/project/pyserial
[LocoLinx]: https://github.com/mrrwa/LocoNet/tree/master/examples/LocoLinx
[LocoLinx32U4]: https://github.com/mrrwa/LocoNet/tree/master/examples/LocoLinx32U4
[LocoBuffer]: http://www.locobuffer.com
[lnCom.py]: .../../lnCom.py
[lnSensorMonitor.py]: .../../lnSensorMonitor.py
[lnThrottleMonitor.py]: .../../lnThrottleMonitor.py
