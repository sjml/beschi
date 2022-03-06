#include <stdlib.h>
#include <stdio.h>

#include "util.h"

#define COMPREHENSIVEMESSAGE_IMPLEMENTATION
#include "ComprehensiveMessage.h"

#ifdef _MSC_VER
    // don't care about deprecations in the test harness code
    #pragma warning(disable : 4996)
#endif


int main(int argc, char** argv) {
    char* genPath = NULL;
    char* readPath = NULL;
    parseArgs(argc, argv, &genPath, &readPath);

    ComprehensiveMessage_TestingMessage example = ComprehensiveMessage_TestingMessage_default;


    size_t bufferSize;
    ComprehensiveMessage_err_t err = COMPREHENSIVEMESSAGE_ERR_OK;
    uint8_t* buffer = NULL;
    FILE* fp = NULL;

    if (genPath != NULL) {
        err = ComprehensiveMessage_TestingMessage_GetSizeInBytes(&example, &bufferSize);
        if (err != COMPREHENSIVEMESSAGE_ERR_OK) { return err; }
        buffer = (uint8_t*)malloc(bufferSize);
        ComprehensiveMessage_DataAccess writer = {.buffer = buffer, .bufferSize = bufferSize, .position = 0};
        err = ComprehensiveMessage_TestingMessage_WriteBytes(&writer, &example, false);
        if (err != COMPREHENSIVEMESSAGE_ERR_OK) { return err; }

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

        ComprehensiveMessage_DataAccess reader = {.buffer = buffer, .bufferSize = bufferSize, .position = 0};
        ComprehensiveMessage_TestingMessage* input = (ComprehensiveMessage_TestingMessage*)malloc(sizeof(ComprehensiveMessage_TestingMessage));
        err = ComprehensiveMessage_TestingMessage_FromBytes(&reader, input);
        if (err != COMPREHENSIVEMESSAGE_ERR_OK) { return err; }

        softAssert(err == COMPREHENSIVEMESSAGE_ERR_OK, "parsing test message");

        softAssert(input->b == example.b, "byte");
        softAssert(input->tf == example.tf, "bool");
        softAssert(input->i16 == example.i16, "i16");
        softAssert(input->ui16 == example.ui16, "ui16");
        softAssert(input->i32 == example.i32, "i32");
        softAssert(input->ui32 == example.ui32, "ui32");
        softAssert(input->i64 == example.i64, "i64");
        softAssert(input->ui64 == example.ui64, "ui64");
        softAssert(input->f == example.f, "float");
        softAssert(input->d == example.d, "double");
        softAssert(strcmp(input->s, example.s) == 0, "string");
        softAssert(input->v2.x == example.v2.x, "Vec2");
        softAssert(input->v2.y == example.v2.y, "Vec2");
        softAssert(input->v3.x == example.v3.x, "Vec3");
        softAssert(input->v3.y == example.v3.y, "Vec3");
        softAssert(input->v3.z == example.v3.z, "Vec3");
        softAssert(input->c.r == example.c.r, "Color");
        softAssert(input->c.g == example.c.g, "Color");
        softAssert(input->c.b == example.c.b, "Color");
        softAssert(input->sl_len == example.sl_len, "[string].length");
        for (uint32_t i  = 0; i < input->sl_len; i++) {
            softAssert(input->sl_els_len[i] == example.sl_els_len[i], "[string].length");
            softAssert(memcmp(input->sl[i], example.sl[i], example.sl_els_len[i]) == 0, "[string]");
        }
        softAssert(input->v2l_len == example.v2l_len, "[Vec2].length");
        for (uint32_t i  = 0; i < input->v2l_len; i++) {
            softAssert(input->v2l[i].x == example.v2l[i].x, "[Vec2].x");
            softAssert(input->v2l[i].y == example.v2l[i].y, "[Vec2].y");
        }
        softAssert(input->v3l_len == example.v3l_len, "[Vec3].length");
        for (uint32_t i  = 0; i < input->v3l_len; i++) {
            softAssert(input->v3l[i].x == example.v3l[i].x, "[Vec3].x");
            softAssert(input->v3l[i].y == example.v3l[i].y, "[Vec3].y");
            softAssert(input->v3l[i].z == example.v3l[i].z, "[Vec3].z");
        }
        softAssert(input->cl_len == example.cl_len, "[Color].length");
        for (uint32_t i  = 0; i < input->cl_len; i++) {
            softAssert(input->cl[i].r == example.cl[i].r, "[Color].r");
            softAssert(input->cl[i].g == example.cl[i].g, "[Color].g");
            softAssert(input->cl[i].b == example.cl[i].b, "[Color].b");
        }
        softAssert(input->cx.identifier == example.cx.identifier, "ComplexData.identifier");
        softAssert(strcmp(input->cx.label, example.cx.label) == 0, "ComplexData.label");
        softAssert(input->cx.backgroundColor.r == example.cx.backgroundColor.r, "ComplexData.backgroundColor.r");
        softAssert(input->cx.backgroundColor.g == example.cx.backgroundColor.g, "ComplexData.backgroundColor.g");
        softAssert(input->cx.backgroundColor.b == example.cx.backgroundColor.b, "ComplexData.backgroundColor.b");
        softAssert(input->cx.textColor.r == example.cx.textColor.r, "ComplexData.textColor.r");
        softAssert(input->cx.textColor.g == example.cx.textColor.g, "ComplexData.textColor.g");
        softAssert(input->cx.textColor.b == example.cx.textColor.b, "ComplexData.textColor.b");
        softAssert(input->cx.spectrum_len == example.cx.spectrum_len, "ComplexData.spectrum.length");
        for (uint32_t i  = 0; i < input->cx.spectrum_len; i++) {
            softAssert(input->cx.spectrum[i].r == example.cx.spectrum[i].r, "ComplexData.spectrum.r");
            softAssert(input->cx.spectrum[i].g == example.cx.spectrum[i].g, "ComplexData.spectrum.g");
            softAssert(input->cx.spectrum[i].b == example.cx.spectrum[i].b, "ComplexData.spectrum.b");
        }
        softAssert(input->cxl_len == example.cxl_len, "[ComplexData].length");
        for (uint32_t i =0; i < input->cxl_len; i++) {
            softAssert(input->cxl[i].identifier == example.cxl[i].identifier, "[ComplexData].identifier");
            softAssert(strcmp(input->cxl[i].label, example.cxl[i].label) == 0, "[ComplexData].label");
            softAssert(input->cxl[i].backgroundColor.r == example.cxl[i].backgroundColor.r, "[ComplexData].backgroundColor.r");
            softAssert(input->cxl[i].backgroundColor.g == example.cxl[i].backgroundColor.g, "[ComplexData].backgroundColor.g");
            softAssert(input->cxl[i].backgroundColor.b == example.cxl[i].backgroundColor.b, "[ComplexData].backgroundColor.b");
            softAssert(input->cxl[i].textColor.r == example.cxl[i].textColor.r, "[ComplexData].textColor.r");
            softAssert(input->cxl[i].textColor.g == example.cxl[i].textColor.g, "[ComplexData].textColor.g");
            softAssert(input->cxl[i].textColor.b == example.cxl[i].textColor.b, "[ComplexData].textColor.b");
            softAssert(input->cxl[i].spectrum_len == example.cxl[i].spectrum_len, "[ComplexData].spectrum.length");
            for (uint32_t j = 0; j < input->cxl[i].spectrum_len; j++) {
                softAssert(input->cxl[i].spectrum[j].r == example.cxl[i].spectrum[j].r, "[ComplexData].spectrum.r");
                softAssert(input->cxl[i].spectrum[j].g == example.cxl[i].spectrum[j].g, "[ComplexData].spectrum.g");
                softAssert(input->cxl[i].spectrum[j].b == example.cxl[i].spectrum[j].b, "[ComplexData].spectrum.b");
            }
        }

        ComprehensiveMessage_TestingMessage_Destroy(input);

        free(buffer);
    }

    return check();
}
