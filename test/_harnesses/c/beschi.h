#ifndef INCLUDE_BESCHI_H
#define INCLUDE_BESCHI_H

#include <stdbool.h>
#include <stdint.h>
#include <string.h>

typedef uint8_t beschi_err_t;
#define BESCHI_ERR_OK  0
#define BESCHI_ERR_EOF 1
#define BESCHI_ERR_INVALID_DATA 2

#define BESCHI_ERR_CHECK_RETURN if (err != BESCHI_ERR_OK) { return err; }

#ifdef __cplusplus
extern "C" {
#endif

///////////////////////////////////////
// standard utility declarations

typedef struct {
    uint8_t* buffer;
    size_t bufferSize;
    size_t position;
} beschi_DataAccess;

bool beschi_IsFinished(beschi_DataAccess *r);
beschi_err_t beschi__ReadUInt8(beschi_DataAccess *r, uint8_t *ui8);
beschi_err_t beschi__ReadBool(beschi_DataAccess *r, bool *b);
beschi_err_t beschi__ReadInt16(beschi_DataAccess *r, int16_t *i16);
beschi_err_t beschi__ReadUInt16(beschi_DataAccess *r, uint16_t *ui16);
beschi_err_t beschi__ReadInt32(beschi_DataAccess *r, int32_t *i32);
beschi_err_t beschi__ReadUInt32(beschi_DataAccess *r, uint32_t *ui32);
beschi_err_t beschi__ReadInt64(beschi_DataAccess *r, int64_t *i64);
beschi_err_t beschi__ReadUInt64(beschi_DataAccess *r, uint64_t *ui32);
beschi_err_t beschi__ReadFloat(beschi_DataAccess *r, float *f);
beschi_err_t beschi__ReadDouble(beschi_DataAccess *r, double *d);
beschi_err_t beschi__ReadString(beschi_DataAccess *r, char **s, uint32_t *len);

beschi_err_t beschi__WriteUInt8(beschi_DataAccess *w, const uint8_t *ui8);
beschi_err_t beschi__WriteBool(beschi_DataAccess *w, const bool *b);
beschi_err_t beschi__WriteInt16(beschi_DataAccess *w, const int16_t *i16);
beschi_err_t beschi__WriteUInt16(beschi_DataAccess *w, const uint16_t *ui16);
beschi_err_t beschi__WriteInt32(beschi_DataAccess *w, const int32_t *i32);
beschi_err_t beschi__WriteUInt32(beschi_DataAccess *w, const uint32_t *ui32);
beschi_err_t beschi__WriteInt64(beschi_DataAccess *w, const int64_t *i64);
beschi_err_t beschi__WriteUInt64(beschi_DataAccess *w, const uint64_t *ui32);
beschi_err_t beschi__WriteFloat(beschi_DataAccess *w, const float *f);
beschi_err_t beschi__WriteDouble(beschi_DataAccess *w, const double *d);
beschi_err_t beschi__WriteString(beschi_DataAccess *w, char* const *s, const uint32_t *len);

// end of standard utility declarations
///////////////////////////////////////


///////////////////////////////////////
// struct/message declarations

typedef enum {
    beschi_MessageType___NullMessage = 0,
    beschi_MessageType_TestingMessageType = 1,
} beschi_MessageType;

beschi_MessageType beschi_GetMessageType(const void* m);
beschi_err_t beschi_GetSizeInBytes(const void* m, size_t* len);
beschi_err_t beschi_ProcessRawBytes(beschi_DataAccess* r, void** msgListOut, size_t* len);

typedef struct {
    float x;
    float y;
} beschi_Vec2;
beschi_err_t beschi_Vec2_WriteBytes(beschi_DataAccess* w, const beschi_Vec2 *v2);
beschi_err_t beschi_Vec2_FromBytes(beschi_DataAccess* r, beschi_Vec2 *v2);

typedef struct {
    float x;
    float y;
    float z;
} beschi_Vec3;
beschi_err_t beschi_Vec3_WriteBytes(beschi_DataAccess* w, const beschi_Vec3 *v3);
beschi_err_t beschi_Vec3_FromBytes(beschi_DataAccess* r, beschi_Vec3 *v3);

typedef struct {
    uint8_t r;
    uint8_t g;
    uint8_t b;
} beschi_Color;
beschi_err_t beschi_Color_WriteBytes(beschi_DataAccess* w, const beschi_Color *c);
beschi_err_t beschi_Color_FromBytes(beschi_DataAccess* r, beschi_Color *c);

typedef struct {
    uint8_t identifier;
    uint32_t label_len;
    char* label;
    beschi_Color textColor;
    beschi_Color backgroundColor;
    uint32_t spectrum_len;
    beschi_Color* spectrum;
} beschi_ComplexData;
beschi_err_t beschi_ComplexData_WriteBytes(beschi_DataAccess* w, const beschi_ComplexData *cx);
beschi_err_t beschi_ComplexData_FromBytes(beschi_DataAccess* r, beschi_ComplexData *cx);

typedef struct {
    beschi_MessageType _mt;
    uint8_t b;
    bool tf;
    int16_t i16;
    uint16_t ui16;
    int32_t i32;
    uint32_t ui32;
    int64_t i64;
    uint64_t ui64;
    float f;
    double d;
    uint32_t s_len;
    char* s;
    beschi_Vec2 v2;
    beschi_Vec3 v3;
    beschi_Color c;
    uint32_t sl_len;
    char** sl;
    uint32_t* sl_els_len;
    uint32_t v2l_len;
    beschi_Vec2* v2l;
    uint32_t v3l_len;
    beschi_Vec3* v3l;
    uint32_t cl_len;
    beschi_Color* cl;
    beschi_ComplexData cx;
    uint32_t cxl_len;
    beschi_ComplexData* cxl;
} beschi_TestingMessage;
beschi_err_t beschi_TestingMessage_WriteBytes(beschi_DataAccess* w, const beschi_TestingMessage *m, bool tag);
beschi_err_t beschi_TestingMessage_FromBytes(beschi_DataAccess* r, beschi_TestingMessage *m);
beschi_err_t beschi_TestingMessage_GetSizeInBytes(const beschi_TestingMessage *m, size_t *size);
void beschi_TestingMessage_Destroy(beschi_TestingMessage *m);

// end of struct/message definitions
///////////////////////////////////////


#ifdef BESCHI_IMPLEMENTATION

//////////////////////////////////////////////////////////////////////////////
//
//   IMPLEMENTATION
//


///////////////////////////////////////
// standard utility definitions

bool beschi_IsFinished(beschi_DataAccess *r) {
    return r->position >= r->bufferSize;
}

beschi_err_t beschi__ReadUInt8(beschi_DataAccess *r, uint8_t *ui8) {
    if (r->bufferSize < r->position + 1) {
        return BESCHI_ERR_EOF;
    }
    memccpy(ui8, r->buffer + r->position, 1, 1);
    r->position += 1;
    return BESCHI_ERR_OK;
}

beschi_err_t beschi__ReadBool(beschi_DataAccess *r, bool *b) {
    uint8_t byteVal;
    beschi_err_t err = beschi__ReadUInt8(r, &byteVal);
    BESCHI_ERR_CHECK_RETURN;
    *b = byteVal > 0;
    return BESCHI_ERR_OK;
}

beschi_err_t beschi__ReadInt16(beschi_DataAccess *r, int16_t *i16) {
    if (r->bufferSize < r->position + 2) {
        return BESCHI_ERR_EOF;
    }
    memccpy(i16, r->buffer + r->position, 1, 2);
    r->position += 2;
    return BESCHI_ERR_OK;
}

beschi_err_t beschi__ReadUInt16(beschi_DataAccess *r, uint16_t *ui16) {
    if (r->bufferSize < r->position + 2) {
        return BESCHI_ERR_EOF;
    }
    memccpy(ui16, r->buffer + r->position, 1, 2);
    r->position += 2;
    return BESCHI_ERR_OK;
}

beschi_err_t beschi__ReadInt32(beschi_DataAccess *r, int32_t *i32) {
    if (r->bufferSize < r->position + 4) {
        return BESCHI_ERR_EOF;
    }
    memccpy(i32, r->buffer + r->position, 1, 4);
    r->position += 4;
    return BESCHI_ERR_OK;
}

beschi_err_t beschi__ReadUInt32(beschi_DataAccess *r, uint32_t *ui32) {
    if (r->bufferSize < r->position + 4) {
        return BESCHI_ERR_EOF;
    }
    memccpy(ui32, r->buffer + r->position, 1, 4);
    r->position += 4;
    return BESCHI_ERR_OK;
}

beschi_err_t beschi__ReadInt64(beschi_DataAccess *r, int64_t *i64) {
    if (r->bufferSize < r->position + 8) {
        return BESCHI_ERR_EOF;
    }
    memccpy(i64, r->buffer + r->position, 1, 8);
    r->position += 8;
    return BESCHI_ERR_OK;
}

beschi_err_t beschi__ReadUInt64(beschi_DataAccess *r, uint64_t *ui64) {
    if (r->bufferSize < r->position + 8) {
        return BESCHI_ERR_EOF;
    }
    memccpy(ui64, r->buffer + r->position, 1, 8);
    r->position += 8;
    return BESCHI_ERR_OK;
}

beschi_err_t beschi__ReadFloat(beschi_DataAccess *r, float *f) {
    if (r->bufferSize < r->position + 4) {
        return BESCHI_ERR_EOF;
    }
    memccpy(f, r->buffer + r->position, 1, 4);
    r->position += 4;
    return BESCHI_ERR_OK;
}

beschi_err_t beschi__ReadDouble(beschi_DataAccess *r, double *d) {
    if (r->bufferSize < r->position + 8) {
        return BESCHI_ERR_EOF;
    }
    memccpy(d, r->buffer + r->position, 1, 8);
    r->position += 8;
    return BESCHI_ERR_OK;
}

beschi_err_t beschi__ReadString(beschi_DataAccess *r, char **s, uint32_t *len) {
    beschi_err_t err;
    err = beschi__ReadUInt32(r, len);
    BESCHI_ERR_CHECK_RETURN;
    if (r->bufferSize < r->position + *len) {
        return BESCHI_ERR_EOF;
    }
    *s = malloc(*len);
    memccpy(*s, r->buffer + r->position, 1, *len);
    r->position += *len;
    return BESCHI_ERR_OK;
}



beschi_err_t beschi__WriteUInt8(beschi_DataAccess *w, const uint8_t *ui8) {
    if (w->bufferSize < w->position + 1) {
        return BESCHI_ERR_EOF;
    }
    memccpy(w->buffer + w->position, ui8, 1, 1);
    w->position += 1;
    return BESCHI_ERR_OK;
}

beschi_err_t beschi__WriteBool(beschi_DataAccess *w, const bool *b) {
    beschi_err_t err;
    uint8_t byteVal = b ? 1 : 0;
    err = beschi__WriteUInt8(w, &byteVal);
    BESCHI_ERR_CHECK_RETURN;
    return BESCHI_ERR_OK;
}

beschi_err_t beschi__WriteInt16(beschi_DataAccess *w, const int16_t *i16) {
    if (w->bufferSize < w->position + 2) {
        return BESCHI_ERR_EOF;
    }
    memccpy(w->buffer + w->position, i16, 1, 2);
    w->position += 2;
    return BESCHI_ERR_OK;
}

beschi_err_t beschi__WriteUInt16(beschi_DataAccess *w, const uint16_t *ui16) {
    if (w->bufferSize < w->position + 2) {
        return BESCHI_ERR_EOF;
    }
    memccpy(w->buffer + w->position, ui16, 1, 2);
    w->position += 2;
    return BESCHI_ERR_OK;
}

beschi_err_t beschi__WriteInt32(beschi_DataAccess *w, const int32_t *i32) {
    if (w->bufferSize < w->position + 4) {
        return BESCHI_ERR_EOF;
    }
    memccpy(w->buffer + w->position, i32, 1, 4);
    w->position += 4;
    return BESCHI_ERR_OK;
}

beschi_err_t beschi__WriteUInt32(beschi_DataAccess *w, const uint32_t *ui32) {
    if (w->bufferSize < w->position + 4) {
        return BESCHI_ERR_EOF;
    }
    memccpy(w->buffer + w->position, ui32, 1, 4);
    w->position += 4;
    return BESCHI_ERR_OK;
}

beschi_err_t beschi__WriteInt64(beschi_DataAccess *w, const int64_t *i64) {
    if (w->bufferSize < w->position + 8) {
        return BESCHI_ERR_EOF;
    }
    memccpy(w->buffer + w->position, i64, 1, 8);
    w->position += 8;
    return BESCHI_ERR_OK;
}

beschi_err_t beschi__WriteUInt64(beschi_DataAccess *w, const uint64_t *ui64) {
    if (w->bufferSize < w->position + 8) {
        return BESCHI_ERR_EOF;
    }
    memccpy(w->buffer + w->position, ui64, 1, 8);
    w->position += 8;
    return BESCHI_ERR_OK;
}

beschi_err_t beschi__WriteFloat(beschi_DataAccess *w, const float *f) {
    if (w->bufferSize < w->position + 4) {
        return BESCHI_ERR_EOF;
    }
    memccpy(w->buffer + w->position, f, 1, 4);
    w->position += 4;
    return BESCHI_ERR_OK;
}

beschi_err_t beschi__WriteDouble(beschi_DataAccess *w, const double *d) {
    if (w->bufferSize < w->position + 8) {
        return BESCHI_ERR_EOF;
    }
    memccpy(w->buffer + w->position, d, 1, 8);
    w->position += 8;
    return BESCHI_ERR_OK;
}

beschi_err_t beschi__WriteString(beschi_DataAccess *w, char* const *s, const uint32_t *len) {
    beschi_err_t err;
    err = beschi__WriteUInt32(w, len);
    BESCHI_ERR_CHECK_RETURN;
    if (w->bufferSize < w->position + *len) {
        return BESCHI_ERR_EOF;
    }
    memccpy(w->buffer + w->position, *s, 1, *len);
    w->position += *len;
    return BESCHI_ERR_OK;
}

// end of standard utility definitions
///////////////////////////////////////


///////////////////////////////////////
// struct/message definitions

beschi_MessageType beschi_GetMessageType(const void* m) {
    return beschi_MessageType___NullMessage;
}

beschi_err_t beschi_GetSizeInBytes(const void* m, size_t* len) {
    beschi_MessageType msgType = beschi_GetMessageType(m);
    switch (msgType) {
    case beschi_MessageType___NullMessage:
        return BESCHI_ERR_INVALID_DATA;
        break;
    case beschi_MessageType_TestingMessageType:
        return beschi_TestingMessage_GetSizeInBytes(m, len);
        break;
    }
    return BESCHI_ERR_INVALID_DATA;
}

beschi_err_t beschi_ProcessRawBytes(beschi_DataAccess* r, void** msgListOut, size_t* len) {
    return BESCHI_ERR_OK;
}

beschi_err_t beschi_Vec2_WriteBytes(beschi_DataAccess* w, const beschi_Vec2 *v2) {
    beschi_err_t err;
    err = beschi__WriteFloat(w, &(v2->x));
    BESCHI_ERR_CHECK_RETURN;
    err = beschi__WriteFloat(w, &(v2->y));
    BESCHI_ERR_CHECK_RETURN;
    return BESCHI_ERR_OK;
}

beschi_err_t beschi_Vec2_FromBytes(beschi_DataAccess* r, beschi_Vec2 *v2) {
    beschi_err_t err;
    err = beschi__ReadFloat(r, &(v2->x));
    BESCHI_ERR_CHECK_RETURN;
    err = beschi__ReadFloat(r, &(v2->y));
    BESCHI_ERR_CHECK_RETURN;
    return BESCHI_ERR_OK;
}

beschi_err_t beschi_Vec3_WriteBytes(beschi_DataAccess* w, const beschi_Vec3 *v3) {
    beschi_err_t err;
    err = beschi__WriteFloat(w, &(v3->x));
    BESCHI_ERR_CHECK_RETURN;
    err = beschi__WriteFloat(w, &(v3->y));
    BESCHI_ERR_CHECK_RETURN;
    err = beschi__WriteFloat(w, &(v3->z));
    BESCHI_ERR_CHECK_RETURN;
    return BESCHI_ERR_OK;
}

beschi_err_t beschi_Vec3_FromBytes(beschi_DataAccess* r, beschi_Vec3 *v3) {
    beschi_err_t err;
    err = beschi__ReadFloat(r, &(v3->x));
    BESCHI_ERR_CHECK_RETURN;
    err = beschi__ReadFloat(r, &(v3->y));
    BESCHI_ERR_CHECK_RETURN;
    err = beschi__ReadFloat(r, &(v3->z));
    BESCHI_ERR_CHECK_RETURN;
    return BESCHI_ERR_OK;
}

beschi_err_t beschi_Color_WriteBytes(beschi_DataAccess* w, const beschi_Color *c) {
    beschi_err_t err;
    err = beschi__WriteUInt8(w, &(c->r));
    BESCHI_ERR_CHECK_RETURN;
    err = beschi__WriteUInt8(w, &(c->g));
    BESCHI_ERR_CHECK_RETURN;
    err = beschi__WriteUInt8(w, &(c->b));
    BESCHI_ERR_CHECK_RETURN;
    return BESCHI_ERR_OK;
}

beschi_err_t beschi_Color_FromBytes(beschi_DataAccess* r, beschi_Color *c) {
    beschi_err_t err;
    err = beschi__ReadUInt8(r, &(c->r));
    BESCHI_ERR_CHECK_RETURN;
    err = beschi__ReadUInt8(r, &(c->g));
    BESCHI_ERR_CHECK_RETURN;
    err = beschi__ReadUInt8(r, &(c->b));
    BESCHI_ERR_CHECK_RETURN;
    return BESCHI_ERR_OK;
}

beschi_err_t beschi_ComplexData_WriteBytes(beschi_DataAccess* w, const beschi_ComplexData *cx) {
    beschi_err_t err;
    err = beschi__WriteUInt8(w, &(cx->identifier));
    BESCHI_ERR_CHECK_RETURN;
    err = beschi__WriteString(w, &(cx->label), &(cx->label_len));
    BESCHI_ERR_CHECK_RETURN;
    err = beschi_Color_WriteBytes(w, &(cx->textColor));
    BESCHI_ERR_CHECK_RETURN;
    err = beschi_Color_WriteBytes(w, &(cx->backgroundColor));
    BESCHI_ERR_CHECK_RETURN;
    err = beschi__WriteUInt32(w, &(cx->spectrum_len));
    BESCHI_ERR_CHECK_RETURN;
    for (uint32_t i = 0; i < cx->spectrum_len; i++) {
        err = beschi_Color_WriteBytes(w, &(cx->spectrum[i]));
        BESCHI_ERR_CHECK_RETURN;
    }
    return BESCHI_ERR_OK;
}

beschi_err_t beschi_ComplexData_FromBytes(beschi_DataAccess* r, beschi_ComplexData *cx) {
    beschi_err_t err;
    err = beschi__ReadUInt8(r, &(cx->identifier));
    BESCHI_ERR_CHECK_RETURN;
    err = beschi__ReadString(r, &(cx->label), &(cx->label_len));
    BESCHI_ERR_CHECK_RETURN;
    err = beschi_Color_FromBytes(r, &(cx->textColor));
    BESCHI_ERR_CHECK_RETURN;
    err = beschi_Color_FromBytes(r, &(cx->backgroundColor));
    BESCHI_ERR_CHECK_RETURN;
    err = beschi__ReadUInt32(r, &(cx->spectrum_len));
    BESCHI_ERR_CHECK_RETURN;
    cx->spectrum = malloc(sizeof(beschi_Color) * cx->spectrum_len);
    for (uint32_t i = 0; i < cx->spectrum_len; i++) {
        err = beschi_Color_FromBytes(r, &(cx->spectrum[i]));
        BESCHI_ERR_CHECK_RETURN;
    }
    return BESCHI_ERR_OK;
}

beschi_err_t beschi_TestingMessage_WriteBytes(beschi_DataAccess* w, const beschi_TestingMessage *m, bool tag) {
    beschi_err_t err;
    if (tag) {
        err = beschi__WriteUInt8(w, (const uint8_t *)&(m->_mt));
        BESCHI_ERR_CHECK_RETURN;
    }
    err = beschi__WriteUInt8(w, &(m->b));
    BESCHI_ERR_CHECK_RETURN;
    err = beschi__WriteBool(w, &(m->tf));
    BESCHI_ERR_CHECK_RETURN;
    err = beschi__WriteInt16(w, &(m->i16));
    BESCHI_ERR_CHECK_RETURN;
    err = beschi__WriteUInt16(w, &(m->ui16));
    BESCHI_ERR_CHECK_RETURN;
    err = beschi__WriteInt32(w, &(m->i32));
    BESCHI_ERR_CHECK_RETURN;
    err = beschi__WriteUInt32(w, &(m->ui32));
    BESCHI_ERR_CHECK_RETURN;
    err = beschi__WriteInt64(w, &(m->i64));
    BESCHI_ERR_CHECK_RETURN;
    err = beschi__WriteUInt64(w, &(m->ui64));
    BESCHI_ERR_CHECK_RETURN;
    err = beschi__WriteFloat(w, &(m->f));
    BESCHI_ERR_CHECK_RETURN;
    err = beschi__WriteDouble(w, &(m->d));
    BESCHI_ERR_CHECK_RETURN;
    err = beschi__WriteString(w, &(m->s), &(m->s_len));
    BESCHI_ERR_CHECK_RETURN;
    err = beschi_Vec2_WriteBytes(w, &(m->v2));
    BESCHI_ERR_CHECK_RETURN;
    err = beschi_Vec3_WriteBytes(w, &(m->v3));
    BESCHI_ERR_CHECK_RETURN;
    err = beschi_Color_WriteBytes(w, &(m->c));
    BESCHI_ERR_CHECK_RETURN;
    err = beschi__WriteUInt32(w, &(m->sl_len));
    BESCHI_ERR_CHECK_RETURN;
    for (uint32_t i = 0; i < m->sl_len; i++) {
        err = beschi__WriteString(w, &(m->sl[i]), &(m->sl_els_len[i]));
        BESCHI_ERR_CHECK_RETURN;
    }
    err = beschi__WriteUInt32(w, &(m->v2l_len));
    BESCHI_ERR_CHECK_RETURN;
    for (uint32_t i = 0; i < m->v2l_len; i++) {
        err = beschi_Vec2_WriteBytes(w, &(m->v2l[i]));
        BESCHI_ERR_CHECK_RETURN;
    }
    err = beschi__WriteUInt32(w, &(m->v3l_len));
    BESCHI_ERR_CHECK_RETURN;
    for (uint32_t i = 0; i < m->v3l_len; i++) {
        err = beschi_Vec3_WriteBytes(w, &(m->v3l[i]));
        BESCHI_ERR_CHECK_RETURN;
    }
    err = beschi__WriteUInt32(w, &(m->cl_len));
    BESCHI_ERR_CHECK_RETURN;
    for (uint32_t i = 0; i < m->cl_len; i++) {
        err = beschi_Color_WriteBytes(w, &(m->cl[i]));
        BESCHI_ERR_CHECK_RETURN;
    }
    err = beschi_ComplexData_WriteBytes(w, &(m->cx));
    BESCHI_ERR_CHECK_RETURN;
    err = beschi__WriteUInt32(w, &(m->cxl_len));
    BESCHI_ERR_CHECK_RETURN;
    for (uint32_t i = 0; i < m->cxl_len; i++) {
        err = beschi_ComplexData_WriteBytes(w, &(m->cxl[i]));
        BESCHI_ERR_CHECK_RETURN;
    }

    return BESCHI_ERR_OK;
}

beschi_err_t beschi_TestingMessage_FromBytes(beschi_DataAccess* r, beschi_TestingMessage *m) {
    beschi_err_t err;
    err = beschi__ReadUInt8(r, &(m->b));
    BESCHI_ERR_CHECK_RETURN;
    err = beschi__ReadBool(r, &(m->tf));
    BESCHI_ERR_CHECK_RETURN;
    err = beschi__ReadInt16(r, &(m->i16));
    BESCHI_ERR_CHECK_RETURN;
    err = beschi__ReadUInt16(r, &(m->ui16));
    BESCHI_ERR_CHECK_RETURN;
    err = beschi__ReadInt32(r, &(m->i32));
    BESCHI_ERR_CHECK_RETURN;
    err = beschi__ReadUInt32(r, &(m->ui32));
    BESCHI_ERR_CHECK_RETURN;
    err = beschi__ReadInt64(r, &(m->i64));
    BESCHI_ERR_CHECK_RETURN;
    err = beschi__ReadUInt64(r, &(m->ui64));
    BESCHI_ERR_CHECK_RETURN;
    err = beschi__ReadFloat(r, &(m->f));
    BESCHI_ERR_CHECK_RETURN;
    err = beschi__ReadDouble(r, &(m->d));
    BESCHI_ERR_CHECK_RETURN;
    err = beschi__ReadString(r, &(m->s), &(m->s_len));
    BESCHI_ERR_CHECK_RETURN;
    err = beschi_Vec2_FromBytes(r, &(m->v2));
    BESCHI_ERR_CHECK_RETURN;
    err = beschi_Vec3_FromBytes(r, &(m->v3));
    BESCHI_ERR_CHECK_RETURN;
    err = beschi_Color_FromBytes(r, &(m->c));
    BESCHI_ERR_CHECK_RETURN;
    err = beschi__ReadUInt32(r, &(m->sl_len));
    BESCHI_ERR_CHECK_RETURN;
    m->sl = malloc(sizeof(char*) * m->sl_len);
    m->sl_els_len = malloc(sizeof(uint32_t) * m->sl_len);
    for (uint32_t i = 0; i < m->sl_len; i++) {
        err = beschi__ReadString(r, &(m->sl[i]), &(m->sl_els_len[i]));
        BESCHI_ERR_CHECK_RETURN;
    }
    err = beschi__ReadUInt32(r, &(m->v2l_len));
    BESCHI_ERR_CHECK_RETURN;
    m->v2l = malloc(sizeof(beschi_Vec2) * m->v2l_len);
    for (uint32_t i = 0; i < m->v2l_len; i++) {
        err = beschi_Vec2_FromBytes(r, &(m->v2l[i]));
        BESCHI_ERR_CHECK_RETURN;
    }
    err = beschi__ReadUInt32(r, &(m->v3l_len));
    BESCHI_ERR_CHECK_RETURN;
    m->v3l = malloc(sizeof(beschi_Vec3) * m->v3l_len);
    for (uint32_t i = 0; i < m->v3l_len; i++) {
        err = beschi_Vec3_FromBytes(r, &(m->v3l[i]));
        BESCHI_ERR_CHECK_RETURN;
    }
    err = beschi__ReadUInt32(r, &(m->cl_len));
    BESCHI_ERR_CHECK_RETURN;
    m->cl = malloc(sizeof(beschi_Color) * m->cl_len);
    for (uint32_t i = 0; i < m->cl_len; i++) {
        err = beschi_Color_FromBytes(r, &(m->cl[i]));
        BESCHI_ERR_CHECK_RETURN;
    }
    err = beschi_ComplexData_FromBytes(r, &(m->cx));
    BESCHI_ERR_CHECK_RETURN;
    err = beschi__ReadUInt32(r, &(m->cxl_len));
    BESCHI_ERR_CHECK_RETURN;
    m->cxl = malloc(sizeof(beschi_ComplexData) * m->cxl_len);
    for (uint32_t i = 0; i < m->cxl_len; i++) {
        err = beschi_ComplexData_FromBytes(r, &(m->cxl[i]));
        BESCHI_ERR_CHECK_RETURN;
    }

    return BESCHI_ERR_OK;
}

beschi_err_t beschi_TestingMessage_GetSizeInBytes(const beschi_TestingMessage *m, size_t *size) {
    *size = 0;
    *size += m->s_len;
    for (uint32_t sl_i = 0; sl_i < m->sl_len; sl_i++) {
        *size += 4 + m->sl_els_len[sl_i];
    }
    *size += m->v2l_len * 8;
    *size += m->v3l_len * 12;
    *size += m->cl_len * 3;
    *size += m->cx.label_len;
    *size += m->cx.spectrum_len * 3;
    for (uint32_t cxl_i = 0; cxl_i < m->cxl_len; cxl_i++) {
        *size += m->cxl[cxl_i].label_len;
        *size += m->cxl[cxl_i].spectrum_len * 3;
        *size += 15;
    }
    *size += 104;

    return BESCHI_ERR_OK;
}

void beschi_TestingMessage_Destroy(beschi_TestingMessage *m) {
    free(m->s);
    for (uint32_t i = 0; i < m->sl_len; i++) {
        free(m->sl[i]);
    }
    free(m->sl_els_len);
    free(m->sl);
    free(m->v2l);
    free(m->v3l);
    free(m->cl);

    free(m->cx.label);
    free(m->cx.spectrum);

    for (uint32_t i = 0; i < m->cxl_len; i++) {
        free(m->cxl[i].label);
        free(m->cxl[i].spectrum);
    }
    free(m->cxl);

    free(m);
}


// end of struct/message definitions
///////////////////////////////////////


//
//   END OF IMPLEMENTATION
//
//////////////////////////////////////////////////////////////////////////////

#endif // BESCHI_IMPLEMENTATION

#ifdef __cplusplus
}
#endif

#endif // INCLUDE_BESCHI_H
