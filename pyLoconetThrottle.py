import threading
import lnOpc as Opc
from pyLoconet import LoconetClass as Loconet

STAT1_SL_SPURGE = 0x80  # internal use only, not seen on net
STAT1_SL_CONUP = 0x40  # consist status
STAT1_SL_BUSY = 0x20  # used with STAT1_SL_ACTIVE
STAT1_SL_ACTIVE = 0x10
STAT1_SL_CONDN = 0x08
STAT1_SL_SPDEX = 0x04
STAT1_SL_SPD14 = 0x02
STAT1_SL_SPD28 = 0x01
STAT2_SL_SUPPRESS = 0x01  # 1 = Adv. Consisting supressed
STAT2_SL_NOT_ID = 0x04  # 1 = ID1/ID2 is not ID usage
STAT2_SL_NOTENCOD = 0x08  # 1 = ID1/ID2 is not encoded alias
STAT2_ALIAS_MASK = (STAT2_SL_NOTENCOD | STAT2_SL_NOT_ID)
STAT2_ID_IS_ALIAS = STAT2_SL_NOT_ID

# mask and values for consist determination
CONSIST_MASK = (STAT1_SL_CONDN | STAT1_SL_CONUP)
CONSIST_MID = (STAT1_SL_CONDN | STAT1_SL_CONUP)
CONSIST_TOP = STAT1_SL_CONDN
CONSIST_SUB = STAT1_SL_CONUP
CONSIST_NO = 0


def CONSIST_STAT(s):
    if (s & CONSIST_MASK) == CONSIST_MID:
        return "Mid-Consisted"
    elif (s & CONSIST_MASK) == CONSIST_MID:
        return "Consist TOP"
    elif (s & CONSIST_MASK) == CONSIST_SUB:
        return "Sub-Consisted"
    else:
        return "Not Consisted"


def CONSISTED(s):
    if (s & CONSIST_MASK) == CONSIST_MID or (s & CONSIST_MASK) == CONSIST_SUB:
        return True
    else:
        return False


# mask and values for locomotive use determination
LOCOSTAT_MASK = (STAT1_SL_BUSY | STAT1_SL_ACTIVE)
LOCO_IN_USE = (STAT1_SL_BUSY | STAT1_SL_ACTIVE)
LOCO_IDLE = STAT1_SL_BUSY
LOCO_COMMON = STAT1_SL_ACTIVE
LOCO_FREE = 0


def LOCO_STAT(s):
    if (s & LOCOSTAT_MASK) == LOCO_IN_USE:
        return "In-Use"
    elif (s & LOCOSTAT_MASK) == LOCO_IDLE:
        return "Idle"
    elif (s & LOCOSTAT_MASK) == LOCO_COMMON:
        return "Common"
    else:
        return "Free"


# mask and values for decoder type encoding for this slot
DEC_MODE_MASK = (STAT1_SL_SPDEX | STAT1_SL_SPD14 | STAT1_SL_SPD28)
# Advanced consisting allowed for the next two
DEC_MODE_128A = (STAT1_SL_SPDEX | STAT1_SL_SPD14 | STAT1_SL_SPD28)
DEC_MODE_28A = STAT1_SL_SPDEX
# normal modes
DEC_MODE_128 = (STAT1_SL_SPD14 | STAT1_SL_SPD28)
DEC_MODE_14 = STAT1_SL_SPD14
DEC_MODE_28TRI = STAT1_SL_SPD28
DEC_MODE_28 = 0


def DEC_MODE(s):
    if (s & DEC_MODE_MASK) == DEC_MODE_128A:
        return "128 (Allow Adv. consisting)"
    elif (s & DEC_MODE_MASK) == DEC_MODE_28A:
        return "28 (Allow Adv. consisting)"
    elif (s & DEC_MODE_MASK) == DEC_MODE_128:
        return "128"
    elif (s & DEC_MODE_MASK) == DEC_MODE_14:
        return "14"
    elif (s & DEC_MODE_MASK) == DEC_MODE_28TRI:
        return "28 (Motorola)"
    else:
        return "28"


# values for track status encoding for this slot
GTRK_PROG_BUSY = 0x08  # 1 = programming track in this master is Busy
GTRK_MLOK1 = 0x04  # 0 = Master is DT200, 1=Master implements LocoNet 1.1
GTRK_IDLE = 0x02  # 0 = Track paused, B'cast EMERG STOP, 1 = Power On
GTRK_POWER = 0x01

