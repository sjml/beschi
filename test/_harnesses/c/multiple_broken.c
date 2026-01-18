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

    BrokenMessages_TruncatedMessage trunc = BrokenMessages_TruncatedMessage_default;
    trunc.x = 1.0f;
    trunc.y = 2.0f;

    BrokenMessages_FullMessage full = BrokenMessages_FullMessage_default;
    full.x = 1.0f;
    full.y = 2.0f;
    full.z = 3.0f;


    size_t bufferSize;
    BrokenMessages_err_t err = BROKENMESSAGES_ERR_OK;
    uint8_t* buffer = NULL;
    FILE* fp = NULL;

    if (genPath != 0) {
        bufferSize = 0;
        size_t s;
        BrokenMessages_FullMessage_GetSizeInBytes(&full, &s);
        bufferSize += s * 6;
        BrokenMessages_TruncatedMessage_GetSizeInBytes(&trunc, &s);
        bufferSize += s;
        bufferSize += 7;

        buffer = (uint8_t*)malloc(bufferSize);
        BrokenMessages_DataAccess writer = {.buffer = buffer, .bufferSize = bufferSize, .position = 0};
        err = BrokenMessages_FullMessage_WriteBytes(&writer, &full, true);
        if (err != BROKENMESSAGES_ERR_OK) { return err; }
        err = BrokenMessages_FullMessage_WriteBytes(&writer, &full, true);
        if (err != BROKENMESSAGES_ERR_OK) { return err; }
        err = BrokenMessages_FullMessage_WriteBytes(&writer, &full, true);
        if (err != BROKENMESSAGES_ERR_OK) { return err; }

        // write a truncated message tagged as a full one
        const uint8_t id = (uint8_t)full._mt;
        err = BrokenMessages_WriteUInt8(&writer, id);
        if (err != BROKENMESSAGES_ERR_OK) { return err; }
        err = BrokenMessages_TruncatedMessage_WriteBytes(&writer, &trunc, false);
        if (err != BROKENMESSAGES_ERR_OK) { return err; }

        err = BrokenMessages_FullMessage_WriteBytes(&writer, &full, true);
        if (err != BROKENMESSAGES_ERR_OK) { return err; }
        err = BrokenMessages_FullMessage_WriteBytes(&writer, &full, true);
        if (err != BROKENMESSAGES_ERR_OK) { return err; }
        err = BrokenMessages_FullMessage_WriteBytes(&writer, &full, true);
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

        // redundant here...
        softAssert(bufferSize == ret, "written bytes check");

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
        void** msgList = NULL;
        size_t msgListLen = 0;
        err = BrokenMessages_ProcessRawBytes(&reader, -1, &msgList, &msgListLen);
        free(buffer);

        softAssert(err == BROKENMESSAGES_ERR_INVALID_DATA, "read broken stream error");
        softAssert(msgListLen == 4, "read broken stream length");

        BrokenMessages_DestroyMessageList(msgList, msgListLen);
    }

    return check();
}
