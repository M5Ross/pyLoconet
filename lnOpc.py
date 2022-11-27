
# MASKS
DIRF_DIR = 0x20  # direction bit    */
DIRF_F0 = 0x10  # Function 0 bit   */
DIRF_F4 = 0x08  # Function 1 bit   */
DIRF_F3 = 0x04  # Function 2 bit   */
DIRF_F2 = 0x02  # Function 3 bit   */
DIRF_F1 = 0x01  # Function 4 bit   */
SND_F8 = 0x08  # Sound 4/Function 8 bit */
SND_F7 = 0x04  # Sound 3/Function 7 bit */
SND_F6 = 0x02  # Sound 2/Function 6 bit */
SND_F5 = 0x01  # Sound 1/Function 5 bit */

SW_ACK_CLOSED = 0x20  # command switch closed/open bit   */
SW_ACK_OUTPUT = 0x10  # command switch output on/off bit */

INPUT_REP_CB = 0x40  # control bit, reserved otherwise      */
INPUT_REP_SW = 0x20  # input is switch input, aux otherwise */
INPUT_REP_HI = 0x10  # input is HI, LO otherwise            */

SW_REP_SW = 0x20  # switch input, aux input otherwise    */
SW_REP_HI = 0x10  # input is HI, LO otherwise            */
SW_REP_CLOSED = 0x20  # 'Closed' line is ON, OFF otherwise   */
SW_REP_THROWN = 0x10  # 'Thrown' line is ON, OFF otherwise   */
SW_REP_INPUTS = 0x40  # sensor inputs, outputs otherwise     */

SW_REQ_DIR = 0x20  # switch direction - closed/thrown     */
SW_REQ_OUT = 0x10  # output On/Off                        */

LOCO_SPD_ESTOP = 0x01  # emergency stop command               */
SE = 0xE4  # Opcode Security Element              */
ANALOGIO = 0xE5  # Analog IO

MULTI_SENSE_MSG = 0x60  # byte 1                          */
MULTI_SENSE_ABSENT = 0x00  # MSG field: transponder lost     */
MULTI_SENSE_PRESENT = 0x20  # MSG field: transponder seen     */
MULTI_SENSE_DEVICE_INFO = 0x60  # MSG field: Device Info Message  */


# LOCONET OPCODE
BUSY = 0x81
GPOFF = 0x82
GPON = 0x83
IDLE = 0x85
LOCO_SPD = 0xa0
LOCO_DIRF = 0xa1
LOCO_SND = 0xa2
LOCO_F3 = 0xa3  # Function 9-12
SW_REQ = 0xb0
SW_REP = 0xb1
INPUT_REP = 0xb2
UNKNOWN = 0xb3
LONG_ACK = 0xb4
SLOT_STAT1 = 0xb5
CONSIST_FUNC = 0xb6
UNLINK_SLOTS = 0xb8
LINK_SLOTS = 0xb9
MOVE_SLOTS = 0xba
RQ_SL_DATA = 0xbb
SW_STATE = 0xbc
SW_ACK = 0xbd
LOCO_ADR = 0xbf
MULTI_SENSE = 0xd0
UHLI_FUN = 0xd4  # Function 9-28 by Uhlenbrock
PEER_XFER = 0xe5
SL_RD_DATA = 0xe7
IMM_PACKET = 0xed
IMM_PACKET_2 = 0xee
WR_SL_DATA = 0xef
MASK = 0x7f  # mask for acknowledge opcodes


class LnMsg:
    def __init__(self, message):
        self.LM_MSG_MAX_LENGTH = 16
        self.data = [0] * self.LM_MSG_MAX_LENGTH
        self.length = len(message)
        if (message is not []) and (self.length <= self.LM_MSG_MAX_LENGTH):
            self.data[:self.length] = message
        else:
            self.length = 0

    def getLnMsg(self):
        return self.data[:self.length]

# SUBCLASS


class locoAdrMsg(LnMsg):
    def __init__(self, msg):
        LnMsg.__init__(self, msg)
        self.command = self.data[0]
        self.adr_hi = self.data[1]
        self.adr_lo = self.data[2]
        self.chksum = self.data[3]

    def __len__(self):
        return 4


class switchAckMsg(LnMsg):
    def __init__(self, msg):
        LnMsg.__init__(self, msg)
        self.command = self.data[0]
        self.sw1 = self.data[1]
        self.sw2 = self.data[2]
        self.chksum = self.data[3]

    def __len__(self):
        return 4


