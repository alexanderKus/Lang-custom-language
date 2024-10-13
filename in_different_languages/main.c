#include <stdio.h>

int main(void){
  int a = 1;
  {
    int a = a + 2;
    printf("a: %d\n",a);
  }
  return 0;
}