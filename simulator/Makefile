##
## EPITECH PROJECT, 2026
## Pharmalgo
## File description:
## Makefile
##

.PHONY: all hardware clean fclean re

TARGET    = challenge
HW_TARGET = challenge_hw
CXX       = g++
CXXFLAGS  = -Wall -Wextra -std=c++17

SRC    = main.cpp \
         ../scripts/cablageTest.cpp
HW_SRC = main.cpp \
         ../scripts/cablageTest.cpp \
         hardware.cpp

LIB = libsim.a

# ── Simulator build (default) ─────────────────────────────────────────────────
all: $(TARGET)

$(TARGET): $(SRC) $(LIB)
	$(CXX) $(CXXFLAGS) $(SRC) $(LIB) -o $(TARGET)

# ── Hardware build (Raspberry Pi 5) ──────────────────────────────────────────
# Requires: sudo apt install liblgpio-dev
hardware: $(HW_TARGET)

$(HW_TARGET): $(HW_SRC)
	$(CXX) $(CXXFLAGS) $(HW_SRC) -o $(HW_TARGET) -llgpio

# ─────────────────────────────────────────────────────────────────────────────
clean:
	rm -f $(TARGET) $(HW_TARGET)

fclean: clean

re: fclean all