FC_SLOT = 0x7b  # Fast clock is in this slot
PRG_SLOT = 0x7c  # This slot communicates with the programming track

# values and macros to decode programming messages
PCMD_RW = 0x40  # 1 = write, 0 = read
PCMD_BYTE_MODE = 0x20  # 1 = byte operation, 0 = bit operation (if possible)
PCMD_TY1 = 0x10  # TY1 Programming type select bit
PCMD_TY0 = 0x08  # TY0 Programming type select bit
PCMD_OPS_MODE = 0x04  # 1 = Ops mode, 0 = Service Mode
PCMD_RSVRD1 = 0x02  # reserved
PCMD_RSVRD0 = 0x01  # reserved

# programming mode mask
PCMD_MODE_MASK = (PCMD_BYTE_MODE | PCMD_OPS_MODE | PCMD_TY1 | PCMD_TY0)

# programming modes
# Paged mode  byte R/W on Service Track
PAGED_ON_SRVC_TRK = PCMD_BYTE_MODE

# Direct mode byte R/W on Service Track
DIR_BYTE_ON_SRVC_TRK = (PCMD_BYTE_MODE | PCMD_TY0)

# Direct mode bit  R/W on Service Track
DIR_BIT_ON_SRVC_TRK = PCMD_TY0

# Physical Register byte R/W on Service Track
REG_BYTE_RW_ON_SRVC_TRK = PCMD_TY1

# Service Track Reserved function
SRVC_TRK_RESERVED = (PCMD_TY1 | PCMD_TY0)

# Ops mode byte program - no feedback
OPS_BYTE_NO_FEEDBACK = (PCMD_BYTE_MODE | PCMD_OPS_MODE)

# Ops mode byte program - feedback
OPS_BYTE_FEEDBACK = (OPS_BYTE_NO_FEEDBACK | PCMD_TY0)

# Ops mode bit program - no feedback
OPS_BIT_NO_FEEDBACK = PCMD_OPS_MODE

# Ops mode bit program - feedback
OPS_BIT_FEEDBACK = (OPS_BIT_NO_FEEDBACK | PCMD_TY0)

# Programmer Status error flags
PSTAT_USER_ABORTED = 0x08  # User aborted this command
PSTAT_READ_FAIL = 0x04  # Failed to detect Read Compare Acknowledge from decoder
PSTAT_WRITE_FAIL = 0x02  # No Write acknowledge from decoder
PSTAT_NO_DECODER = 0x01  # Service mode programming track empty

# bit masks for CVH */
CVH_CV8_CV9 = 0x30  # mask for CV# bits 8 and 9
CVH_CV7 = 0x01  # mask for CV# bit 7
CVH_D7 = 0x02  # MSbit for data value


# build data byte from programmer message
def PROG_DATA(ptr):
    return ((ptr.cvh & CVH_D7) << 6) | (ptr.data7 & 0x7f)


# build CV # from programmer message
def PROG_CV_NUM(ptr):
    return ((((ptr.cvh & CVH_CV8_CV9) >> 3) | (ptr.cvh & CVH_CV7)) * 128) + (ptr.cvl & 0x7f)


SLOT_REFRESH_TICKS = 600  # 600 * 100ms = 60 seconds between speed refresh
TH_OP_DEFERRED_SPEED = 0x01

# LocoNet Throttle Support

# TH_STATE
TH_ST_FREE = 0
TH_ST_ACQUIRE = 1
TH_ST_SELECT = 2
TH_ST_DISPATCH = 3
TH_ST_SLOT_MOVE = 4
TH_ST_SLOT_FREE = 5
TH_ST_SLOT_RESUME = 6
TH_ST_SLOT_STEAL = 7
TH_ST_IN_USE = 8

# TH_ERROR
TH_ER_OK = 0
TH_ER_SLOT_IN_USE = 1
TH_ER_BUSY = 2
TH_ER_NOT_SELECTED = 3
TH_ER_NO_LOCO = 4
TH_ER_NO_SLOTS = 5


