
import lnOpc

LN_BUF_SIZE = 128
LN_BUF_OPC_WRAP_AROUND = 0x00		# Special character to indcate a buffer wrap
LN_CHECKSUM_SEED = 0xFF


class LnBufStats:
    def __init__(self):
        self.RxPackets = 0
        self.RxErrors = 0
        self.TxPackets = 0
        self.TxErrors = 0
        self.Collisions = 0


class LnBuf:
    def __init__(self):
        self.Buf = [0]*LN_BUF_SIZE
        self.WriteIndex = 0
        self.ReadIndex = 0
        self.ReadPacketIndex = 0
        self.CheckSum = 0
        self.ReadExpLen = 0
        self.Stats = LnBufStats()

    def move(self, dest, start, long):
        self.Buf[dest:dest+long] = self.Buf[start:start+long]


class LoconetBuffer:
    def __init__(self):
        self.Buffer = LnBuf()

    def recvLnMsg(self):
        while self.Buffer.ReadIndex != self.Buffer.WriteIndex:
            newByte = self.Buffer.Buf[self.Buffer.ReadIndex]
            if newByte & 0x80:
                if self.Buffer.ReadPacketIndex != self.Buffer.ReadIndex:
                    self.Buffer.Stats.RxErrors += 1

                self.Buffer.ReadPacketIndex = self.Buffer.ReadIndex
                self.Buffer.CheckSum = LN_CHECKSUM_SEED
                bGotNewLength = 0
                # self.Buffer.ReadExpLen = self.getLnMsgSize([newByte, 0])
                self.Buffer.ReadExpLen = 0 if newByte & 0x60 == 0x60 else (newByte & 0x60) >> 4 + 2
                if self.Buffer.ReadExpLen != 0:
                    bGotNewLength = 1
            elif self.Buffer.ReadExpLen == 0:
                self.Buffer.ReadExpLen = newByte
                bGotNewLength = 1
            else:
                bGotNewLength = 0

            if bGotNewLength:
                if (self.Buffer.ReadPacketIndex + self.Buffer.ReadExpLen) > LN_BUF_SIZE:
                    tempSize = LN_BUF_SIZE - self.Buffer.ReadPacketIndex
                    lastWriteIndex = self.Buffer.WriteIndex

                    if self.Buffer.WriteIndex > self.Buffer.ReadIndex:
                        self.Buffer.WriteIndex = self.Buffer.WriteIndex - self.Buffer.ReadPacketIndex
                    else:
                        self.Buffer.WriteIndex = self.Buffer.WriteIndex - tempSize

                    if lastWriteIndex < self.Buffer.ReadIndex:
                        self.Buffer.move(tempSize, 0, lastWriteIndex)
                    else:
                        tempSize = lastWriteIndex - self.Buffer.ReadPacketIndex
                    self.Buffer.move(0, self.Buffer.ReadPacketIndex, tempSize)

                    self.Buffer.ReadIndex -= self.Buffer.ReadPacketIndex
                    self.Buffer.ReadPacketIndex = 0

            tempMsg = None

            self.Buffer.ReadIndex += 1

            tempSize = self.Buffer.ReadIndex - self.Buffer.ReadPacketIndex

            if self.Buffer.ReadIndex >= LN_BUF_SIZE:
                self.Buffer.ReadIndex = 0

            if tempSize == self.Buffer.ReadExpLen:
                if self.Buffer.CheckSum == newByte:
                    tempMsg = lnOpc.LnMsg(self.Buffer.Buf[:self.Buffer.ReadPacketIndex])
                    self.Buffer.Stats.RxPackets += 1
                else:
                    self.Buffer.Stats.RxErrors += 1

                self.Buffer.ReadPacketIndex = self.Buffer.ReadIndex

                if tempMsg is not None:
                    return tempMsg.getLnMsg()

            self.Buffer.CheckSum ^= newByte

        return None

    def getLnBufStats(self):
        return self.Buffer.Stats

    def getLnMsgSize(self, LnMsg):
        return LnMsg[1] if LnMsg[0] & 0x60 == 0x60 else ((LnMsg[0] & 0x60) >> 4) + 2

    def addByteLnBuf(self, newByte):
        self.Buffer.Buf[self.Buffer.WriteIndex+1] = newByte
        if self.Buffer.WriteIndex >= LN_BUF_SIZE:
            self.Buffer.WriteIndex = 0

    def addMsgLnBuf(self, newMsg):
        lenght = self.getLnMsgSize(newMsg)
        for index in range(lenght):
            self.addByteLnBuf(newMsg.data[index])

    def lnPacketReady(self):
        return True if self.Buffer.ReadIndex != self.Buffer.WriteIndex else False
