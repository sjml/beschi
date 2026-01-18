#ifdef __cplusplus
}
#endif

#endif // INCLUDE_BESCHI_H


// end of struct/message declarations
///////////////////////////////////////


#ifdef BESCHI_IMPLEMENTATION

//////////////////////////////////////////////////////////////////////////////
//
//   IMPLEMENTATION
//


#ifndef BESCHI_MALLOC
    #define BESCHI_MALLOC(size)             malloc(size)
    #define BESCHI_REALLOC(ptr, newSize)    realloc(ptr, newSize)
    #define BESCHI_FREE(ptr)                free(ptr)
#endif


///////////////////////////////////////
// standard utility definitions

bool beschi_IsFinished(const beschi_DataAccess *r) {
    return r->position >= r->bufferSize;
}

beschi_err_t beschi_ReadUInt8(beschi_DataAccess *r, uint8_t *ui8) {
    if (r->bufferSize < r->position + 1) {
        return BESCHI_ERR_EOF;
    }
    memcpy(ui8, r->buffer + r->position, 1);
    r->position += 1;
    return BESCHI_ERR_OK;
}

beschi_err_t beschi_ReadBool(beschi_DataAccess *r, bool *b) {
    uint8_t byteVal;
    beschi_err_t err = beschi_ReadUInt8(r, &byteVal);
    if (err != BESCHI_ERR_OK) {
        return err;
    }
    *b = byteVal > 0;
    return BESCHI_ERR_OK;
}

beschi_err_t beschi_ReadInt16(beschi_DataAccess *r, int16_t *i16) {
    if (r->bufferSize < r->position + 2) {
        return BESCHI_ERR_EOF;
    }
    memcpy(i16, r->buffer + r->position, 2);
    r->position += 2;
    return BESCHI_ERR_OK;
}

beschi_err_t beschi_ReadUInt16(beschi_DataAccess *r, uint16_t *ui16) {
    if (r->bufferSize < r->position + 2) {
        return BESCHI_ERR_EOF;
    }
    memcpy(ui16, r->buffer + r->position, 2);
    r->position += 2;
    return BESCHI_ERR_OK;
}

beschi_err_t beschi_ReadInt32(beschi_DataAccess *r, int32_t *i32) {
    if (r->bufferSize < r->position + 4) {
        return BESCHI_ERR_EOF;
    }
    memcpy(i32, r->buffer + r->position, 4);
    r->position += 4;
    return BESCHI_ERR_OK;
}

beschi_err_t beschi_ReadUInt32(beschi_DataAccess *r, uint32_t *ui32) {
    if (r->bufferSize < r->position + 4) {
        return BESCHI_ERR_EOF;
    }
    memcpy(ui32, r->buffer + r->position, 4);
    r->position += 4;
    return BESCHI_ERR_OK;
}

beschi_err_t beschi_ReadInt64(beschi_DataAccess *r, int64_t *i64) {
    if (r->bufferSize < r->position + 8) {
        return BESCHI_ERR_EOF;
    }
    memcpy(i64, r->buffer + r->position, 8);
    r->position += 8;
    return BESCHI_ERR_OK;
}

beschi_err_t beschi_ReadUInt64(beschi_DataAccess *r, uint64_t *ui64) {
    if (r->bufferSize < r->position + 8) {
        return BESCHI_ERR_EOF;
    }
    memcpy(ui64, r->buffer + r->position, 8);
    r->position += 8;
    return BESCHI_ERR_OK;
}

beschi_err_t beschi_ReadFloat(beschi_DataAccess *r, float *f) {
    if (r->bufferSize < r->position + 4) {
        return BESCHI_ERR_EOF;
    }
    memcpy(f, r->buffer + r->position, 4);
    r->position += 4;
    return BESCHI_ERR_OK;
}

beschi_err_t beschi_ReadDouble(beschi_DataAccess *r, double *d) {
    if (r->bufferSize < r->position + 8) {
        return BESCHI_ERR_EOF;
    }
    memcpy(d, r->buffer + r->position, 8);
    r->position += 8;
    return BESCHI_ERR_OK;
}

