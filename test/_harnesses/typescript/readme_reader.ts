import * as fs from 'fs';

import * as AppMessages from '../../../out/generated/typescript/AppMessages';

const data = fs.readFileSync("./vec3.msg");
const dv = new DataView(new Uint8Array(data).buffer);
const msg = AppMessages.Vector3Message.FromBytes(dv, 0).val;
if (msg.y == Math.fround(4096.1234)) {
    console.log("Ready to go!");
}
