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

    const fullOffest = da.currentOffset;
    da.currentOffset = 4;
    da.setByte(15);

    writeBuffer(Buffer.from(data, 0, fullOffest), filePath);
}

function read(filePath: string, softAssert: (condition: boolean, label: string) => void) {
    const dv = getDataView(filePath);

    let errMsg: string;
    try {
        const unpacked = SmallMessages.UnpackMessages(dv);
    }
    catch (e) {
        errMsg = e.message;
    }

    softAssert(errMsg == "Unexpected number of messages in buffer.", "broken unpack error");
}

runTest(generate, read);
