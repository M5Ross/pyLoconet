
from pyLoconetThrottle import LoconetThrottleClass as LoconetThrottle

# edit these define and adapt to your system
COM_PORT = 'COM1'
COM_BAUD = 57600


class MyThrottle(LoconetThrottle):
    def __init__(self, Options, ThrottleId, Port):
        LoconetThrottle.__init__(self, Options, ThrottleId, Port)

    def notifyThrottleAddress(self, State, Address, Slot):
        pass

    def notifyThrottleSpeed(self, State, Speed):
        pass

    def notifyThrottleDirection(self, State, Direction):
        pass

    def notifyThrottleFunction(self, Function, Value):
        pass

    def notifyThrottleSlotStatus(self, Status):
        pass

    def notifyThrottleError(self, Error):
        pass

    def notifyThrottleState(self, PrevState, State):
        pass

    def start(self):
        print("### START LOCONET THROTTLE ###")

    def stop(self):
        print("### STOP LOCONET THROTTLE ###")

    def your_custom_code(self):
        print("put here you code...")


input("loconet throttle template\nPress any key to start...")

lnThr = MyThrottle(0, 1, [COM_PORT, COM_BAUD])
lnThr.run()
