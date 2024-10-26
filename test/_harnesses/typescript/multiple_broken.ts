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
    const da = new BrokenMessages.DataAccess(data);

    full.WriteBytes(da, true);
    full.WriteBytes(da, true);
    full.WriteBytes(da, true);

    // write a truncated message tagged as a full one
    da.buffer.setUint8(da.currentOffset, BrokenMessages.MessageType.FullMessageType);
    da.currentOffset += 1;
    trunc.WriteBytes(da, false);

    full.WriteBytes(da, true);
    full.WriteBytes(da, true);
    full.WriteBytes(da, true);

    writeBuffer(Buffer.from(data, 0, da.currentOffset), filePath);

    softAssert(size == da.currentOffset, "written bytes check");
}

function read(filePath: string, softAssert: (condition: boolean, label: string) => void) {
    const dv = getDataView(filePath);
    let errMsg: string;
    try {
        const msgList = BrokenMessages.ProcessRawBytes(dv);
    }
    catch (e) {
        errMsg = e.message;
    }

    softAssert(errMsg === "Invalid message type found: 63", "read broken stream");
}

runTest(generate, read);
