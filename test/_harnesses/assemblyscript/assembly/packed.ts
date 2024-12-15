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

    return harness.getDataPtr();
}

export function read(): void {
    const dv = harness.getDataView();

    const unpacked = SmallMessages.UnpackMessages(dv);
    harness.softAssert(unpacked.length == 10, `packed count`);

    harness.softAssert(unpacked[0].getMessageType() == SmallMessages.MessageType.IntMessageType,   "packed[0]");
    harness.softAssert(unpacked[1].getMessageType() == SmallMessages.MessageType.FloatMessageType, "packed[1]");
    harness.softAssert(unpacked[2].getMessageType() == SmallMessages.MessageType.FloatMessageType, "packed[2]");
    harness.softAssert(unpacked[3].getMessageType() == SmallMessages.MessageType.FloatMessageType, "packed[3]");
    harness.softAssert(unpacked[4].getMessageType() == SmallMessages.MessageType.IntMessageType,   "packed[4]");
    harness.softAssert(unpacked[5].getMessageType() == SmallMessages.MessageType.EmptyMessageType, "packed[5]");
    harness.softAssert(unpacked[6].getMessageType() == SmallMessages.MessageType.LongMessageType,  "packed[6]");
    harness.softAssert(unpacked[7].getMessageType() == SmallMessages.MessageType.LongMessageType,  "packed[7]");
    harness.softAssert(unpacked[8].getMessageType() == SmallMessages.MessageType.LongMessageType,  "packed[8]");
    harness.softAssert(unpacked[9].getMessageType() == SmallMessages.MessageType.IntMessageType,   "packed[9]");

}
