#ifndef INCLUDE_BESCHI_H
#define INCLUDE_BESCHI_H

#include <stdbool.h>
#include <stdint.h>
#include <string.h>

typedef uint8_t beschi_err_t;
#define BESCHI_ERR_OK  0
#define BESCHI_ERR_EOF 1

#ifdef __cplusplus
extern "C" {
#endif

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
beschi_err_t beschi__WriteString(beschi_DataAccess *w, const char **s, const uint32_t *len);


#ifdef BESCHI_IMPLEMENTATION

//////////////////////////////////////////////////////////////////////////////
//
//   IMPLEMENTATION
//


///////////////////////////////////////
// standard utility functions

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
    if (err != BESCHI_ERR_OK) {
        return err;
    }
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
    if (err != BESCHI_ERR_OK) {
        return err;
    }
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
    if (err != BESCHI_ERR_OK) {
        return err;
    }
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

beschi_err_t beschi__WriteString(beschi_DataAccess *w, const char **s, const uint32_t *len) {
    beschi_err_t err;
    err = beschi__WriteUInt32(w, len);
    if (err != BESCHI_ERR_OK) {
        return err;
    }
    if (w->bufferSize < w->position + *len) {
        return BESCHI_ERR_EOF;
    }
    memccpy(w->buffer + w->position, *s, 1, *len);
    w->position += *len;
    return BESCHI_ERR_OK;
}

// end of standard utility functions
///////////////////////////////////////

///////////////////////////////////////
// message definitions


// end of message definitions
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
