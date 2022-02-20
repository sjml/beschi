// separated this out in the hopes that I could have this
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

