
from pyLoconet import LoconetClass as Loconet

# edit these define and adapt to your system
# ready to use with LocoBuffer or Arduino LocoLinx
COM_PORT = 'COM1'
COM_BAUD = 57600


class MyLoconet(Loconet):
    def __init__(self, port):
        self.counter = 0
        Loconet.__init__(self, port)

    # all 'notify' below are callbacks overrides from LoconetClass
    def notify_power(self, state):
        print("### Power: %s" % ("ON" if state else "OFF"))

    def notify_sensor(self, address, state):
        print("### Sensor %s: %s" % (str(address), "ON" if state else "OFF"))

    def notify_switch_state(self, address, output, direction):
        print("### Switch %s, output %s, dirction %s" %
              (str(address), "ON" if output else "OFF", "RIGHT" if direction else "LEFT"))

    def notify_multisense_transponder(self, address, zone, loco, present):
        address = int((address + 1) / 2)
        print("### Multisense: %s of loco %s in zone %s.%s" %
              ("PRESENCE" if present else "ABSENCE", str(loco), str(address), zone))

    def your_custom_code(self, packet, flag):
        # here you can put your code, this function is called every 'cycle_delay' seconds inside process loop 'ln.run()'
		# loconet receiver/transmitter is not affected by this define because it is managed in a secondary thread
        print("PACKET:", hex(packet) if packet is not None else "None", "..." if flag else "...not", "processed")
        print("This example code auto end the process after 100 cycles, actual %s/100 ..." % self.counter)
        self.counter += 1
        # check if 100th cycle elapsed
        if self.counter > 100:
            # remember to call 'close()' function to end the loop process safely exiting from 'ln.run()' and closing loconet tranceiver
            self.close()

    def start(self):
        # this function is called one time at the end of 'MyLoconet' init function, when loconet interface is ready
		# remenber to define your preferred 'cicle time' here, it can be modified when as your prefear in 'your_custom_code' function
        self.cycle_delay = 0.5
        print("### START LOCONET ###")

    def stop(self):
        # this function is called one time when you exit from 'ln.run()'
        print("### STOP LOCONET ###")


input("This example explain simply how to use pyLoconet\nPress any key to start...")
# pass COM port name and baudrate to the class
ln = MyLoconet([COM_PORT, COM_BAUD])
# call to loop loconet process
ln.run()
