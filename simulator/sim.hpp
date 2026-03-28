/*
** EPITECH PROJECT, 2025
** Pharmalgo
** File description:
** sim.hpp
*/

#include <stdint.h>

// Logic states
#define HIGH 1
#define LOW  0

// Pins available for the cross
#define SORTIE_1  15
#define SORTIE_2  16
#define SORTIE_3  14
#define SORTIE_4  17

// Initializes the simulator
void sim_init();

// Allows you to set the value of a pin
void sim(uint8_t pin, uint8_t value);

