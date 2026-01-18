// To use this header file, include it normally wherever you need access
//   to its structures and functions.
// Then in *exactly* one file, #define BESCHI_IMPLEMENTATION
//   *before* including it.

#ifndef INCLUDE_BESCHI_H
#define INCLUDE_BESCHI_H

#include <stdlib.h>
#include <stddef.h>
#include <stdint.h>
#include <stdbool.h>

typedef uint8_t beschi_err_t;
#define BESCHI_ERR_OK  0
#define BESCHI_ERR_EOF 1
#define BESCHI_ERR_INVALID_DATA 2
#define BESCHI_ERR_ALLOCATION_FAILURE 3

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

bool beschi_IsFinished(const beschi_DataAccess *r);
beschi_err_t beschi_ReadUInt8(beschi_DataAccess *r, uint8_t *ui8);
beschi_err_t beschi_ReadBool(beschi_DataAccess *r, bool *b);
beschi_err_t beschi_ReadInt16(beschi_DataAccess *r, int16_t *i16);
beschi_err_t beschi_ReadUInt16(beschi_DataAccess *r, uint16_t *ui16);
beschi_err_t beschi_ReadInt32(beschi_DataAccess *r, int32_t *i32);
beschi_err_t beschi_ReadUInt32(beschi_DataAccess *r, uint32_t *ui32);
beschi_err_t beschi_ReadInt64(beschi_DataAccess *r, int64_t *i64);
beschi_err_t beschi_ReadUInt64(beschi_DataAccess *r, uint64_t *ui32);
beschi_err_t beschi_ReadFloat(beschi_DataAccess *r, float *f);
beschi_err_t beschi_ReadDouble(beschi_DataAccess *r, double *d);
beschi_err_t beschi_ReadString(beschi_DataAccess *r, char **s, {# STRING_SIZE_TYPE_NATIVE #} *len);

beschi_err_t beschi_WriteUInt8(beschi_DataAccess *w, const uint8_t ui8);
beschi_err_t beschi_WriteBool(beschi_DataAccess *w, const bool b);
beschi_err_t beschi_WriteInt16(beschi_DataAccess *w, const int16_t i16);
beschi_err_t beschi_WriteUInt16(beschi_DataAccess *w, const uint16_t ui16);
beschi_err_t beschi_WriteInt32(beschi_DataAccess *w, const int32_t i32);
beschi_err_t beschi_WriteUInt32(beschi_DataAccess *w, const uint32_t ui32);
beschi_err_t beschi_WriteInt64(beschi_DataAccess *w, const int64_t i64);
beschi_err_t beschi_WriteUInt64(beschi_DataAccess *w, const uint64_t ui32);
beschi_err_t beschi_WriteFloat(beschi_DataAccess *w, const float f);
beschi_err_t beschi_WriteDouble(beschi_DataAccess *w, const double d);
beschi_err_t beschi_WriteString(beschi_DataAccess *w, char* const *s, const {# STRING_SIZE_TYPE_NATIVE #} len);

// end of standard utility declarations
///////////////////////////////////////


///////////////////////////////////////
// struct/message declarations

