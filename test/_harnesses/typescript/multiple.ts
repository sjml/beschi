import { getDataView, writeBuffer, runTest } from "./util";

import * as SmallMessages from '../../../out/generated/typescript/SmallMessages';

// including here to check that namespacing works
import * as Nested from '../../../out/generated/typescript/Nested';

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
longMsg.intMember = 2147483647n + 10n; // (2^31 - 1) + 10


function generate(filePath: string, softAssert: (condition: boolean, label: string) => void) {
    let size = 0;
    size += byteMsg.getSizeInBytes();
    size += intMsgA.getSizeInBytes() * 3;
    size += intMsgB.getSizeInBytes() * 4;
    size += emptyMsg.getSizeInBytes() * 2;
    size += longMsg.getSizeInBytes();
    size += floatMsg.getSizeInBytes();
    size += 12;

    const data = new ArrayBuffer(size);
    const da = new SmallMessages.DataAccess(data);

    byteMsg.writeBytes(da, true);   //  0
    intMsgA.writeBytes(da, true);   //  1
    intMsgB.writeBytes(da, true);   //  2
    emptyMsg.writeBytes(da, true);  //  3
    longMsg.writeBytes(da, true);   //  4
    floatMsg.writeBytes(da, true);  //  5
    intMsgA.writeBytes(da, true);   //  6
    intMsgB.writeBytes(da, true);   //  7
    intMsgB.writeBytes(da, true);   //  8
    intMsgB.writeBytes(da, true);   //  9
    intMsgA.writeBytes(da, true);   // 10
    emptyMsg.writeBytes(da, true);  // 11

    writeBuffer(Buffer.from(data, 0, da.currentOffset), filePath);

    softAssert(size == da.currentOffset, "written bytes check");
}

function read(filePath: string, softAssert: (condition: boolean, label: string) => void) {
    const dv = getDataView(filePath);

    const msgList = SmallMessages.ProcessRawBytes(dv);

    softAssert(msgList.length == 12, "reading multiple messages length");

    softAssert(msgList[0].getMessageType() == SmallMessages.MessageType.ByteMessageType, "msg 0 type");
    softAssert((msgList[0] as SmallMessages.ByteMessage).byteMember == byteMsg.byteMember, "msg 0 content");

    softAssert(msgList[1].getMessageType() == SmallMessages.MessageType.IntMessageType, "msg 1 type");
    softAssert((msgList[1] as SmallMessages.IntMessage).intMember == intMsgA.intMember, "msg 1 content");

    softAssert(msgList[2].getMessageType() == SmallMessages.MessageType.IntMessageType, "msg 2 type");
    softAssert((msgList[2] as SmallMessages.IntMessage).intMember == intMsgB.intMember, "msg 2 content");

    softAssert(msgList[3].getMessageType() == SmallMessages.MessageType.EmptyMessageType, "msg 3 type");

    softAssert(msgList[4].getMessageType() == SmallMessages.MessageType.LongMessageType, "msg 4 type");
    softAssert((msgList[4] as SmallMessages.LongMessage).intMember == longMsg.intMember, "msg 4 content");

    softAssert(msgList[5].getMessageType() == SmallMessages.MessageType.FloatMessageType, "msg 5 type");
    softAssert((msgList[5] as SmallMessages.FloatMessage).floatMember == Math.fround(floatMsg.floatMember), "msg 5 content");

    softAssert(msgList[6].getMessageType() == SmallMessages.MessageType.IntMessageType, "msg 6 type");
    softAssert((msgList[6] as SmallMessages.IntMessage).intMember == intMsgA.intMember, "msg 6 content");

    softAssert(msgList[7].getMessageType() == SmallMessages.MessageType.IntMessageType, "msg 7 type");
    softAssert((msgList[7] as SmallMessages.IntMessage).intMember == intMsgB.intMember, "msg 7 content");

    softAssert(msgList[8].getMessageType() == SmallMessages.MessageType.IntMessageType, "msg 8 type");
    softAssert((msgList[8] as SmallMessages.IntMessage).intMember == intMsgB.intMember, "msg 8 content");

    softAssert(msgList[9].getMessageType() == SmallMessages.MessageType.IntMessageType, "msg 9 type");
    softAssert((msgList[9] as SmallMessages.IntMessage).intMember == intMsgB.intMember, "msg 9 content");

    softAssert(msgList[10].getMessageType() == SmallMessages.MessageType.IntMessageType, "msg 10 type");
    softAssert((msgList[10] as SmallMessages.IntMessage).intMember == intMsgA.intMember, "msg 10 content");

    softAssert(msgList[11].getMessageType() == SmallMessages.MessageType.EmptyMessageType, "msg 11 type");
}

runTest(generate, read);
