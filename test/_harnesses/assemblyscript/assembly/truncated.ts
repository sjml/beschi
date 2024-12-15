import * as harness from "./_harness";
export * from "./_harness";

import * as BrokenMessages from '../../../../out/generated/assemblyscript/BrokenMessages';

const lmsg = new BrokenMessages.ListMessage();
lmsg.ints = [1, 2, 32767, 4, 5];

export function generate(): usize {
    const msgLen = 14;
    harness.allocate(msgLen);
    const dv = harness.getDataView();
    const success = lmsg.writeBytes(dv, false);
    harness.softAssert(success == true, "writing broken message");

    dv.setUint8(0, 0xFF);

    return harness.getDataPtr();
}

export function read(): void {
    const dv = harness.getDataView();
    const input = BrokenMessages.ListMessage.fromBytes(dv);

    harness.softAssert(input == null, "reading truncated message");
}
