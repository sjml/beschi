import * as harness from "./_harness";
export * from "./_harness";

import * as ComprehensiveMessage from '../../../../out/generated/assemblyscript/ComprehensiveMessage';

const example = new ComprehensiveMessage.TestingMessage();


export function generate(): usize {
    let size: usize = example.getSizeInBytes();

    harness.allocate(size);
    const dv = harness.getDataView();

    let success: bool = example.writeBytes(dv, false);
    harness.softAssert(success == true, "written bytes check");

    return harness.getDataPtr();
}

export function read(): void {
    const dv = harness.getDataView();

    const input = ComprehensiveMessage.TestingMessage.fromBytes(dv);
    harness.softAssert(input !== null, "parsing test message");
}
