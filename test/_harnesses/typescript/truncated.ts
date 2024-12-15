import { getDataView, writeBuffer, runTest } from "./util";

import * as BrokenMessages from '../../../out/generated/typescript/BrokenMessages';

const lmsg = new BrokenMessages.ListMessage();
lmsg.ints = [1, 2, 32767, 4, 5];

function generate(filePath: string, softAssert: (condition: boolean, label: string) => void) {
    const msgLen = 14;
    const data = new ArrayBuffer(msgLen);
    const da = new BrokenMessages.DataAccess(data);
    lmsg.writeBytes(da, false);

    // tweak the buffer so the message looks longer
    da.data.setUint8(0, 0xFF);

    writeBuffer(Buffer.from(data, 0, da.currentOffset), filePath);
}

function read(filePath: string, softAssert: (condition: boolean, label: string) => void) {
    const dv = getDataView(filePath);
    let errMsg: string;
    try {
        const input = BrokenMessages.ListMessage.fromBytes(dv);
    }
    catch (e) {
        errMsg = e.message;
    }

    softAssert(errMsg === "Could not read ListMessage from offset 14 (RangeError -- Offset is outside the bounds of the DataView)", "reading truncated message");
}


runTest(generate, read);
