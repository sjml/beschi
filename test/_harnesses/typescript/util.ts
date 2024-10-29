import minimist from "minimist";

export function runTest(
    generateFunc: (filePath: string, assertionFunc: (condition: boolean, label: string) => void) => void,
    readFunc:     (filePath: string, assertionFunc: (condition: boolean, label: string) => void) => void
    ) {
    let ok: boolean = true;
    function softAssert(condition: boolean, label: string) {
        if (!condition) {
            console.error("FAILED! TypeScript: " + label);
            ok = false;
        }
    }

    const args = minimist(process.argv.slice(2));

    if (args["generate"]) {
        generateFunc(args["generate"], softAssert);
    }
    else if (args["read"]) {
        readFunc(args["read"], softAssert);
    }

    if (!ok) {
        console.error("Failed assertions");
        process.exit(1);
    }
}

// separated these out in the hopes that I could have this
//   work with Deno, but that proved more complex than just
//   isolating the node library calls.
import * as fs from 'fs';
import * as path from 'path';

export function getDataView(filePath: string): DataView {
    const data = fs.readFileSync(filePath);
    return new DataView(new Uint8Array(data).buffer);
}

export function writeBuffer(buffer: Buffer, filePath: string) {
    const dir = path.dirname(filePath);
    if (!fs.existsSync(dir)) {
        fs.mkdirSync(dir);
    }
    fs.writeFileSync(filePath, buffer);
}

