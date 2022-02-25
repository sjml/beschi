#include <stdio.h>
#include <string.h>
#include <stdlib.h>
#include <stdbool.h>

static bool OK = true;
static void softAssert(bool condition, const char* label) {
    if (!condition) {
        fprintf(stderr, "FAILED! C: %s\n", label);
        OK = false;
    }
}

static int check() {
    if (!OK) {
        fprintf(stderr, "Failed assertions.\n");
        return 1;
    }
    return 0;
}

static int parseArgs(int argc, char** argv, char** genPath, char** readPath) {
    for (int ai = 0; ai < argc; ai++) {
        if (strcmp("--generate", argv[ai]) == 0) {
            if (argc <= ai+1) {
                fprintf(stderr, "ERROR: No generate filename given.\n");
                return 1;
            }
            *genPath = argv[ai+1];
            break;
        }
        if (strcmp("--read", argv[ai]) == 0) {
            if (argc <= ai+1) {
                fprintf(stderr, "ERROR: No read filename given.\n");
                return 1;
            }
            *readPath = argv[ai+1];
            break;
        }
    }
    return 0;
}
