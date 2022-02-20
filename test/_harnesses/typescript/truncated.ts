import { getDataView, writeBuffer, runTest } from "./util";

import * as BrokenMessages from '../../../out/generated/typescript/BrokenMessages';

const lmsg = new BrokenMessages.ListMessage();
lmsg.ints = [1, 2, 32767, 4, 5];

function generate(filePath: string, softAssert: (condition: boolean, label: string) => void) {
    const data = new ArrayBuffer(16);
    const dv = new DataView(data);
    const offset = lmsg.WriteBytes(dv, 0, false);

    // tweak the buffer so the message looks longer
    dv.setUint8(0, 0xFF);

    writeBuffer(Buffer.from(data, 0, offset), filePath);
}

function read(filePath: string, softAssert: (condition: boolean, label: string) => void) {
    const dv = getDataView(filePath);
    const input = BrokenMessages.ListMessage.FromBytes(dv, 0).val;

    softAssert(input == null, "reading truncated message");
}


runTest(generate, read);
