#include <stdlib.h>
#include <stdio.h>
#include <stddef.h>

#include "util.h"

#define BROKENMESSAGES_IMPLEMENTATION
#include "BrokenMessages.h"

#ifdef _MSC_VER
    // don't care about deprecations in the test harness code
    #pragma warning(disable : 4996)
#endif

int main(int argc, char** argv) {
    char* genPath = NULL;
    char* readPath = NULL;
    parseArgs(argc, argv, &genPath, &readPath);

    BrokenMessages_TruncatedMessage broken = BrokenMessages_TruncatedMessage_default;
    broken.x = 1.0f;
    broken.y = 2.0f;

    size_t bufferSize;
    BrokenMessages_err_t err = BROKENMESSAGES_ERR_OK;
    uint8_t* buffer = NULL;
    FILE* fp = NULL;

    if (genPath != 0) {
        err = BrokenMessages_TruncatedMessage_GetSizeInBytes(&broken, &bufferSize);
        if (err != BROKENMESSAGES_ERR_OK) { return err; }

        buffer = (uint8_t*)malloc(bufferSize);
        BrokenMessages_DataAccess writer = {.buffer = buffer, .bufferSize = bufferSize, .position = 0};
        err = BrokenMessages_TruncatedMessage_WriteBytes(&writer, &broken, false);
        if (err != BROKENMESSAGES_ERR_OK) { return err; }

        fp = fopen(genPath, "wb");
        if (fp == NULL) {
            fprintf(stderr, "ERROR: Couldn't open %s\n", genPath);
            exit(1);
        }
        size_t ret = fwrite(buffer, 1, bufferSize, fp);
        if (ret != bufferSize) {
            fprintf(stderr, "ERROR: Couldn't write to %s\n", genPath);
            exit(1);
        }
        fclose(fp);

        free(buffer);

        printf("fwrite count: %zu\nerror: %d\nbuffer size: %zu\n", ret, err, bufferSize);
        printf("written to: %s\n", genPath);
    }

    else if (readPath != NULL) {
        fp = fopen(readPath, "rb");
        fseek(fp, 0, SEEK_END);
        bufferSize = (size_t)ftell(fp);
        rewind(fp);
        buffer = (uint8_t*)malloc(bufferSize);
        size_t ret = fread(buffer, 1, bufferSize, fp);
        fclose(fp);

        if (ret != bufferSize) {
            fprintf(stderr, "ERROR: Couldn't read %s\n", readPath);
            exit(1);
        }

        BrokenMessages_DataAccess reader = {.buffer = buffer, .bufferSize = bufferSize, .position = 0};
        BrokenMessages_FullMessage* input = (BrokenMessages_FullMessage*)malloc(sizeof(BrokenMessages_FullMessage));
        err = BrokenMessages_FullMessage_FromBytes(&reader, input);

        softAssert(err == BROKENMESSAGES_ERR_EOF, "reading broken message");

        BrokenMessages_FullMessage_Destroy(input);

        free(buffer);
    }

    return check();
}
