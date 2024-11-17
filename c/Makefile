# Define the compiler
CC = gcc

# Define compiler flags
CFLAGS = -g -Wall -O0 -std=c11
CFLAGS += -Iinclude  # Include the 'include' directory for headers

# Define the source files
SRC = $(wildcard *.c)

# Define the object files
OBJ = $(SRC:.c=.o)

# Define the target executable
TARGET = clang

# Rule to build the target executable
all: $(TARGET)

$(TARGET): $(OBJ)
	$(CC) $(CFLAGS) -o $(TARGET) $(OBJ)

# Rule to compile each source file into an object file
%.o: %.c
	$(CC) $(CFLAGS) -c $< -o $@

# Clean rule to remove object files and the executable
clean:
	rm -f $(OBJ) $(TARGET)
