import * as harness from "./_harness";
export * from "./_harness";

import * as SmallMessages from '../../../../out/generated/assemblyscript/SmallMessages';


const msgList: SmallMessages.Message[] = [
    new SmallMessages.IntMessage(),
    new SmallMessages.FloatMessage(),
    new SmallMessages.FloatMessage(),
    new SmallMessages.FloatMessage(),
    new SmallMessages.IntMessage(),
    new SmallMessages.EmptyMessage(),
    new SmallMessages.LongMessage(),
    new SmallMessages.LongMessage(),
    new SmallMessages.LongMessage(),
    new SmallMessages.IntMessage(),
];


export function generate(): usize {
    let size = SmallMessages.GetPackedSize(msgList);

    harness.allocate(size);
    const dv = harness.getDataView();
    SmallMessages.PackMessages(msgList, dv);
    dv.setUint8(4, 15);

    return harness.getDataPtr();
}

export function read(): void {
    const dv = harness.getDataView();

    harness.expectAbort("Unexpected number of messages in buffer.");
    const unpacked = SmallMessages.UnpackMessages(dv);
}
