// @ts-ignore: decorator
@external("env", "softAssert")
export declare function softAssert(condition: boolean, label: string): void;

// @ts-ignore: decorator
@external("env", "expectAbort")
export declare function expectAbort(errMsg: string): void;

// @ts-ignore: decorator
@external("env", "log")
export declare function log(msg: string): void;


let data: Uint8Array|null = null;

export function allocate(size: usize): usize {
    data = new Uint8Array(size as i32);
    return data!.dataStart;
}

export function getDataView(): DataView {
    return new DataView(data!.buffer);
}

export function getDataPtr(): usize {
    if (data == null) {
        return 0;
    }
    return data!.dataStart;
}

export function getDataLen(): usize {
    if (data == null) {
        return 0;
    }
    return data!.byteLength;
}
