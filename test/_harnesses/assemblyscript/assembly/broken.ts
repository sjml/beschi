import * as harness from "./_harness";
export * from "./_harness";

import * as BrokenMessages from '../../../../out/generated/assemblyscript/BrokenMessages';

const broken = new BrokenMessages.TruncatedMessage();
broken.x = 1.0;
broken.y = 2.0;

export function generate(): usize {
    const byteLen = broken.getSizeInBytes();
    harness.allocate(byteLen);
    const dv = harness.getDataView();
    const success = broken.writeBytes(dv, false);
    harness.softAssert(success == true, "writing broken message");

    return harness.getDataPtr();
}

export function read(): void {
    const dv = harness.getDataView();
    const input = BrokenMessages.FullMessage.fromBytes(dv);

    harness.softAssert(input == null, "reading broken message");
}
