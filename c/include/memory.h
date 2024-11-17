#ifndef clang_memory_h
#define clang_memory_h

#include "common.h"

#define GROW_CAPACITY(capacity) \
  ((capacity) < 8 ? 8 : (capacity) * 2)

#define GROW_ARRAY(type, pointer, oldCount, newCount) \
  (type*)reallocate(pointer, sizeof(type) * (oldCount), \
    sizeof(type) * (newCount))

#define FREE_ARRAY(type, pointer, oldCount) \
  reallocate(pointer, sizeof(type) * (oldCount), 0)

/**
 *  | oldSize  | newSize  | Operation                |
 *  |----------+----------+--------------------------|
 *  | 0        | Non-zero | allocate new block       |
 *  | Non-zero | 0        | free allocate            |
 *  | Non-zero | <oldSize | shrink existing allocate |
 *  | Non-zero | >oldSize | grow existing allocate   |
 */
void* reallocate(void* pointer, size_t oldSize, size_t newSize);

#endif