beschi_err_t beschi_ReadString(beschi_DataAccess *r, char **s, {# STRING_SIZE_TYPE_LOWER #}_t *len) {
    beschi_err_t err;
    err = beschi_Read{# STRING_SIZE_TYPE #}(r, len);
    if (err != BESCHI_ERR_OK) {
        return err;
    }
    if (r->bufferSize < r->position + *len) {
        return BESCHI_ERR_EOF;
    }
    *s = (char*)BESCHI_MALLOC((size_t)(*len + 1));
    if (*s == NULL) { return BESCHI_ERR_ALLOCATION_FAILURE; }
    memcpy(*s, r->buffer + r->position, *len);
    (*s)[*len] = '\0';
    r->position += *len;
    return BESCHI_ERR_OK;
}



beschi_err_t beschi_WriteUInt8(beschi_DataAccess *w, const uint8_t ui8) {
    if (w->bufferSize < w->position + 1) {
        return BESCHI_ERR_EOF;
    }
    w->buffer[w->position] = ui8;
    w->position += 1;
    return BESCHI_ERR_OK;
}

beschi_err_t beschi_WriteBool(beschi_DataAccess *w, const bool b) {
    beschi_err_t err;
    err = beschi_WriteUInt8(w, (uint8_t)(b ? 1 : 0));
    if (err != BESCHI_ERR_OK) {
        return err;
    }
    return BESCHI_ERR_OK;
}

beschi_err_t beschi_WriteInt16(beschi_DataAccess *w, const int16_t i16) {
    if (w->bufferSize < w->position + 2) {
        return BESCHI_ERR_EOF;
    }
    memcpy(w->buffer + w->position, &i16, 2);
    w->position += 2;
    return BESCHI_ERR_OK;
}

beschi_err_t beschi_WriteUInt16(beschi_DataAccess *w, const uint16_t ui16) {
    if (w->bufferSize < w->position + 2) {
        return BESCHI_ERR_EOF;
    }
    memcpy(w->buffer + w->position, &ui16, 2);
    w->position += 2;
    return BESCHI_ERR_OK;
}

beschi_err_t beschi_WriteInt32(beschi_DataAccess *w, const int32_t i32) {
    if (w->bufferSize < w->position + 4) {
        return BESCHI_ERR_EOF;
    }
    memcpy(w->buffer + w->position, &i32, 4);
    w->position += 4;
    return BESCHI_ERR_OK;
}

beschi_err_t beschi_WriteUInt32(beschi_DataAccess *w, const uint32_t ui32) {
    if (w->bufferSize < w->position + 4) {
        return BESCHI_ERR_EOF;
    }
    memcpy(w->buffer + w->position, &ui32, 4);
    w->position += 4;
    return BESCHI_ERR_OK;
}

beschi_err_t beschi_WriteInt64(beschi_DataAccess *w, const int64_t i64) {
    if (w->bufferSize < w->position + 8) {
        return BESCHI_ERR_EOF;
    }
    memcpy(w->buffer + w->position, &i64, 8);
    w->position += 8;
    return BESCHI_ERR_OK;
}

beschi_err_t beschi_WriteUInt64(beschi_DataAccess *w, const uint64_t ui64) {
    if (w->bufferSize < w->position + 8) {
        return BESCHI_ERR_EOF;
    }
    memcpy(w->buffer + w->position, &ui64, 8);
    w->position += 8;
    return BESCHI_ERR_OK;
}

beschi_err_t beschi_WriteFloat(beschi_DataAccess *w, const float f) {
    if (w->bufferSize < w->position + 4) {
        return BESCHI_ERR_EOF;
    }
    memcpy(w->buffer + w->position, &f, 4);
    w->position += 4;
    return BESCHI_ERR_OK;
}

beschi_err_t beschi_WriteDouble(beschi_DataAccess *w, const double d) {
    if (w->bufferSize < w->position + 8) {
        return BESCHI_ERR_EOF;
    }
    memcpy(w->buffer + w->position, &d, 8);
    w->position += 8;
    return BESCHI_ERR_OK;
}

beschi_err_t beschi_WriteString(beschi_DataAccess *w, char* const *s, const {# STRING_SIZE_TYPE_LOWER #}_t len) {
    beschi_err_t err;
    err = beschi_Write{# STRING_SIZE_TYPE #}(w, len);
    if (err != BESCHI_ERR_OK) {
        return err;
    }
    if (w->bufferSize < w->position + len) {
        return BESCHI_ERR_EOF;
    }
    memcpy(w->buffer + w->position, *s, len);
    w->position += len;
    return BESCHI_ERR_OK;
}

// end of standard utility definitions
///////////////////////////////////////


///////////////////////////////////////
// struct/message definitions

