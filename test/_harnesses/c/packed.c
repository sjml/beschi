#include <stdlib.h>
#include <stdio.h>
#include <stddef.h>

#include "util.h"

#define SMALLMESSAGES_IMPLEMENTATION
#include "SmallMessages.h"

#ifdef _MSC_VER
    // don't care about deprecations in the test harness code
    #pragma warning(disable : 4996)
#endif

static void* copyDefault(const void* def, size_t size) {
    if (def == NULL || size == 0) {
        return NULL;
    }
    void* newMsg = malloc(size);
    if (newMsg != NULL) {
        memcpy(newMsg, def, size);
    }
    return newMsg;
}

int main(int argc, char** argv) {
    char* genPath = NULL;
    char* readPath = NULL;
    parseArgs(argc, argv, &genPath, &readPath);

    void** msgList = (void**)malloc(sizeof(void*) * 10);
    msgList[0] = copyDefault(&SmallMessages_IntMessage_default, sizeof(SmallMessages_IntMessage_default));
    msgList[1] = copyDefault(&SmallMessages_FloatMessage_default, sizeof(SmallMessages_FloatMessage_default));
    msgList[2] = copyDefault(&SmallMessages_FloatMessage_default, sizeof(SmallMessages_FloatMessage_default));
    msgList[3] = copyDefault(&SmallMessages_FloatMessage_default, sizeof(SmallMessages_FloatMessage_default));
    msgList[4] = copyDefault(&SmallMessages_IntMessage_default, sizeof(SmallMessages_IntMessage_default));
    msgList[5] = copyDefault(&SmallMessages_EmptyMessage_default, sizeof(SmallMessages_EmptyMessage_default));
    msgList[6] = copyDefault(&SmallMessages_LongMessage_default, sizeof(SmallMessages_LongMessage_default));
    msgList[7] = copyDefault(&SmallMessages_LongMessage_default, sizeof(SmallMessages_LongMessage_default));
    msgList[8] = copyDefault(&SmallMessages_LongMessage_default, sizeof(SmallMessages_LongMessage_default));
    msgList[9] = copyDefault(&SmallMessages_IntMessage_default, sizeof(SmallMessages_IntMessage_default));

    size_t bufferSize;
    SmallMessages_err_t err = SMALLMESSAGES_ERR_OK;
    uint8_t* buffer = NULL;
    FILE* fp = NULL;

    if (genPath != 0) {
        err = SmallMessages_GetPackedSize(msgList, 10, &bufferSize);
        if (err != SMALLMESSAGES_ERR_OK) { return err; }
        buffer = (uint8_t*)malloc(bufferSize);

        SmallMessages_DataAccess writer = {.buffer = buffer, .bufferSize = bufferSize, .position = 0};
        err = SmallMessages_PackMessages(msgList, 10, &writer);
        if (err != SMALLMESSAGES_ERR_OK) { return err; }

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
        if (fp == NULL) {
            fprintf(stderr, "ERROR: Couldn't open %s\n", readPath);
            exit(1);
        }
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

        SmallMessages_DataAccess reader = {.buffer = buffer, .bufferSize = bufferSize, .position = 0};
        void** packed = NULL;
        size_t packedLen = 0;
        err = SmallMessages_UnpackMessages(&reader, &packed, &packedLen);
        if (err != SMALLMESSAGES_ERR_OK) { return err; }
        free(buffer);

        softAssert(packedLen == 10, "packed count");

        softAssert(SmallMessages_GetMessageType(packed[0]) == SmallMessages_MessageType_IntMessage,   "packed[0]");
        softAssert(SmallMessages_GetMessageType(packed[1]) == SmallMessages_MessageType_FloatMessage, "packed[1]");
        softAssert(SmallMessages_GetMessageType(packed[2]) == SmallMessages_MessageType_FloatMessage, "packed[2]");
        softAssert(SmallMessages_GetMessageType(packed[3]) == SmallMessages_MessageType_FloatMessage, "packed[3]");
        softAssert(SmallMessages_GetMessageType(packed[4]) == SmallMessages_MessageType_IntMessage,   "packed[4]");
        softAssert(SmallMessages_GetMessageType(packed[5]) == SmallMessages_MessageType_EmptyMessage, "packed[5]");
        softAssert(SmallMessages_GetMessageType(packed[6]) == SmallMessages_MessageType_LongMessage,  "packed[6]");
        softAssert(SmallMessages_GetMessageType(packed[7]) == SmallMessages_MessageType_LongMessage,  "packed[7]");
        softAssert(SmallMessages_GetMessageType(packed[8]) == SmallMessages_MessageType_LongMessage,  "packed[8]");
        softAssert(SmallMessages_GetMessageType(packed[9]) == SmallMessages_MessageType_IntMessage,   "packed[9]");

        SmallMessages_DestroyMessageList(packed, packedLen);
    }

    SmallMessages_DestroyMessageList(msgList, 10);
    return check();
}
