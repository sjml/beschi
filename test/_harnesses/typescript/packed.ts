import fs from "fs";
import { getDataView, writeBuffer, runTest } from "./util";

import * as SmallMessages from '../../../out/generated/typescript/SmallMessages';

const msgList: SmallMessages.Message[] = [
    new SmallMessages.IntMessage(),
    new SmallMessages.FloatMessage(),
    new SmallMessages.FloatMessage(),
    new SmallMessages.FloatMessage(),
    new SmallMessages.IntMessage(),
    new SmallMessages.EmptyMessage(),
    new SmallMessages.LongMessage(),
    new SmallMessages.LongMessage(),
    new SmallMessages.LongMessage(),
    new SmallMessages.IntMessage(),
];


function generate(filePath: string, softAssert: (condition: boolean, label: string) => void) {
    const size = SmallMessages.GetPackedSize(msgList);
    const data = new ArrayBuffer(size);
    const da = new SmallMessages.DataAccess(data);
    SmallMessages.PackMessages(msgList, da);

    writeBuffer(Buffer.from(data, 0, da.currentOffset), filePath);

    softAssert(da.currentOffset == 67, "written bytes check");
}

function read(filePath: string, softAssert: (condition: boolean, label: string) => void) {
    const dv = getDataView(filePath);

    const unpacked = SmallMessages.UnpackMessages(dv);

    softAssert(unpacked.length == 10, "packed count");

    softAssert(unpacked[0].getMessageType() == SmallMessages.MessageType.IntMessageType,   "packed[0]");
    softAssert(unpacked[1].getMessageType() == SmallMessages.MessageType.FloatMessageType, "packed[1]");
    softAssert(unpacked[2].getMessageType() == SmallMessages.MessageType.FloatMessageType, "packed[2]");
    softAssert(unpacked[3].getMessageType() == SmallMessages.MessageType.FloatMessageType, "packed[3]");
    softAssert(unpacked[4].getMessageType() == SmallMessages.MessageType.IntMessageType,   "packed[4]");
    softAssert(unpacked[5].getMessageType() == SmallMessages.MessageType.EmptyMessageType, "packed[5]");
    softAssert(unpacked[6].getMessageType() == SmallMessages.MessageType.LongMessageType,  "packed[6]");
    softAssert(unpacked[7].getMessageType() == SmallMessages.MessageType.LongMessageType,  "packed[7]");
    softAssert(unpacked[8].getMessageType() == SmallMessages.MessageType.LongMessageType,  "packed[8]");
    softAssert(unpacked[9].getMessageType() == SmallMessages.MessageType.IntMessageType,   "packed[9]");
}

runTest(generate, read);
