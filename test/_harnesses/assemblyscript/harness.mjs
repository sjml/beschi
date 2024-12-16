import process from "node:process";
import path from "node:path";
import fs from "node:fs";
import { fileURLToPath } from "url";

const [, , ...params] = process.argv;
const programName = params[0];
const command = params[1];
const outFile = params[2];

const __filename = fileURLToPath(import.meta.url);
const __dirname = path.dirname(__filename);
const AS_BASE = __dirname;

const buildPath = path.join(AS_BASE, "build");
const wasmPath = path.join(buildPath, `${programName}.wasm`);
const wasmBytes = fs.readFileSync(wasmPath);
const wasmModule = await WebAssembly.compile(wasmBytes);

let ok = true;

function liftString(pointer, mem) {
    if (!pointer) return null;
    const
      end = pointer + new Uint32Array(mem.buffer)[pointer - 4 >>> 2] >>> 1,
      memoryU16 = new Uint16Array(mem.buffer);
    let
      start = pointer >>> 1,
      string = "";
    while (end - start > 1024) string += String.fromCharCode(...memoryU16.subarray(start, start += 1024));
    return string + String.fromCharCode(...memoryU16.subarray(start, end));
}

let abortMessageExpectation = null;
let receivedAbortMessage = null;
try {
    const instance = await WebAssembly.instantiate(wasmModule, {
        env: {
            abort: (msg, file, line, col) => {
                msg = liftString(msg, instance.exports.memory);
                file = liftString(file, instance.exports.memory);
                console.error(`ASSEMBLYSCRIPT FATAL ERROR: ${file}:${line}:${col}\n${msg}`);
                receivedAbortMessage = msg;
            },
            log: (msg) => {
                console.log(liftString(msg, instance.exports.memory));
            },
            softAssert: (condition, label) => {
                if (!condition) {
                    if (typeof label === "number") {
                        label = liftString(label, instance.exports.memory);
                    }
                    console.error(`FAILED! AssemblyScript: ${label}`);
                    ok = false;
                }
            },
            expectAbort: (message) => {
                abortMessageExpectation = message;
            },
        }
    });

    if (command == "--generate") {
        const dataPtr = instance.exports.generate();
        const dataLen = instance.exports.getDataLen();
        const msgBuffer = new Uint8Array(instance.exports.memory.buffer, dataPtr, dataLen);
        const dir = path.dirname(outFile);
        fs.mkdirSync(dir, { recursive: true });
        fs.writeFileSync(outFile, msgBuffer);
    }
    else if (command == "--read") {
        const msgBuffer = fs.readFileSync(outFile);
        const dataPtr = instance.exports.allocate(msgBuffer.length);
        const moduleMemory = new Uint8Array(instance.exports.memory.buffer, dataPtr, msgBuffer.length);
        moduleMemory.set(new Uint8Array(msgBuffer));
        instance.exports.read();
    }

}
catch(e) {
    if (abortMessageExpectation !== null && abortMessageExpectation === receivedAbortMessage) {
        // it failed like we expected
    }
    else {
        console.error(`WebAssembly Error: ${programName}`, e);
        process.exit(2);
    }
}

if (!ok) {
    console.error("Failed assertions.");
    process.exit(1);
}
