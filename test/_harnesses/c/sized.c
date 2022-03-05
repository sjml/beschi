#include <stdlib.h>
#include <stdio.h>
#include <stddef.h>

#include "util.h"

#define SIZEDMESSAGE_IMPLEMENTATION
#include "SizedMessage.h"

#ifdef _MSC_VER
    // don't care about deprecations in the test harness code
    #pragma warning(disable : 4996)
#endif

int main(int argc, char** argv) {
    char* genPath = NULL;
    char* readPath = NULL;
    parseArgs(argc, argv, &genPath, &readPath);

    SizedMessage_TextContainer shortList = SizedMessage_TextContainer_default;
    shortList.label = (char*)"list that fits in a byte";
    shortList.label_len = (uint8_t)strlen(shortList.label);
    shortList.collection_len = 69;
    char* collection[69] = {
            (char*)"Lorem", (char*)"ipsum", (char*)"dolor", (char*)"sit", (char*)"amet", (char*)"consectetur",
            (char*)"adipiscing", (char*)"elit", (char*)"sed", (char*)"do", (char*)"eiusmod", (char*)"tempor",
            (char*)"incididunt", (char*)"ut", (char*)"labore", (char*)"et", (char*)"dolore", (char*)"magna",
            (char*)"aliqua", (char*)"Ut", (char*)"enim", (char*)"ad", (char*)"minim", (char*)"veniam",
            (char*)"quis", (char*)"nostrud", (char*)"exercitation", (char*)"ullamco", (char*)"laboris", (char*)"nisi",
            (char*)"ut", (char*)"aliquip", (char*)"ex", (char*)"ea", (char*)"commodo", (char*)"consequat",
            (char*)"Duis", (char*)"aute", (char*)"irure", (char*)"dolor", (char*)"in", (char*)"reprehenderit",
            (char*)"in", (char*)"voluptate", (char*)"velit", (char*)"esse", (char*)"cillum", (char*)"dolore",
            (char*)"eu", (char*)"fugiat", (char*)"nulla", (char*)"pariatur", (char*)"Excepteur", (char*)"sint",
            (char*)"occaecat", (char*)"cupidatat", (char*)"non", (char*)"proident", (char*)"sunt", (char*)"in",
            (char*)"culpa", (char*)"qui", (char*)"officia", (char*)"deserunt", (char*)"mollit", (char*)"anim",
            (char*)"id", (char*)"est", (char*)"laborum",
    };
    shortList.collection = collection;
    uint8_t* collection_els_len = (uint8_t*)malloc(69);
    for (int i=0; i < 69; i++) {
        collection_els_len[i] = (uint8_t)strlen(collection[i]);
    }
    shortList.collection_els_len = collection_els_len;

    size_t bufferSize;
    SizedMessage_err_t err = SIZEDMESSAGE_ERR_OK;
    uint8_t* buffer = NULL;
    FILE* fp = NULL;

    if (genPath != 0) {
        err = SizedMessage_TextContainer_GetSizeInBytes(&shortList, &bufferSize);
        if (err != SIZEDMESSAGE_ERR_OK) { return err; }

        buffer = (uint8_t*)malloc(bufferSize);
        SizedMessage_DataAccess writer = {.buffer = buffer, .bufferSize = bufferSize, .position = 0};
        err = SizedMessage_TextContainer_WriteBytes(&writer, &shortList, false);
        if (err != SIZEDMESSAGE_ERR_OK) { return err; }

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

        softAssert(bufferSize == 464, "short list size calculation check");
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

        SizedMessage_DataAccess reader = {.buffer = buffer, .bufferSize = bufferSize, .position = 0};
        SizedMessage_TextContainer* input = (SizedMessage_TextContainer*)malloc(sizeof(SizedMessage_TextContainer));
        err = SizedMessage_TextContainer_FromBytes(&reader, input);

        softAssert(strcmp(input->label, shortList.label) == 0, "readback label comparison");
        softAssert(input->collection_len == shortList.collection_len, "readback list length");
        for (int i = 0; i < input->collection_len; i++)
        {
            softAssert(strcmp(input->collection[i], shortList.collection[i]) == 0, "short list comparison");
        }

        SizedMessage_TextContainer_Destroy(input);

        free(buffer);
    }

    free(shortList.collection_els_len);
    return check();
}
