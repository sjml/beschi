import * as harness from "./_harness";
export * from "./_harness";

import * as SmallMessages from '../../../../out/generated/assemblyscript/SmallMessages';
import * as Nested from '../../../../out/generated/assemblyscript/Nested';

var nested = new Nested.DeepData();
nested.data.data.data.data.data.data.data.data.datums = [];

var emptyMsg = new SmallMessages.EmptyMessage();
var byteMsg = new SmallMessages.ByteMessage();
byteMsg.byteMember = 242;
var intMsgA = new SmallMessages.IntMessage();
intMsgA.intMember = -42;
var intMsgB = new SmallMessages.IntMessage();
intMsgB.intMember = 2048;
var floatMsg = new SmallMessages.FloatMessage();
floatMsg.floatMember = 1234.5678;
var longMsg = new SmallMessages.LongMessage();
longMsg.intMember = 2147483647 + 10; // (2^31 - 1) + 10

export function generate(): usize {
    let size: usize = 0;
    size += byteMsg.getSizeInBytes();
    size += intMsgA.getSizeInBytes() * 3;
    size += intMsgB.getSizeInBytes() * 4;
    size += emptyMsg.getSizeInBytes() * 2;
    size += longMsg.getSizeInBytes();
    size += floatMsg.getSizeInBytes();
    size += 12;

    harness.allocate(size);
    const dv = harness.getDataView();
    const da = new SmallMessages.DataAccess(dv);

    let success: bool = true; // good vibes
    success = byteMsg.writeBytesDA(da, true);   //  0
    harness.softAssert(success == true, "writing multiple message [0]");
    success = intMsgA.writeBytesDA(da, true);   //  1
    harness.softAssert(success == true, "writing multiple message [1]");
    success = intMsgB.writeBytesDA(da, true);   //  2
    harness.softAssert(success == true, "writing multiple message [2]");
    success = emptyMsg.writeBytesDA(da, true);  //  3
    harness.softAssert(success == true, "writing multiple message [3]");
    success = longMsg.writeBytesDA(da, true);   //  4
    harness.softAssert(success == true, "writing multiple message [4]");
    success = floatMsg.writeBytesDA(da, true);  //  5
    harness.softAssert(success == true, "writing multiple message [5]");
    success = intMsgA.writeBytesDA(da, true);   //  6
    harness.softAssert(success == true, "writing multiple message [6]");
    success = intMsgB.writeBytesDA(da, true);   //  7
    harness.softAssert(success == true, "writing multiple message [7]");
    success = intMsgB.writeBytesDA(da, true);   //  8
    harness.softAssert(success == true, "writing multiple message [8]");
    success = intMsgB.writeBytesDA(da, true);   //  9
    harness.softAssert(success == true, "writing multiple message [9]");
    success = intMsgA.writeBytesDA(da, true);   // 10
    harness.softAssert(success == true, "writing multiple message [10]");
    success = emptyMsg.writeBytesDA(da, true);  // 11
    harness.softAssert(success == true, "writing multiple message [11]");

    return harness.getDataPtr();
}

export function read(): void {
    const dv = harness.getDataView();

    const msgList = SmallMessages.ProcessRawBytes(dv, -1);

    harness.softAssert(msgList.length == 12, "reading multiple messages length");

    harness.softAssert(msgList[0].getMessageType() == SmallMessages.MessageType.ByteMessageType, "msg 0 type");
    harness.softAssert((msgList[0] as SmallMessages.ByteMessage).byteMember == byteMsg.byteMember, "msg 0 content");

    harness.softAssert(msgList[1].getMessageType() == SmallMessages.MessageType.IntMessageType, "msg 1 type");
    harness.softAssert((msgList[1] as SmallMessages.IntMessage).intMember == intMsgA.intMember, "msg 1 content");

    harness.softAssert(msgList[2].getMessageType() == SmallMessages.MessageType.IntMessageType, "msg 2 type");
    harness.softAssert((msgList[2] as SmallMessages.IntMessage).intMember == intMsgB.intMember, "msg 2 content");

    harness.softAssert(msgList[3].getMessageType() == SmallMessages.MessageType.EmptyMessageType, "msg 3 type");

    harness.softAssert(msgList[4].getMessageType() == SmallMessages.MessageType.LongMessageType, "msg 4 type");
    harness.softAssert((msgList[4] as SmallMessages.LongMessage).intMember == longMsg.intMember, "msg 4 content");

    harness.softAssert(msgList[5].getMessageType() == SmallMessages.MessageType.FloatMessageType, "msg 5 type");
    harness.softAssert((msgList[5] as SmallMessages.FloatMessage).floatMember == Math.fround(floatMsg.floatMember), "msg 5 content");

    harness.softAssert(msgList[6].getMessageType() == SmallMessages.MessageType.IntMessageType, "msg 6 type");
    harness.softAssert((msgList[6] as SmallMessages.IntMessage).intMember == intMsgA.intMember, "msg 6 content");

    harness.softAssert(msgList[7].getMessageType() == SmallMessages.MessageType.IntMessageType, "msg 7 type");
    harness.softAssert((msgList[7] as SmallMessages.IntMessage).intMember == intMsgB.intMember, "msg 7 content");

    harness.softAssert(msgList[8].getMessageType() == SmallMessages.MessageType.IntMessageType, "msg 8 type");
    harness.softAssert((msgList[8] as SmallMessages.IntMessage).intMember == intMsgB.intMember, "msg 8 content");

    harness.softAssert(msgList[9].getMessageType() == SmallMessages.MessageType.IntMessageType, "msg 9 type");
    harness.softAssert((msgList[9] as SmallMessages.IntMessage).intMember == intMsgB.intMember, "msg 9 content");

    harness.softAssert(msgList[10].getMessageType() == SmallMessages.MessageType.IntMessageType, "msg 10 type");
    harness.softAssert((msgList[10] as SmallMessages.IntMessage).intMember == intMsgA.intMember, "msg 10 content");

    harness.softAssert(msgList[11].getMessageType() == SmallMessages.MessageType.EmptyMessageType, "msg 11 type");
}
