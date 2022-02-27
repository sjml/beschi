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

int main(int argc, char** argv) {
    char* genPath = NULL;
    char* readPath = NULL;
    parseArgs(argc, argv, &genPath, &readPath);

    SmallMessages_EmptyMessage emptyMsg = SmallMessages_EmptyMessage_default;
    SmallMessages_ByteMessage byteMsg = SmallMessages_ByteMessage_default;
    byteMsg.byteMember = 242;
    SmallMessages_IntMessage intMsgA = SmallMessages_IntMessage_default;
    intMsgA.intMember = -42;
    SmallMessages_IntMessage intMsgB = SmallMessages_IntMessage_default;
    intMsgB.intMember = 2048;
    SmallMessages_FloatMessage floatMsg = SmallMessages_FloatMessage_default;
    floatMsg.floatMember = 1234.5678f;
    SmallMessages_LongMessage longMsg = SmallMessages_LongMessage_default;
    longMsg.intMember = (int64_t)2147483647L + 10;


    size_t bufferSize;
    SmallMessages_err_t err = SMALLMESSAGES_ERR_OK;
    uint8_t* buffer = NULL;
    FILE* fp = NULL;

    if (genPath != 0) {
        bufferSize = 0;
        size_t s;
        SmallMessages_ByteMessage_GetSizeInBytes(&byteMsg, &s);
        bufferSize += s;
        SmallMessages_IntMessage_GetSizeInBytes(&intMsgA, &s);
        bufferSize += s * 3;
        SmallMessages_IntMessage_GetSizeInBytes(&intMsgB, &s);
        bufferSize += s * 4;
        SmallMessages_EmptyMessage_GetSizeInBytes(&emptyMsg, &s);
        bufferSize += s * 2;
        SmallMessages_LongMessage_GetSizeInBytes(&longMsg, &s);
        bufferSize += s;
        SmallMessages_FloatMessage_GetSizeInBytes(&floatMsg, &s);
        bufferSize += s;
        bufferSize += 12;

        buffer = (uint8_t*)malloc(bufferSize);
        SmallMessages_DataAccess writer = {.buffer = buffer, .bufferSize = bufferSize, .position = 0};
        err = SmallMessages_ByteMessage_WriteBytes(&writer, &byteMsg, true);
        SMALLMESSAGES_ERR_CHECK_RETURN;
        err = SmallMessages_IntMessage_WriteBytes(&writer, &intMsgA, true);
        SMALLMESSAGES_ERR_CHECK_RETURN;
        err = SmallMessages_IntMessage_WriteBytes(&writer, &intMsgB, true);
        SMALLMESSAGES_ERR_CHECK_RETURN;
        err = SmallMessages_EmptyMessage_WriteBytes(&writer, &emptyMsg, true);
        SMALLMESSAGES_ERR_CHECK_RETURN;
        err = SmallMessages_LongMessage_WriteBytes(&writer, &longMsg, true);
        SMALLMESSAGES_ERR_CHECK_RETURN;
        err = SmallMessages_FloatMessage_WriteBytes(&writer, &floatMsg, true);
        SMALLMESSAGES_ERR_CHECK_RETURN;
        err = SmallMessages_IntMessage_WriteBytes(&writer, &intMsgA, true);
        SMALLMESSAGES_ERR_CHECK_RETURN;
        err = SmallMessages_IntMessage_WriteBytes(&writer, &intMsgB, true);
        SMALLMESSAGES_ERR_CHECK_RETURN;
        err = SmallMessages_IntMessage_WriteBytes(&writer, &intMsgB, true);
        SMALLMESSAGES_ERR_CHECK_RETURN;
        err = SmallMessages_IntMessage_WriteBytes(&writer, &intMsgB, true);
        SMALLMESSAGES_ERR_CHECK_RETURN;
        err = SmallMessages_IntMessage_WriteBytes(&writer, &intMsgA, true);
        SMALLMESSAGES_ERR_CHECK_RETURN;
        err = SmallMessages_EmptyMessage_WriteBytes(&writer, &emptyMsg, true);
        SMALLMESSAGES_ERR_CHECK_RETURN;

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

        SmallMessages_DataAccess reader = {.buffer = buffer, .bufferSize = bufferSize, .position = 0};
        void** msgList = NULL;
        size_t msgListLen = 0;
        err = SmallMessages_ProcessRawBytes(&reader, &msgList, &msgListLen);
        SMALLMESSAGES_ERR_CHECK_RETURN;
        free(buffer);

        softAssert(msgListLen == 12, "reading multiple messages length");

        softAssert(SmallMessages_GetMessageType(msgList[0]) == SmallMessages_MessageType_ByteMessage, "msg 0 type");
        softAssert(((SmallMessages_ByteMessage*)(msgList[0]))->byteMember == byteMsg.byteMember, "msg 0 content");

        softAssert(SmallMessages_GetMessageType(msgList[1]) == SmallMessages_MessageType_IntMessage, "msg 1 type");
        softAssert(((SmallMessages_IntMessage*)(msgList[1]))->intMember == intMsgA.intMember, "msg 1 content");

        softAssert(SmallMessages_GetMessageType(msgList[2]) == SmallMessages_MessageType_IntMessage, "msg 2 type");
        softAssert(((SmallMessages_IntMessage*)(msgList[2]))->intMember == intMsgB.intMember, "msg 2 content");

        softAssert(SmallMessages_GetMessageType(msgList[3]) == SmallMessages_MessageType_EmptyMessage, "msg 3 type");

        softAssert(SmallMessages_GetMessageType(msgList[4]) == SmallMessages_MessageType_LongMessage, "msg 4 type");
        softAssert(((SmallMessages_LongMessage*)(msgList[4]))->intMember == longMsg.intMember, "msg 4 content");

        softAssert(SmallMessages_GetMessageType(msgList[5]) == SmallMessages_MessageType_FloatMessage, "msg 5 type");
        softAssert(((SmallMessages_FloatMessage*)(msgList[5]))->floatMember == floatMsg.floatMember, "msg 5 content");

        softAssert(SmallMessages_GetMessageType(msgList[6]) == SmallMessages_MessageType_IntMessage, "msg 6 type");
        softAssert(((SmallMessages_IntMessage*)(msgList[6]))->intMember == intMsgA.intMember, "msg 6 content");

        softAssert(SmallMessages_GetMessageType(msgList[7]) == SmallMessages_MessageType_IntMessage, "msg 7 type");
        softAssert(((SmallMessages_IntMessage*)(msgList[7]))->intMember == intMsgB.intMember, "msg 7 content");

        softAssert(SmallMessages_GetMessageType(msgList[8]) == SmallMessages_MessageType_IntMessage, "msg 8 type");
        softAssert(((SmallMessages_IntMessage*)(msgList[8]))->intMember == intMsgB.intMember, "msg 8 content");

        softAssert(SmallMessages_GetMessageType(msgList[9]) == SmallMessages_MessageType_IntMessage, "msg 9 type");
        softAssert(((SmallMessages_IntMessage*)(msgList[9]))->intMember == intMsgB.intMember, "msg 9 content");

        softAssert(SmallMessages_GetMessageType(msgList[10]) == SmallMessages_MessageType_IntMessage, "msg 10 type");
        softAssert(((SmallMessages_IntMessage*)(msgList[10]))->intMember == intMsgA.intMember, "msg 10 content");

        softAssert(SmallMessages_GetMessageType(msgList[11]) == SmallMessages_MessageType_EmptyMessage, "msg 11 type");

        SmallMessages_DestroyMessageList(msgList, msgListLen);
    }

    return check();
}
