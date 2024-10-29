import { getDataView, writeBuffer, runTest } from "./util";

import * as SizedMessage from '../../../out/generated/typescript/SizedMessage';

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

function generate(filePath: string, softAssert: (condition: boolean, label: string) => void) {
    const data = new ArrayBuffer(shortList.getSizeInBytes());
    const da = new SizedMessage.DataAccess(data);
    shortList.writeBytes(da, false);

    writeBuffer(Buffer.from(data, 0, da.currentOffset), filePath);

    softAssert(shortList.getSizeInBytes() == 464, "short list size calculation check");
    softAssert(shortList.getSizeInBytes() == da.currentOffset, "written bytes check");
}

function read(filePath: string, softAssert: (condition: boolean, label: string) => void) {
    const dv = getDataView(filePath);
    const input = SizedMessage.TextContainer.fromBytes(dv);

    softAssert(input.label == shortList.label, "readback label comparison");
    softAssert(input.collection.length == shortList.collection.length, "readback list length");
    for (let i = 0; i < input.collection.length; i++)
    {
        softAssert(input.collection[i] == shortList.collection[i], "short list comparison");
    }
}


runTest(generate, read);
