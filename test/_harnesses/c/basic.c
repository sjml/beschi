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
    example.b = 250;
    example.tf = true;
    example.i16 = -32000;
    example.ui16 = 65000;
    example.i32 = -2000000000;
    example.ui32 = 4000000000;
    example.i64 = -9000000000000000000L;
    example.ui64 = 18000000000000000000UL;
    example.f = 3.1415927410125732421875f;
    example.d = 2.718281828459045090795598298427648842334747314453125;
    example.ee = ComprehensiveMessage_Enumerated_Beta;
    example.es = ComprehensiveMessage_Specified_Negative;
    example.s = (char*)"Lorem ipsum dolor sit amet, consectetur adipiscing elit.";
    example.s_len = (uint32_t)strlen(example.s);
    example.v2.x = 256.512f;
    example.v2.y = 1024.768f;
    example.v3.x = 128.64f;
    example.v3.y = 2048.4096f;
    example.v3.z = 16.32f;
    example.c.r = 255;
    example.c.g = 128;
    example.c.b = 0;
    example.il_len = 5;
    short il[5] = { -1000, 500, 0, 750, 2000 };
    example.il = il;
    example.el_len = 6;
    ComprehensiveMessage_Specified el[6] = {
        ComprehensiveMessage_Specified_Negative,
        ComprehensiveMessage_Specified_Negative,
        ComprehensiveMessage_Specified_Positive,
        ComprehensiveMessage_Specified_Zero,
        ComprehensiveMessage_Specified_Positive,
        ComprehensiveMessage_Specified_Zero
    };
    example.el = el;
    example.sl_len = 7;
    char* sl[7] = {
        (char*)"Lorem ipsum dolor sit amet, consectetur adipiscing elit.",
        (char*)"Quisque est eros, placerat ut libero ut, pellentesque tincidunt sem.",
        (char*)"Vivamus pellentesque turpis aliquet pretium tincidunt.",
        (char*)"Nulla facilisi.",
        (char*)"🐼❤️✝️",
        (char*)"用ねぼ雪入文モ段足リフケ報通ンさーを応細めい気川ヤセ車不古6治ニフサコ悩段をご青止ぽっ期年ト量報驚テルユ役1家埋詰軟きぎ。",
        (char*)"لآخر نشجب ونستنكر هؤلاء الرجال المفتونون بنشوة اللحظة الهائمون في رغبات",
    };
    example.sl = sl;
    uint32_t sampleTextLengths[7] = {
        (uint32_t)strlen(sl[0]),
        (uint32_t)strlen(sl[1]),
        (uint32_t)strlen(sl[2]),
        (uint32_t)strlen(sl[3]),
        (uint32_t)strlen(sl[4]),
        (uint32_t)strlen(sl[5]),
        (uint32_t)strlen(sl[6]),
    };
    example.sl_els_len = sampleTextLengths;

    example.v2l_len = 4;
    ComprehensiveMessage_Vec2 v21 = { .x = 10.0f, .y = 15.0f };
    ComprehensiveMessage_Vec2 v22 = { .x = 20.0f, .y = 25.0f };
    ComprehensiveMessage_Vec2 v23 = { .x = 30.0f, .y = 35.0f };
    ComprehensiveMessage_Vec2 v24 = { .x = 40.0f, .y = 45.0f };
    ComprehensiveMessage_Vec2 v2l[4] = { v21, v22, v23, v24 };
    example.v2l = v2l;

    example.v3l_len = 4;
    ComprehensiveMessage_Vec3 v31 = { .x = 10.0f, .y = 15.0f, .z = 17.5f };
    ComprehensiveMessage_Vec3 v32 = { .x = 20.0f, .y = 25.0f, .z = 27.5f };
    ComprehensiveMessage_Vec3 v33 = { .x = 30.0f, .y = 35.0f, .z = 37.5f };
    ComprehensiveMessage_Vec3 v34 = { .x = 40.0f, .y = 45.0f, .z = 47.5f };
    ComprehensiveMessage_Vec3 v3l[4] = { v31, v32, v33, v34 };
    example.v3l = v3l;

    example.cl_len = 3;
    ComprehensiveMessage_Color c1 = { .r = 255, .g = 0, .b = 0 };
    ComprehensiveMessage_Color c2 = { .r = 0, .g = 255, .b = 0 };
    ComprehensiveMessage_Color c3 = { .r = 0, .g = 0, .b = 255 };
    ComprehensiveMessage_Color cl[3] = { c1, c2, c3 };
    example.cl = cl;

    ComprehensiveMessage_ComplexData cx;
    cx.identifier = 127;
    cx.label = (char*)"ComplexDataObject";
    cx.label_len = (uint32_t)strlen(cx.label);
    cx.backgroundColor = c1;
    cx.textColor = c2;
    cx.spectrum_len = 3;
    ComprehensiveMessage_Color cx_spectrum[3] = {c3, c2, c1};
    cx.spectrum = cx_spectrum;
    cx.ranges_len = 2;
    ComprehensiveMessage_Specified cx_ranges[2] = {
        ComprehensiveMessage_Specified_Negative,
        ComprehensiveMessage_Specified_Positive,
    };
    cx.ranges = cx_ranges;
    example.cx = cx;

    ComprehensiveMessage_ComplexData cx1;
    cx1.identifier = 255;
    cx1.label = (char*)"Complex1";
    cx1.label_len = (uint32_t)strlen(cx1.label);
    cx1.backgroundColor = c3;
    cx1.textColor = c1;
    cx1.spectrum_len = 5;
    ComprehensiveMessage_Color cx1_spectrum[5] = { c3, c2, c1, c2, c3 };
    cx1.spectrum = cx1_spectrum;
    cx1.ranges_len = 2;
    ComprehensiveMessage_Specified cx1_ranges[2] = {
        ComprehensiveMessage_Specified_Zero,
        ComprehensiveMessage_Specified_Positive,
    };
    cx1.ranges = cx1_ranges;

    ComprehensiveMessage_ComplexData cx2;
    cx2.identifier = 63;
    cx2.label = (char*)"Complex2";
    cx2.label_len = (uint32_t)strlen(cx2.label);
    cx2.backgroundColor = c1;
    cx2.textColor = c3;
    cx2.spectrum_len = 5;
    ComprehensiveMessage_Color cx2_spectrum[5] = { c1, c2, c3, c2, c1 };
    cx2.spectrum = cx2_spectrum;
    cx2.ranges_len = 2;
    ComprehensiveMessage_Specified cx2_ranges[2] = {
        ComprehensiveMessage_Specified_Negative,
        ComprehensiveMessage_Specified_Zero,
    };
    cx2.ranges = cx2_ranges;

    ComprehensiveMessage_ComplexData cxl[2] = { cx1, cx2 };
    example.cxl_len = 2;
    example.cxl = cxl;


    size_t bufferSize;
    ComprehensiveMessage_err_t err = COMPREHENSIVEMESSAGE_ERR_OK;
    uint8_t* buffer = NULL;
    FILE* fp = NULL;

    if (genPath != NULL) {
        err = ComprehensiveMessage_TestingMessage_GetSizeInBytes(&example, &bufferSize);
        softAssert(bufferSize == 956, "size calculation check");
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
        softAssert(input->ee == example.ee, "enumerated");
        softAssert(input->es == example.es, "specified");
        softAssert(strcmp(input->s, example.s) == 0, "string");
        softAssert(input->v2.x == example.v2.x, "Vec2");
        softAssert(input->v2.y == example.v2.y, "Vec2");
        softAssert(input->v3.x == example.v3.x, "Vec3");
        softAssert(input->v3.y == example.v3.y, "Vec3");
        softAssert(input->v3.z == example.v3.z, "Vec3");
        softAssert(input->c.r == example.c.r, "Color");
        softAssert(input->c.g == example.c.g, "Color");
        softAssert(input->c.b == example.c.b, "Color");
        softAssert(input->il_len == example.il_len, "[int16].length");
        for (uint32_t i = 0; i < input->il_len; i++) {
            softAssert(input->il[i] == example.il[i], "[int16]");
        }
        softAssert(input->el_len == example.el_len, "[Specified].length");
        for (uint32_t i = 0; i < input->el_len; i++) {
            softAssert(input->el[i] == example.el[i], "[Specified]");
        }
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
        softAssert(input->cx.ranges_len == example.cx.ranges_len, "ComplexData.ranges.length");
        for (uint32_t i  = 0; i < input->cx.ranges_len; i++) {
            softAssert(input->cx.ranges[i] == example.cx.ranges[i], "ComplexData.ranges");
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
            softAssert(input->cxl[i].ranges_len == example.cxl[i].ranges_len, "[ComplexData].ranges.length");
            for (uint32_t j = 0; j < input->cxl[i].ranges_len; j++) {
                softAssert(input->cxl[i].ranges[j] == example.cxl[i].ranges[j], "[ComplexData].ranges");
            }
        }

        ComprehensiveMessage_TestingMessage_Destroy(input);

        free(buffer);
    }

    return check();
}
