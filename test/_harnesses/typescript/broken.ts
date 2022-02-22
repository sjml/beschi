import { getDataView, writeBuffer, runTest } from "./util";

import * as BrokenMessages from '../../../out/generated/typescript/BrokenMessages';

const broken = new BrokenMessages.TruncatedMessage();
broken.x = 1.0;
broken.y = 2.0;

function generate(filePath: string, softAssert: (condition: boolean, label: string) => void) {
    const data = new ArrayBuffer(broken.GetSizeInBytes());
    const dv = new DataView(data);
    const offset = broken.WriteBytes(dv, false, 0);

    writeBuffer(Buffer.from(data, 0, offset), filePath);

    softAssert(broken.GetSizeInBytes() == offset, "written bytes check");
}

function read(filePath: string, softAssert: (condition: boolean, label: string) => void) {
    const dv = getDataView(filePath);
    const input = BrokenMessages.FullMessage.FromBytes(dv, 0).val;

    softAssert(input == null, "reading broken message");
}


runTest(generate, read);