class switchReqMsg(LnMsg):
    def __init__(self, msg):
        LnMsg.__init__(self, msg)
        self.command = self.data[0]
        self.sw1 = self.data[1]
        self.sw2 = self.data[2]
        self.chksum = self.data[3]

    def __len__(self):
        return 4


class slotReqMsg(LnMsg):
    def __init__(self, msg):
        LnMsg.__init__(self, msg)
        self.command = self.data[0]
        self.slot = self.data[1]
        self.pad = self.data[2]
        self.chksum = self.data[3]

    def __len__(self):
        return 4


class slotMoveMsg(LnMsg):
    def __init__(self, msg):
        LnMsg.__init__(self, msg)
        self.command = self.data[0]
        self.src = self.data[1]
        self.dest = self.data[2]
        self.chksum = self.data[3]

    def __len__(self):
        return 4


class slotLinkMsg(LnMsg):
    def __init__(self, msg):
        LnMsg.__init__(self, msg)
        self.command = self.data[0]
        self.src = self.data[1]
        self.dest = self.data[2]
        self.chksum = self.data[3]

    def __len__(self):
        return 4


class consistFuncMsg(LnMsg):
    def __init__(self, msg):
        LnMsg.__init__(self, msg)
        self.command = self.data[0]
        self.slot = self.data[1]
        self.dirf = self.data[2]
        self.chksum = self.data[3]

    def __len__(self):
        return 4


class slotStatusMsg(LnMsg):
    def __init__(self, msg):
        LnMsg.__init__(self, msg)
        self.command = self.data[0]
        self.slot = self.data[1]
        self.stat = self.data[2]
        self.chksum = self.data[3]

    def __len__(self):
        return 4


class longAckMsg(LnMsg):
    def __init__(self, msg):
        LnMsg.__init__(self, msg)
        self.command = self.data[0]
        self.opcode = self.data[1]
        self.ack1 = self.data[2]
        self.chksum = self.data[3]

    def __len__(self):
        return 4


class inputRepMsg(LnMsg):
    def __init__(self, msg):
        LnMsg.__init__(self, msg)
        self.command = self.data[0]
        self.in1 = self.data[1]
        self.in2 = self.data[2]
        self.chksum = self.data[3]

    def __len__(self):
        return 4


class swRepMsg(LnMsg):
    def __init__(self, msg):
        LnMsg.__init__(self, msg)
        self.command = self.data[0]
        self.sn1 = self.data[1]
        self.sn2 = self.data[2]
        self.chksum = self.data[3]

    def __len__(self):
        return 4


class swReqMsg(LnMsg):
    def __init__(self, msg):
        LnMsg.__init__(self, msg)
        self.command = self.data[0]
        self.sw1 = self.data[1]
        self.sw2 = self.data[2]
        self.chksum = self.data[3]

    def __len__(self):
        return 4


class multiSenseTranspMsg(LnMsg):
    def __init__(self, msg):
        LnMsg.__init__(self, msg)
        self.command = self.data[0]
        self.type = self.data[1]
        self.zone = self.data[2]
        self.adr1 = self.data[3]
        self.adr2 = self.data[4]
        self.chksum = self.data[5]

    def __len__(self):
        return 6


class multiSenseDeviceInfoMsg(LnMsg):
    def __init__(self, msg):
        LnMsg.__init__(self, msg)
        self.command = self.data[0]
        self.arg1 = self.data[1]
        self.arg2 = self.data[2]
        self.arg3 = self.data[3]
        self.arg4 = self.data[4]
        self.chksum = self.data[5]

    def __len__(self):
        return 6


class UhlenbrockFun928Msg(LnMsg):
    def __init__(self, msg):
        LnMsg.__init__(self, msg)
        self.command = self.data[0]
        self.twenty = self.data[1]
        self.slot = self.data[2]
        self.fun_type = self.data[3]
        self.function = self.data[4]
        self.chksum = self.data[5]

    def __len__(self):
        return 6


class locoDataMsg(LnMsg):
    def __init__(self, msg):
        LnMsg.__init__(self, msg)
        self.command = self.data[0]
        self.slot = self.data[1]
        self.data = self.data[2]
        self.chksum = self.data[3]

    def __len__(self):
        return 4


class locoSndMsg(LnMsg):
    def __init__(self, msg):
        LnMsg.__init__(self, msg)
        self.command = self.data[0]
        self.slot = self.data[1]
        self.snd = self.data[2]
        self.chksum = self.data[3]

    def __len__(self):
        return 4


