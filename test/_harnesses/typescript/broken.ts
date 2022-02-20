import * as minimist from "minimist";

import { getDataView, writeBuffer } from "./fileUtil";

import * as BrokenMessages from '../../../out/generated/typescript/BrokenMessages';

let ok: boolean = true;
function softAssert(condition: boolean, label: string) {
    if (!condition) {
        console.error("FAILED! TypeScript: " + label);
        ok = false;
    }
}

const trunc = new BrokenMessages.TruncatedMessage();
trunc.x = 1.0;
trunc.y = 2.0;

const lmsg = new BrokenMessages.ListMessage();
lmsg.ints = [1, 2, 32767, 4, 5];

const args = minimist(process.argv.slice(2));

if (args["generateBroken"]) {
    const data = new ArrayBuffer(1024);
    const dv = new DataView(data);
    const offset = trunc.WriteBytes(dv, 0);

    writeBuffer(Buffer.from(data, 0, offset), args["generateBroken"]);
}
else if (args["readBroken"]) {
    const dv = getDataView(args["readBroken"]);
    const input = BrokenMessages.FullMessage.FromBytes(dv, 0).val;

    softAssert(input == null, "reading broken message");
}

else if (args["generateTruncated"]) {
    const data = new ArrayBuffer(16);
    const dv = new DataView(data);
    const offset = lmsg.WriteBytes(dv, 0);

    // tweak the buffer so the message looks longer
    dv.setUint8(0, 0xFF);

    writeBuffer(Buffer.from(data, 0, offset), args["generateTruncated"]);
}
else if (args["readTruncated"]) {
    const dv = getDataView(args["readTruncated"]);
    const input = BrokenMessages.ListMessage.FromBytes(dv, 0).val;

    softAssert(input == null, "reading truncated message");
}

if (!ok) {
    console.error("Failed assertions");
    process.exit(1);
}
