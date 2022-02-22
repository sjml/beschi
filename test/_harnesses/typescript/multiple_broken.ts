import { getDataView, writeBuffer, runTest } from "./util";

import * as BrokenMessages from '../../../out/generated/typescript/BrokenMessages';


const trunc = new BrokenMessages.TruncatedMessage();
trunc.x = 1.0;
trunc.y = 2.0;

const full = new BrokenMessages.FullMessage();
full.x = 1.0;
full.y = 2.0;
full.z = 3.0;


function generate(filePath: string, softAssert: (condition: boolean, label: string) => void) {
    let size = 6 * full.GetSizeInBytes();
    size += 6; // markers, one byte each
    size += trunc.GetSizeInBytes();
    size += 1; // trunc marker

    const data = new ArrayBuffer(size);
    const dv = new DataView(data);
    let offset = 0;


    offset = full.WriteBytes(dv, true, offset);
    offset = full.WriteBytes(dv, true, offset);
    offset = full.WriteBytes(dv, true, offset);

    // write a truncated message tagged as a full one
    dv.setUint8(offset, BrokenMessages.MessageType.FullMessageType);
    offset += 1;
    offset = trunc.WriteBytes(dv, false, offset);

    offset = full.WriteBytes(dv, true, offset);
    offset = full.WriteBytes(dv, true, offset);
    offset = full.WriteBytes(dv, true, offset);

    writeBuffer(Buffer.from(data, 0, offset), filePath);

    softAssert(size == offset, "written bytes check");
}

function read(filePath: string, softAssert: (condition: boolean, label: string) => void) {
    const dv = getDataView(filePath);

    const msgList = BrokenMessages.ProcessRawBytes(dv, 0).vals;

    softAssert(msgList.length == 5, "read broken stream length");
    softAssert(msgList[4] == null, "read broken stream null sentinel");
}

runTest(generate, read);
