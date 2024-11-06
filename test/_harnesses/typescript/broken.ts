import { getDataView, writeBuffer, runTest } from "./util";

import * as BrokenMessages from '../../../out/generated/typescript/BrokenMessages';

const broken = new BrokenMessages.TruncatedMessage();
broken.x = 1.0;
broken.y = 2.0;

function generate(filePath: string, softAssert: (condition: boolean, label: string) => void) {
    const data = new ArrayBuffer(broken.getSizeInBytes());
    const da = new BrokenMessages.DataAccess(data);
    broken.writeBytes(da, false);

    writeBuffer(Buffer.from(data, 0, da.currentOffset), filePath);

    softAssert(broken.getSizeInBytes() == da.currentOffset, "written bytes check");
}

function read(filePath: string, softAssert: (condition: boolean, label: string) => void) {
    const dv = getDataView(filePath);
    let errMsg: string;
    try {
        const input = BrokenMessages.FullMessage.fromBytes(dv);
    }
    catch (e) {
        errMsg = e.message;
    }

    softAssert(errMsg === "Could not read FullMessage from offset 8 (RangeError -- Offset is outside the bounds of the DataView)", "reading broken message");
}


runTest(generate, read);
