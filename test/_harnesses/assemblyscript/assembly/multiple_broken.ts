import * as harness from "./_harness";
export * from "./_harness";

import * as BrokenMessages from '../../../../out/generated/assemblyscript/BrokenMessages';

const trunc = new BrokenMessages.TruncatedMessage();
trunc.x = 1.0;
trunc.y = 2.0;

const full = new BrokenMessages.FullMessage();
full.x = 1.0;
full.y = 2.0;
full.z = 3.0;

export function generate(): usize {
    let size: usize = 6 * full.getSizeInBytes();
    size += 6; // markers, one byte each
    size += trunc.getSizeInBytes();
    size += 1; // trunc marker

    harness.allocate(size);
    const dv = harness.getDataView();
    const da = new BrokenMessages.DataAccess(dv);

    let success: bool = true; // good vibes
    success = full.writeBytesDA(da, true);
    success = full.writeBytesDA(da, true);
    success = full.writeBytesDA(da, true);

    // write a truncated message tagged as a full one
    da.setByte(BrokenMessages.MessageType.FullMessageType as u8);
    trunc.writeBytesDA(da, false);

    success = full.writeBytesDA(da, true);
    success = full.writeBytesDA(da, true);
    success = full.writeBytesDA(da, true);

    return harness.getDataPtr();
}

export function read(): void {
    const dv = harness.getDataView();

    const msgList = BrokenMessages.ProcessRawBytes(dv, -1);

    harness.softAssert(msgList.length == 4, "read broken stream")
}
