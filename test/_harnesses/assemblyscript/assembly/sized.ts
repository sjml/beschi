import * as harness from "./_harness";
export * from "./_harness";

import * as SizedMessage from '../../../../out/generated/assemblyscript/SizedMessage';

const shortList = new SizedMessage.TextContainer();
shortList.label = "list that fits in a byte";
shortList.collection = [
    "Lorem", "ipsum", "dolor", "sit", "amet", "consectetur",
    "adipiscing", "elit", "sed", "do", "eiusmod", "tempor",
    "incididunt", "ut", "labore", "et", "dolore", "magna",
    "aliqua", "Ut", "enim", "ad", "minim", "veniam",
    "quis", "nostrud", "exercitation", "ullamco", "laboris", "nisi",
    "ut", "aliquip", "ex", "ea", "commodo", "consequat",
    "Duis", "aute", "irure", "dolor", "in", "reprehenderit",
    "in", "voluptate", "velit", "esse", "cillum", "dolore",
    "eu", "fugiat", "nulla", "pariatur", "Excepteur", "sint",
    "occaecat", "cupidatat", "non", "proident", "sunt", "in",
    "culpa", "qui", "officia", "deserunt", "mollit", "anim",
    "id", "est", "laborum",
];

export function generate(): usize {
    let size: usize = shortList.getSizeInBytes();
    harness.softAssert(size == 464, "short list size calculation check");

    harness.allocate(size);
    const dv = harness.getDataView();

    let success: bool = shortList.writeBytes(dv, false);
    harness.softAssert(success == true, "written bytes check");

    return harness.getDataPtr();
}

export function read(): void {
    const dv = harness.getDataView();

    const input = SizedMessage.TextContainer.fromBytes(dv);
    harness.softAssert(input !== null, "readback");
    harness.softAssert(input!.label == shortList.label, "readback label comparison");
    harness.softAssert(input!.collection.length == shortList.collection.length, "readback list length");
    for (let i = 0; i < input!.collection.length; i++) {
        harness.softAssert(input!.collection[i] == shortList.collection[i], "short list comparison");
    }
}