class locoDirfMsg(LnMsg):
    def __init__(self, msg):
        LnMsg.__init__(self, msg)
        self.command = self.data[0]
        self.slot = self.data[1]
        self.dirf = self.data[2]
        self.chksum = self.data[3]

    def __len__(self):
        return 4


class locoSpdMsg(LnMsg):
    def __init__(self, msg):
        LnMsg.__init__(self, msg)
        self.command = self.data[0]
        self.slot = self.data[1]
        self.spd = self.data[2]
        self.chksum = self.data[3]

    def __len__(self):
        return 4


class rwSlotDataMsg(LnMsg):
    def __init__(self, msg):
        LnMsg.__init__(self, msg)
        self.command = self.data[0]
        self.mesg_size = self.data[1]
        self.slot = self.data[2]
        self.stat = self.data[3]
        self.adr = self.data[4]
        self.spd = self.data[5]
        self.dirf = self.data[6]
        self.trk = self.data[7]
        self.ss2 = self.data[8]
        self.adr2 = self.data[9]
        self.snd = self.data[10]
        self.id1 = self.data[11]
        self.id2 = self.data[12]
        self.chksum = self.data[13]

    def __len__(self):
        return 14


class fastClockMsg(LnMsg):
    def __init__(self, msg):
        LnMsg.__init__(self, msg)
        self.command = self.data[0]
        self.mesg_size = self.data[1]
        self.slot = self.data[2]
        self.clk_rate = self.data[3]
        self.frac_minsl = self.data[4]
        self.frac_minsh = self.data[5]
        self.mins_60 = self.data[6]
        self.track_stat = self.data[7]
        self.hours_24 = self.data[8]
        self.days = self.data[9]
        self.clk_cntrl = self.data[10]
        self.id1 = self.data[11]
        self.id2 = self.data[12]
        self.chksum = self.data[13]

    def __len__(self):
        return 14


class progTaskMsg(LnMsg):
    def __init__(self, msg):
        LnMsg.__init__(self, msg)
        self.command = self.data[0]
        self.mesg_size = self.data[1]
        self.slot = self.data[2]
        self.pcmd = self.data[3]
        self.pstat = self.data[4]
        self.hopsa = self.data[5]
        self.lopsa = self.data[6]
        self.trk = self.data[7]
        self.cvh = self.data[8]
        self.cvl = self.data[9]
        self.data7 = self.data[10]
        self.pad2 = self.data[11]
        self.pad3 = self.data[12]
        self.chksum = self.data[13]

    def __len__(self):
        return 14


class peerXferMsg(LnMsg):
    def __init__(self, msg):
        LnMsg.__init__(self, msg)
        self.command = self.data[0]
        self.mesg_size = self.data[1]
        self.src = self.data[2]
        self.dst_l = self.data[3]
        self.dst_h = self.data[4]
        self.pxct1 = self.data[5]
        self.d1 = self.data[6]
        self.d2 = self.data[7]
        self.d3 = self.data[8]
        self.d4 = self.data[9]
        self.pxct2 = self.data[10]
        self.d5 = self.data[11]
        self.d6 = self.data[12]
        self.d7 = self.data[13]
        self.d8 = self.data[14]
        self.chksum = self.data[15]

    def __len__(self):
        return 16


class Msg:
    def __init__(self, msg):
        self.la = locoAdrMsg(msg)
        self.sa = switchAckMsg(msg)
        self.sr = slotReqMsg(msg)
        self.sm = slotMoveMsg(msg)
        self.cf = consistFuncMsg(msg)
        self.ss = slotStatusMsg(msg)
        self.lack = longAckMsg(msg)
        self.ir = inputRepMsg(msg)
        self.srp = swRepMsg(msg)
        self.srq = swReqMsg(msg)
        self.ld = locoDataMsg(msg)
        self.ls = locoSndMsg(msg)
        self.ldf = locoDirfMsg(msg)
        self.lsp = locoSpdMsg(msg)
        self.sd = rwSlotDataMsg(msg)
        self.fc = rwSlotDataMsg(msg)
        self.pt = progTaskMsg(msg)
        self.px = peerXferMsg(msg)
        # self.sp = sendPktMsg(msg)
        # self.sv = svMsg(msg)
        # self.sz = szMsg(msg)
        # self.se = seMsg(msg)
        # self.ub = UhlenbrockMsg(msg)
        # self.anio = AnalogIoMsg(msg)
        self.mstr = multiSenseTranspMsg(msg)
        self.msdi = multiSenseDeviceInfoMsg(msg)
        self.uhf = UhlenbrockFun928Msg(msg)
        self.data = LnMsg(msg)
