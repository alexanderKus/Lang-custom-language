#ifndef clang_chunk_h
#define clang_chunk_h

#include "common.h"

typedef enum {
  OP_RETURN,
} OpCode;

typedef struct {
  int count;
  int capacity;
  uint8_t *code;
} Chunk;

void initChunk(Chunk* Chunk);
void writeChunk(Chunk* Chunk, uint8_t byte);
void freeChunk(Chunk* chunk);

#endif