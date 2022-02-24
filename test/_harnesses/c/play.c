#include <stdlib.h>
#include <stdio.h>
#include <assert.h>

#define BESCHI_IMPLEMENTATION
#include "beschi.h"

typedef struct {
    float x;
    float y;
    float z;
} Vec3;

const Vec3 example1 = {.x = 45.0f,  .y =   72.89f,     .z = 1234567.891011f};
const Vec3 example2 = {.x = 89.76f, .y = 1067.141593f, .z = 1234567.891011f};

int main(int arv, char** argv) {
    const size_t bufferSize = sizeof(Vec3) * 2;
    uint8_t* buffer = malloc(bufferSize);

    beschi_err_t err = BESCHI_ERR_OK;

    beschi_DataAccess writer = {.buffer = buffer, .bufferSize = bufferSize, .position = 0};
    err = beschi__WriteFloat(&writer, &example1.x);
    if (err != BESCHI_ERR_OK) {
        printf("ERROR! Couldn't write example1.x. :(\n");
    }
    err = beschi__WriteFloat(&writer, &example1.y);
    if (err != BESCHI_ERR_OK) {
        printf("ERROR! Couldn't write example1.y. :(\n");
    }
    err = beschi__WriteFloat(&writer, &example1.z);
    if (err != BESCHI_ERR_OK) {
        printf("ERROR! Couldn't write example1.z. :(\n");
    }
    err = beschi__WriteFloat(&writer, &example2.x);
    if (err != BESCHI_ERR_OK) {
        printf("ERROR! Couldn't write example2.x. :(\n");
    }
    err = beschi__WriteFloat(&writer, &example2.y);
    if (err != BESCHI_ERR_OK) {
        printf("ERROR! Couldn't write example2.y. :(\n");
    }
    err = beschi__WriteFloat(&writer, &example2.z);
    if (err != BESCHI_ERR_OK) {
        printf("ERROR! Couldn't write example2.z. :(\n");
    }


    Vec3 input1, input2;

    beschi_DataAccess reader = {.buffer = buffer, .bufferSize = bufferSize, .position = 0};
    err = beschi__ReadFloat(&reader, &input1.x);
    if (err != BESCHI_ERR_OK) {
        printf("ERROR! Couldn't read input1.x. :(\n");
    }
    err = beschi__ReadFloat(&reader, &input1.y);
    if (err != BESCHI_ERR_OK) {
        printf("ERROR! Couldn't read input1.y. :(\n");
    }
    err = beschi__ReadFloat(&reader, &input1.z);
    if (err != BESCHI_ERR_OK) {
        printf("ERROR! Couldn't read input1.z. :(\n");
    }
    err = beschi__ReadFloat(&reader, &input2.x);
    if (err != BESCHI_ERR_OK) {
        printf("ERROR! Couldn't read input2.x. :(\n");
    }
    err = beschi__ReadFloat(&reader, &input2.y);
    if (err != BESCHI_ERR_OK) {
        printf("ERROR! Couldn't read input2.y. :(\n");
    }
    err = beschi__ReadFloat(&reader, &input2.z);
    if (err != BESCHI_ERR_OK) {
        printf("ERROR! Couldn't read input2.z. :(\n");
    }

    printf("{x1: %.5f, y1: %.5f, z1: %.5f}\n{x2: %.5f, y2: %.5f, z2: %.5f}\n", input1.x, input1.y, input1.z, input2.x, input2.y, input2.z);
    assert(input1.x == example1.x);
    assert(input1.y == example1.y);
    assert(input1.z == example1.z);
    assert(input2.x == example2.x);
    assert(input2.y == example2.y);
    assert(input2.z == example2.z);
    printf("All checks passed.\n");
}

/*
int main(int argc, char** argv) {
    FILE* fp = fopen("../../../out/data/broken.csharp.msg", "rb");
    fseek(fp, 0, SEEK_END);
    long fileSize = ftell(fp);
    fseek(fp, 0, SEEK_SET);

    uint8_t* buffer = malloc(fileSize);
    fread(buffer, fileSize, 1, fp);
    fclose(fp);

    beschi_DataAccess data;
    data.buffer = buffer;
    data.bufferSize = fileSize;
    data.position = 0;

    Vec3 v3;
    beschi_err_t err = BESCHI_ERR_OK;
    err = beschi__ReadFloat(&data, &v3.x);
    if (err != BESCHI_ERR_OK) {
        printf("ERROR!\n");
    }
    err = beschi__ReadFloat(&data, &v3.y);
    if (err != BESCHI_ERR_OK) {
        printf("ERROR!\n");
    }
    err = beschi__ReadFloat(&data, &v3.z);
    if (err != BESCHI_ERR_OK) {
        printf("ERROR!\n");
    }
    free(buffer);

    printf("{x: %.1f, y: %.1f, z: %.1f}\n", v3.x, v3.y, v3.z);

    return 0;
}
*/
