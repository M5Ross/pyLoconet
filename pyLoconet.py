
import lnOpc as Opc
from lnCom import LoconetUart
from time import sleep


class LoconetError(Exception):
    pass


class LoconetClass:
    def __init__(self, port):
        self.SendPacket = Opc.LnMsg([])
        self.exit = False
        self.cycle_delay = 0.1
        self.com = LoconetUart(port[0], port[1])
        if self.com.start():
            self.start()
        else:
            raise LoconetError("Cannot start port communication!")

    def start(self):
        pass

    def stop(self):
        pass

    def close(self):
        self.exit = True
        sleep(self.cycle_delay)
        self.com.stop()

    def receive(self):
        if self.com.available() > 0:
            packet = self.com.receive_ln_packet()
            length = len(packet) - 1
            if self.get_checksum(packet, length) == packet[length]:
                return packet
        return None

    def send(self, packet, packet_len):
        return self.com.send_ln_packet(packet, packet_len)

    def send_len(self, ln_packet_len):
        self.SendPacket.data[ln_packet_len] = self.get_checksum(self.SendPacket, ln_packet_len)
        ln_packet_len += 1
        return self.send(self.SendPacket, ln_packet_len)

    def send_packet(self, packet):
        self.SendPacket = packet
        return self.send_len(len(packet))

    def send_packet_len(self, packet, packet_len):
        self.SendPacket = packet
        return self.send_len(packet_len)

    def send_2byte(self, opcode, data1, data2):
        self.SendPacket.data[0] = opcode
        self.SendPacket.data[1] = data1
        self.SendPacket.data[2] = data2
        return self.send_len(3)

    def send_4byte(self, opcode, data1, data2, data3, data4):
        self.SendPacket.data[0] = opcode
        self.SendPacket.data[1] = data1
        self.SendPacket.data[2] = data2
        self.SendPacket.data[3] = data3
        self.SendPacket.data[4] = data4
        return self.send_len(5)

    def send_long_ack(self, uc_code):
        return self.send_2byte(Opc.LONG_ACK, Opc.PEER_XFER, uc_code)

    def report_power(self, state):
        self.SendPacket.data[0] = Opc.GPON if state else Opc.GPOFF
        return self.send_len(1)

    def get_status_string(self, status):
        if self.LN_CD_BACKOFF <= status <= self.LN_RETRY_ERROR:
            return self.loconet_status_strings[status]
        return "Invalid Status"

    def process_switch_sensor_message(self, packet=None):
        ln_packet = Opc.Msg(packet)
        consumed_flag = True

        address = ln_packet.srq.sw1 | ((ln_packet.srq.sw2 & 0x0F) << 7)
        c = ln_packet.sr.command
        if c != Opc.INPUT_REP:
            address += 1

        if c == Opc.INPUT_REP:
            address <<= 1
            address += 2 if ln_packet.ir.in2 & Opc.INPUT_REP_SW else 1
            self.notify_sensor(address, ln_packet.ir.in2 & Opc.INPUT_REP_HI)

        elif c == Opc.GPON:
            self.notify_power(1)

        elif c == Opc.GPOFF:
            self.notify_power(0)

        elif c == Opc.SW_REQ:
            self.notify_switch_request(address, ln_packet.srq.sw2 & Opc.SW_REQ, ln_packet.srq.sw2 & Opc.SW_REQ_DIR)

        elif c == Opc.SW_REP:
            if ln_packet.srp.sn2 & Opc.SW_REP_INPUTS:
                self.notify_switch_report(address, ln_packet.srp.sn2 & Opc.SW_REP_HI,
                                          ln_packet.srp.sn2 & Opc.SW_REP_SW)
            else:
                self.notify_switch_output_report(address, ln_packet.srp.sn2 & Opc.SW_REP_CLOSED,
                                                 ln_packet.srp.sn2 & Opc.SW_REP_THROWN)

        elif c == Opc.SW_STATE:
            self.notify_switch_state(address, ln_packet.srq.sw2 & Opc.SW_REQ_OUT, ln_packet.srq.sw2 & Opc.SW_REQ_DIR)

        elif c == Opc.SW_ACK:
            pass

        elif c == Opc.MULTI_SENSE:
            c1 = ln_packet.data.data[1] & Opc.MULTI_SENSE_MSG
            if c1 == Opc.MULTI_SENSE_DEVICE_INFO:
                pcmd = ln_packet.msdi.arg3 & 0xF0

                if pcmd == 0x30 or pcmd == 0x10:
                    cm1 = ln_packet.msdi.arg3
                    cm2 = ln_packet.msdi.arg4
                    board_id = ln_packet.msdi.arg2 + 1 + 128 if ln_packet.msdi.arg1 & 0x01 == 1 else 0
                    d = 1
                    for i in range(4):
                        mode = 0 if cm1 & d != 0 else 1
                        direction = cm2 & d
                        d *= 2
                        self.notify_multisense_power(board_id, i+1, mode, direction)
                elif pcmd == 0x70:
                    pass
                elif pcmd == 0x00:
                    pass

            elif c1 == Opc.MULTI_SENSE_ABSENT or c1 == Opc.MULTI_SENSE_PRESENT:
                address = ln_packet.mstr.zone + ((ln_packet.mstr.type & 0x1F) << 7) + 1
                present = True if ln_packet.mstr.type & 0x20 != 0 else False

                loco = ln_packet.mstr.adr2
                if ln_packet.mstr.adr1 != 0x7D:
                    loco += ln_packet.mstr.adr1 * 128

                z = ln_packet.mstr.zone & 0x0F

                if z == 0x00:
                    zone = "A"
                elif z == 0x02:
                    zone = "B"
                elif z == 0x04:
                    zone = "C"
                elif z == 0x06:
                    zone = "D"
                elif z == 0x08:
                    zone = "E"
                elif z == 0x0A:
                    zone = "F"
                elif z == 0x0C:
                    zone = "G"
                elif z == 0x0E:
                    zone = "H"
                else:
                    zone = z

                self.notify_multisense_transponder(address, zone, loco, present)

        elif c == Opc.LONG_ACK:
            if ln_packet.lack.opcode == (Opc.SW_STATE & 0x07):
                self.notify_long_ack(ln_packet.lack.ack1 & 0x01)
            else:
                consumed_flag = False
        else:
            consumed_flag = False

        return consumed_flag

    def request_switch(self, address, output, direction):
        addr_h = ((address-1) >> 7) & 0x0F
        addr_l = address & 0x7F
        if output:
            addr_h |= Opc.SW_REQ_OUT
        if direction:
            addr_h |= Opc.SW_REQ_DIR
        return self.send_2byte(Opc.SW_REQ, addr_l, addr_h)

    def report_switch(self, address):
        address -= 1
        return self.send_2byte(Opc.SW_STATE, address & 0x7F, (address >> 7) & 0x0F)

    def report_sensor(self, address, state):
        addr_h = ((address-1) >> 8) & 0x0F | Opc.INPUT_REP_CB
        addr_l = (address >> 1) & 0x7F
        if address % 2:
            addr_h |= Opc.INPUT_REP_SW
        if state:
            addr_h |= Opc.INPUT_REP_HI
        return self.send_2byte(Opc.INPUT_REP, addr_l, addr_h)

    def report_multisense(self, address, state, loco):
        address -= 1
        address <<= 1
        type_ = (address >> 7) & 0x1F
        if state:
            type_ |= Opc.MULTI_SENSE_PRESENT
        zone = address & 0x7E
        if loco < 128:
            ad1 = 0x7D
        else:
            ad1 = (loco >> 7) & 0x7F
        ad2 = loco & 0x7F
        return self.send_4byte(Opc.MULTI_SENSE, type_, zone, ad1, ad2)

    def run(self):
        while True:
            flag = False
            packet = self.receive()
            if packet is not None:
                flag = self.process_switch_sensor_message(packet)
            self.your_custom_code(packet, flag)
            if self.exit:
                break
            sleep(self.cycle_delay)
        self.stop()

    @staticmethod
    def delay(seconds):
        sleep(seconds)

    @staticmethod
    def get_checksum(packet, packet_len):
        checksum = 0xFF
        for i in range(packet_len):
            checksum ^= packet.data[i]
        return checksum

    def your_custom_code(self, packet, flag):
        pass

    def notify_sensor(self, address, state):
        pass

    def notify_switch_request(self, address, output, direction):
        pass

    def notify_switch_report(self, address, output, direction):
        pass

    def notify_switch_output_report(self, address, closed, thrown):
        pass

    def notify_switch_state(self, address, output, direction):
        pass

    def notify_power(self, state):
        pass

    def notify_multisense_transponder(self, address, zone, loco, present):
        pass

    def notify_multisense_power(self, board, subdistrict, mode, direction):
        pass

    def notify_long_ack(self, direction):
        pass