class LoconetThrottleClass:
    def __init__(self, Options, ThrottleId, Port):

        self.myState = 0  # State of throttle
        self.myTicksSinceLastAction = 0
        self.myThrottleId = 0  # Id of throttle
        self.mySlot = 0  # Master Slot index
        self.myAddress = 0  # Decoder Address
        self.mySpeed = 0  # Loco Speed
        self.myDeferredSpeed = 0  # Deferred Loco Speed setting
        self.myStatus1 = 0  # Stat1
        self.myDirFunc0to4 = 0  # Direction
        self.myFunc5to8 = 0  # Function

        self.myFunc9to12 = 0  # Function
        self.myFunc13to20 = 0  # Function
        self.myFunc21to28 = 0  # Function

        self.myUserData = 0
        self.myOptions = 0
        self.myLastTimerMillis = 0

        # redefinitions
        self.myState = TH_ST_FREE
        self.myThrottleId = ThrottleId
        self.myDeferredSpeed = 0
        self.myOptions = Options

        self.alive = threading.Event()
        self.thread = threading.Thread(target=self.process100ms)
        self.thread.setDaemon(True)

        # open loconet communication
        self.LocoNet = Loconet(Port)

        self.cicle_delay = 0.1
        self.exit = False

    def start(self):
        pass

    def stop(self):
        pass

    def close(self):
        self.stop()
        self.exit = True
        self.alive.clear()
        self.thread.join(5)
        self.LocoNet.delay(self.cicle_delay)
        self.LocoNet.close()

    def run(self):
        self.alive.set()
        self.thread.start()
        while True:
            packet = self.LocoNet.receive()
            if packet is not None:
                print("PACKET:", hex(packet))
                if not self.LocoNet.process_switch_sensor_message(packet):
                    self.processMessage(packet)
            self.your_custom_code()
            self.LocoNet.delay(self.cicle_delay)
            if self.exit:
                break

    def set_custom_cicle_delay(self, seconds):
        self.cicle_delay = seconds

    def your_custom_code(self):
        pass

    def process100ms(self):
        while self.alive.isSet():
            self.LocoNet.delay(0.1)
            if self.myState == TH_ST_IN_USE:
                self.myTicksSinceLastAction += 1
                if self.myDeferredSpeed or self.myTicksSinceLastAction > SLOT_REFRESH_TICKS:
                    self.LocoNet.send_2byte(Opc.LOCO_SPD,
                                            self.mySlot,
                                            self.myDeferredSpeed if self.myDeferredSpeed else self.mySpeed)
                    self.myDeferredSpeed = 0
                    self.myTicksSinceLastAction = 0

    def processMessage(self, ln_packet):
        LnPacket = Opc.Msg(ln_packet)
        consumed_flag = True

        # Update our copy of slot information if applicable
        if LnPacket.sd.command == Opc.SL_RD_DATA:
            SlotAddress = (LnPacket.sd.adr2 << 7) + LnPacket.sd.adr

            if self.mySlot == LnPacket.sd.slot:
                # Make sure that the slot address matches even though we have the right slot number
                # as it is possible that another throttle got in before us and took our slot.
                if self.myAddress == SlotAddress:
                    if self.myState == TH_ST_SLOT_RESUME and self.myThrottleId != (
                            (LnPacket.sd.id2 << 7) + LnPacket.sd.id1):
                        self.updateState(TH_ST_FREE, 1)
                        self.notifyThrottleError(TH_ER_NO_LOCO)
                        consumed_flag = False
                    else:
                        self.updateState(TH_ST_IN_USE, 1)
                        self.updateAddress(SlotAddress, 1)
                        self.updateSpeed(LnPacket.sd.spd, 1)
                        self.updateDirectionAndFunctions(LnPacket.sd.dirf, 1)
                        self.updateFunctions5to8(LnPacket.sd.snd, 1)
                        self.updateStatus1(LnPacket.sd.stat, 1)

                        # force function update
                        self.updateFunctions9to12(0, 1)
                        self.updateFunctions13to20(0, 1)
                        self.updateFunctions21to28(0, 1)

                        # We need to force a State update to cause a display refresh once all data is known
                        self.updateState(TH_ST_IN_USE, 1)

                        # Now Write our own Throttle Id to the slot and write it back to the command station
                        LnPacket.sd.command = Opc.WR_SL_DATA
                        LnPacket.sd.id1 = self.myThrottleId & 0x7F
                        LnPacket.sd.id2 = self.myThrottleId >> 7
                        self.LocoNet.send(LnPacket, len(LnPacket.sd))

                # Ok another throttle did a NULL MOVE with the same slot before we did so we have to try again
                elif self.myState == TH_ST_SLOT_MOVE:
                    self.updateState(TH_ST_SELECT, 1)
                    self.LocoNet.send_2byte(Opc.LOCO_ADR, self.myAddress >> 7, self.myAddress & 0x7F)

            # Slot data is not for one of our slots so check if we have requested a new addres
            else:
                if self.myAddress == SlotAddress:
                    if self.myState == TH_ST_SELECT or self.myState == TH_ST_DISPATCH:
                        if (LnPacket.sd.stat & STAT1_SL_CONUP) == 0 and (LnPacket.sd.stat & LOCO_IN_USE) != LOCO_IN_USE:
                            if self.myState == TH_ST_SELECT:
                                self.updateState(TH_ST_SLOT_MOVE, 1)
                                self.mySlot = LnPacket.sd.slot
                                data2 = LnPacket.sd.slot
                            else:
                                self.updateState(TH_ST_FREE, 1)
                                data2 = 0

                            self.LocoNet.send_2byte(Opc.MOVE_SLOTS, LnPacket.sd.slot, data2)
                        else:
                            self.notifyThrottleError(TH_ER_SLOT_IN_USE)
                            self.updateState(TH_ST_FREE, 1)
                            consumed_flag = False

                    elif self.myState == TH_ST_SLOT_STEAL:
                        # Make Sure the Slot is actually IN_USE already as we are not going to do an SLOT_MOVE etc
                        if (LnPacket.sd.stat & STAT1_SL_CONUP) == 0 and (LnPacket.sd.stat & LOCO_IN_USE) == LOCO_IN_USE:
                            self.mySlot = LnPacket.sd.slot

                            self.updateState(TH_ST_IN_USE, 1)

                            self.updateAddress(SlotAddress, 1)
                            self.updateSpeed(LnPacket.sd.spd, 1)
                            self.updateDirectionAndFunctions(LnPacket.sd.dirf, 1)
                            self.updateFunctions5to8(LnPacket.sd.snd, 1)
                            self.updateStatus1(LnPacket.sd.stat, 1)

                            # force function update
                            self.updateFunctions9to12(0, 1)
                            self.updateFunctions13to20(0, 1)
                            self.updateFunctions21to28(0, 1)

                            # We need to force a State update to cause a display refresh once all data is known
                            self.updateState(TH_ST_IN_USE, 1)
                        else:
                            self.notifyThrottleError(TH_ER_NO_LOCO)
                            self.updateState(TH_ST_FREE, 1)
                            consumed_flag = False

                    elif self.myState == TH_ST_SLOT_FREE:
                        self.LocoNet.send_2byte(Opc.SLOT_STAT1, LnPacket.sd.slot, self.myStatus1 & ~STAT1_SL_BUSY)
                        self.mySlot = 0xFF
                        self.updateState(TH_ST_FREE, 1)

                if self.myState == TH_ST_ACQUIRE:
                    self.mySlot = LnPacket.sd.slot
                    self.updateState(TH_ST_IN_USE, 1)

                    self.updateAddress(SlotAddress, 1)
                    self.updateSpeed(LnPacket.sd.spd, 1)
                    self.updateDirectionAndFunctions(LnPacket.sd.dirf, 1)
                    self.updateStatus1(LnPacket.sd.stat, 1)

                    # force function update
                    self.updateFunctions9to12(0, 1)
                    self.updateFunctions13to20(0, 1)
                    self.updateFunctions21to28(0, 1)

        elif ((LnPacket.sd.command >= Opc.LOCO_SPD) and (LnPacket.sd.command <= Opc.LOCO_SND)) or (
                LnPacket.sd.command == Opc.SLOT_STAT1):
            if self.mySlot == LnPacket.ld.slot:
                if LnPacket.ld.command == Opc.LOCO_SPD:
                    self.updateSpeed(LnPacket.ld.data, 0)

                elif LnPacket.ld.command == Opc.LOCO_DIRF:
                    self.updateDirectionAndFunctions(LnPacket.ld.data, 0)

                elif LnPacket.ld.command == Opc.LOCO_SND:
                    self.updateFunctions5to8(LnPacket.ld.data, 0)

                elif LnPacket.ld.command == Opc.SLOT_STAT1:
                    self.updateStatus1(LnPacket.ld.data, 0)

        elif LnPacket.lack.command == Opc.LONG_ACK:
            if TH_ST_ACQUIRE <= self.myState <= TH_ST_SLOT_MOVE:
                if LnPacket.lack.opcode == (Opc.MOVE_SLOTS & 0x7F):
                    self.notifyThrottleError(TH_ER_NO_LOCO)
                    consumed_flag = False

                if LnPacket.lack.opcode == (Opc.LOCO_ADR & 0x7F):
                    self.notifyThrottleError(TH_ER_NO_SLOTS)
                    consumed_flag = False

                self.updateState(TH_ST_FREE, 1)

        elif LnPacket.data[0] == Opc.LOCO_F3:
            if self.mySlot == LnPacket.data[1]:
                self.updateFunctions9to12(LnPacket.data[2], 0)
                # 00 00 00 00 F12 F11 F10 F9

        elif LnPacket.uhf.command == Opc.UHLI_FUN:
            if self.mySlot == LnPacket.uhf.slot:
                if LnPacket.uhf.twenty == 0x20:
                    if LnPacket.uhf.fun_type == 0x07:
                        # for F9 to F12
                        self.updateFunctions9to12((LnPacket.uhf.function >> 4) & 0x0F, 0)
                        # (F12) F11 F10 F9 00 00 00 00

                    if LnPacket.uhf.fun_type == 0x08:
                        # for F13 to F19
                        self.updateFunctions13to20((LnPacket.uhf.function & 0x7F) | (self.myFunc13to20 & 0x80), 0)
                        # (F20) F19 F18 F17 F16 F15 F14 F13

                    if LnPacket.uhf.fun_type == 0x09:
                        # for F21 to F27
                        self.updateFunctions21to28((LnPacket.uhf.function & 0x7F) | (self.myFunc21to28 & 0x80), 0)
                        # (F28) F27 F26 F25 F24 F23 F22 F21

                    if LnPacket.uhf.fun_type == 0x05:
                        # for F28 and F20
                        self.updateFunctions13to20(((LnPacket.uhf.function << 2) & 0x80) | (self.myFunc13to20 & 0x7F),
                                                   0)
                        # F20 (F19 F18 F17 F16 F15 F14 F13)
                        self.updateFunctions21to28(((LnPacket.uhf.function << 1) & 0x80) | (self.myFunc21to28 & 0x7F),
                                                   0)
                        # F28 (F27 F26 F25 F24 F23 F22 F21)

        else:
            consumed_flag = False

        return consumed_flag

    def getAddress(self):
        return self.myAddress

    def stealAddress(self, Address):
        if self.myState == TH_ST_FREE:
            self.updateAddress(Address, 1)
            self.updateState(TH_ST_SLOT_STEAL, 1)

            self.LocoNet.send_2byte(Opc.LOCO_ADR, Address >> 7, Address & 0x7F)
            return TH_ER_OK

        self.notifyThrottleError(TH_ER_BUSY)
        return TH_ER_BUSY

    def setAddress(self, Address):
        if self.myState == TH_ST_FREE:
            self.updateAddress(Address, 1)
            self.updateState(TH_ST_SELECT, 1)

            self.LocoNet.send_2byte(Opc.LOCO_ADR, Address >> 7, Address & 0x7F)
            return TH_ER_OK

        self.notifyThrottleError(TH_ER_BUSY)
        return TH_ER_BUSY

    def resumeAddress(self, Address, LastSlot):
        if self.myState == TH_ST_FREE:
            self.mySlot = LastSlot
            self.updateAddress(Address, 1)
            self.updateState(TH_ST_SLOT_RESUME, 1)

            self.LocoNet.send_2byte(Opc.RQ_SL_DATA, LastSlot, 0)
            return TH_ER_OK

        self.notifyThrottleError(TH_ER_BUSY)
        return TH_ER_BUSY

    def freeAddress(self, Address):
        if self.myState == TH_ST_FREE:
            self.updateAddress(Address, 1)
            self.updateState(TH_ST_SLOT_FREE, 1)

            self.LocoNet.send_2byte(Opc.LOCO_ADR, Address >> 7, Address & 0x7F)
            return TH_ER_OK

        self.notifyThrottleError(TH_ER_BUSY)
        return TH_ER_BUSY

    def dispatchAddress(self, Address):
        if self.myState == TH_ST_FREE:
            self.updateAddress(Address, 1)
            self.updateState(TH_ST_DISPATCH, 1)

            self.LocoNet.send_2byte(Opc.LOCO_ADR, Address >> 7, Address & 0x7F)
            return TH_ER_OK

        self.notifyThrottleError(TH_ER_BUSY)
        return TH_ER_BUSY

    def acquireAddress(self):
        if self.myState == TH_ST_FREE:
            self.updateState(TH_ST_ACQUIRE, 1)
            self.LocoNet.send_2byte(Opc.MOVE_SLOTS, 0, 0)
            return TH_ER_OK

        self.notifyThrottleError(TH_ER_BUSY)
        return TH_ER_BUSY

    def releaseAddress(self):
        if self.myState == TH_ST_IN_USE:
            self.LocoNet.send_2byte(Opc.SLOT_STAT1, self.mySlot, self.myStatus1 & ~STAT1_SL_BUSY)

        self.mySlot = 0xFF
        self.updateState(TH_ST_FREE, 1)

    # To make it easier to handle the Speed steps 0 = Stop, 1 = EmStop and 2 - 127 normal speed steps we will swap speed
    # steps 0 and 1 so that the normal range for speed steps is Stop = 1 2-127 is normal as before and now 0 = EmStop
    @staticmethod
    def SwapSpeedZeroAndEmStop(Speed):
        if Speed == 0:
            return 1
        if Speed == 1:
            return 0
        return Speed

    def getSpeed(self):
        return self.SwapSpeedZeroAndEmStop(self.mySpeed)

    def setSpeed(self, Speed):
        if self.myState == TH_ST_IN_USE:
            Speed = self.SwapSpeedZeroAndEmStop(Speed)

            if self.mySpeed != Speed:
                # Always defer any speed other than stop or em stop
                if self.myOptions & TH_OP_DEFERRED_SPEED and ((Speed > 1) or (self.myTicksSinceLastAction == 0)):
                    self.myDeferredSpeed = Speed
                else:
                    self.LocoNet.send_2byte(Opc.LOCO_SPD, self.mySlot, Speed)
                    self.myTicksSinceLastAction = 0
                    self.myDeferredSpeed = 0
            return TH_ER_OK

        self.notifyThrottleError(TH_ER_NOT_SELECTED)
        return TH_ER_NOT_SELECTED

    def getDirection(self):
        return self.myDirFunc0to4 & Opc.DIRF_DIR

    def setDirection(self, Direction):
        if self.myState == TH_ST_IN_USE:
            self.LocoNet.send_2byte(Opc.LOCO_DIRF, self.mySlot, (self.myDirFunc0to4 | Opc.DIRF_DIR) if Direction else
                                    (self.myDirFunc0to4 & ~Opc.DIRF_DIR))

            self.myTicksSinceLastAction = 0
            return TH_ER_OK

        self.notifyThrottleError(TH_ER_NOT_SELECTED)
        return TH_ER_NOT_SELECTED

    def getFunction(self, Function):
        if Function <= 4:
            return self.myDirFunc0to4 & (1 << ((Function - 1) if Function else 4))
        elif 9 <= Function <= 12:
            return self.myFunc9to12 & (1 << (Function - 9))
        elif 13 <= Function <= 20:
            return self.myFunc13to20 & (1 << (Function - 13))
        elif 21 <= Function <= 28:
            return self.myFunc21to28 & (1 << (Function - 21))
        else:
            return self.myFunc5to8 & (1 << (Function - 5))

    def setFunction(self, Function, Value):
        if self.myState == TH_ST_IN_USE:
            if Function <= 8:
                if Function <= 4:
                    OpCode = Opc.LOCO_DIRF
                    Data = self.myDirFunc0to4
                    Mask = 1 << ((Function - 1) if Function else 4)
                else:
                    OpCode = Opc.LOCO_SND
                    Data = self.myFunc5to8
                    Mask = (1 << (Function - 5))

                if Value:
                    Data |= Mask
                else:
                    Data &= ~Mask

                self.LocoNet.send_2byte(OpCode, self.mySlot, Data)

            else:
                if 9 <= Function <= 12:
                    Data = self.myFunc9to12
                    Mask = 1 << (Function - 9)

                    if Value:
                        Data |= Mask
                    else:
                        Data &= ~Mask

                    self.LocoNet.send_2byte(Opc.LOCO_F3, self.mySlot, Data & 0x7F)

                elif 13 <= Function <= 19:  # F13 to F19 code 0x08
                    Data = self.myFunc13to20 & 0x7F
                    Mask = 1 << (Function - 13)

                    if Value:
                        Data |= Mask
                    else:
                        Data &= ~Mask

                    self.LocoNet.send_4byte(Opc.UHLI_FUN, 0x20, self.mySlot, 0x08, Data & 0x7F)

                elif 21 <= Function <= 27:  # F21 to F27 code 0x09
                    Data = self.myFunc21to28 & 0x7F
                    Mask = 1 << (Function - 21)

                    if Value:
                        Data |= Mask
                    else:
                        Data &= ~Mask

                    self.LocoNet.send_4byte(Opc.UHLI_FUN, 0x20, self.mySlot, 0x09, Data & 0x7F)

                elif Function == 20 or Function == 28:  # F28 and F20 code 0x05
                    # 0110 0000
                    Data = ((self.myFunc21to28 & 0x80) >> 1) | ((self.myFunc13to20 & 0x80) >> 2)

                    if Function == 20:
                        Mask = 0x20  # 0B00100000
                    else:
                        Mask = 0x40  # 0B01000000

                    if Value:
                        Data |= Mask
                    else:
                        Data &= ~Mask

                    self.LocoNet.send_4byte(Opc.UHLI_FUN, 0x20, self.mySlot, 0x05, Data & 0x7F)

            self.myTicksSinceLastAction = 0
            return TH_ER_OK

        self.notifyThrottleError(TH_ER_NOT_SELECTED)
        return TH_ER_NOT_SELECTED

    def setDirFunc0to4Direct(self, Value):
        if self.myState == TH_ST_IN_USE:
            self.LocoNet.send_2byte(Opc.LOCO_DIRF, self.mySlot, Value & 0x7F)
            return TH_ER_OK

        self.notifyThrottleError(TH_ER_NOT_SELECTED)
        return TH_ER_NOT_SELECTED

    def setFunc5to8Direct(self, Value):
        if self.myState == TH_ST_IN_USE:
            self.LocoNet.send_2byte(Opc.LOCO_SND, self.mySlot, Value & 0x7F)
            return TH_ER_OK

        self.notifyThrottleError(TH_ER_NOT_SELECTED)
        return TH_ER_NOT_SELECTED

    # Value = 0, 0, 0, 0, F12, F11, F10, F9
    def setFunc9to12Direct(self, Value):
        if self.myState == TH_ST_IN_USE:
            self.LocoNet.send_2byte(Opc.LOCO_F3, self.mySlot, Value & 0x0F)
            return TH_ER_OK

        self.notifyThrottleError(TH_ER_NOT_SELECTED)
        return TH_ER_NOT_SELECTED

    # Value = F20, F19, F18, F17, F16, F15, F14, F13
    def setFunc13to20Direct(self, Value):
        if self.myState == TH_ST_IN_USE:
            # F13 to F19
            self.LocoNet.send_4byte(Opc.UHLI_FUN, 0x20, self.mySlot, 0x08, Value & 0x7F)

            # F20( and F28)
            Value = ((self.myFunc21to28 & 0x80) >> 1) | ((Value & 0x80) >> 2)
            self.LocoNet.send_4byte(Opc.UHLI_FUN, 0x20, self.mySlot, 0x05, Value & 0x7F)

            return TH_ER_OK

        self.notifyThrottleError(TH_ER_NOT_SELECTED)
        return TH_ER_NOT_SELECTED

    # Value = F28, F27, F26, F25, F24, F23, F22, F21
    def setFunc21to28Direct(self, Value):
        if self.myState == TH_ST_IN_USE:
            # F21 to F27
            self.LocoNet.send_4byte(Opc.UHLI_FUN, 0x20, self.mySlot, 0x09, Value & 0x7F)

            # F28( and F21)
            Value = ((Value & 0x80) >> 1) | ((self.myFunc13to20 & 0x80) >> 2)
            self.LocoNet.send_4byte(Opc.UHLI_FUN, 0x20, self.mySlot, 0x05, Value & 0x7F)

            return TH_ER_OK

        self.notifyThrottleError(TH_ER_NOT_SELECTED)
        return TH_ER_NOT_SELECTED

    def getState(self):
        return self.myState

    @staticmethod
    def getStateStr(State):
        if State == TH_ST_FREE:
            return "Free"
        elif State == TH_ST_ACQUIRE:
            return "Acquire"
        elif State == TH_ST_SELECT:
            return "Select"
        elif State == TH_ST_DISPATCH:
            return "Dispatch"
        elif State == TH_ST_SLOT_MOVE:
            return "Slot Move"
        elif State == TH_ST_SLOT_FREE:
            return "Slot Free"
        elif State == TH_ST_SLOT_RESUME:
            return "Slot Resume"
        elif State == TH_ST_SLOT_STEAL:
            return "Slot Steal"
        elif State == TH_ST_IN_USE:
            return "In Use"
        else:
            return "Unknown"

    @staticmethod
    def getErrorStr(Error):
        if Error == TH_ER_OK:
            return "Ok"
        elif Error == TH_ER_SLOT_IN_USE:
            return "In Use"
        elif Error == TH_ER_BUSY:
            return "Busy"
        elif Error == TH_ER_NOT_SELECTED:
            return "Not Sel"
        elif Error == TH_ER_NO_LOCO:
            return "No Loco"
        elif Error == TH_ER_NO_SLOTS:
            return "No Free Slots"
        else:
            return "Unknown"

    def updateAddress(self, Address, ForceNotify):
        if ForceNotify or self.myAddress != Address:
            self.myAddress = Address
            self.notifyThrottleAddress(self.myState, Address, self.mySlot)

    def updateSpeed(self, Speed, ForceNotify):
        if ForceNotify or self.mySpeed != Speed:
            self.mySpeed = Speed
            self.notifyThrottleSpeed(self.myState, self.SwapSpeedZeroAndEmStop(Speed))

    def updateState(self, State, ForceNotify):
        if ForceNotify or self.myState != State:
            PrevState = self.myState
            self.myState = State
            self.notifyThrottleState(PrevState, State)

    def updateStatus1(self, Status, ForceNotify):
        if ForceNotify or self.myStatus1 != Status:
            self.myStatus1 = Status
            self.notifyThrottleSlotStatus(Status)
            self.updateState(TH_ST_IN_USE if (Status & LOCO_IN_USE) == LOCO_IN_USE else TH_ST_FREE, ForceNotify)

    def updateDirectionAndFunctions(self, DirFunc0to4, ForceNotify):
        if ForceNotify or self.myDirFunc0to4 != DirFunc0to4:
            Diffs = self.myDirFunc0to4 ^ DirFunc0to4
            self.myDirFunc0to4 = DirFunc0to4

            # Check Functions 1 - 4
            Mask = 1
            for Function in range(1, 5):
                if ForceNotify or (Diffs & Mask):
                    self.notifyThrottleFunction(Function, DirFunc0to4 & Mask)
                Mask <<= 1

            # Check Function 0
            if ForceNotify or (Diffs & Opc.DIRF_F0):
                self.notifyThrottleFunction(0, DirFunc0to4 & Opc.DIRF_F0)

            # Check Direction
            if ForceNotify or (Diffs & Opc.DIRF_DIR):
                self.notifyThrottleDirection(self.myState, DirFunc0to4 & Opc.DIRF_DIR)

    def updateFunctions5to8(self, Func5to8, ForceNotify):

        if ForceNotify or self.myFunc5to8 != Func5to8:
            Diffs = self.myFunc5to8 ^ Func5to8
            self.myFunc5to8 = Func5to8

            # Check Functions 5 - 8
            Mask = 1
            for Function in range(5, 9):
                if ForceNotify or (Diffs & Mask):
                    self.notifyThrottleFunction(Function, Func5to8 & Mask)
                Mask <<= 1

    def updateFunctions9to12(self, Func9to12, ForceNotify):
        if ForceNotify or self.myFunc9to12 != Func9to12:
            Diffs = self.myFunc9to12 ^ Func9to12
            self.myFunc9to12 = Func9to12

            # Check Functions 9 - 12
            Mask = 1
            for Function in range(9, 13):
                if ForceNotify or (Diffs & Mask):
                    self.notifyThrottleFunction(Function, Func9to12 & Mask)
                Mask <<= 1

    def updateFunctions13to20(self, Func13to20, ForceNotify):
        if ForceNotify or self.myFunc13to20 != Func13to20:
            Diffs = self.myFunc13to20 ^ Func13to20
            self.myFunc13to20 = Func13to20

            # Check Functions 13 - 20
            Mask = 1
            for Function in range(13, 21):
                if ForceNotify or (Diffs & Mask):
                    self.notifyThrottleFunction(Function, Func13to20 & Mask)
                Mask <<= 1

    def updateFunctions21to28(self, Func21to28, ForceNotify):
        if ForceNotify or self.myFunc21to28 != Func21to28:
            Diffs = self.myFunc21to28 ^ Func21to28
            self.myFunc21to28 = Func21to28

            # Check Functions 21 - 28
            Mask = 1
            for Function in range(21, 29):
                if ForceNotify or (Diffs & Mask):
                    self.notifyThrottleFunction(Function, Func21to28 & Mask)
                Mask <<= 1

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
