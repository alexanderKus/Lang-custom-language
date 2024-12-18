#include "include/common.h"
#include "include/vm.h"
#include "include/chunk.h"
#include "include/debug.h"

int main(int argc, char* argv[]){
  initVM();
  Chunk chunk = {0};
  initChunk(&chunk);
  int constant = addConstant(&chunk, 1.2);
  writeChunk(&chunk, OP_CONSTANT, 123);
  writeChunk(&chunk, constant, 123);
  writeChunk(&chunk, OP_RETURN, 123);

  //disassembleChunk(&chunk, "test chunk");
  interpret(&chunk);
  freeVM();
  freeChunk(&chunk);
  return 0;
}
