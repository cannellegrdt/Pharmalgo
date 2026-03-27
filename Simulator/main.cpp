/*
** EPITECH PROJECT, 2025
** Pharmalgo
** File description:
** main.cpp
*/

#include "sim.hpp"
#include <unistd.h>

extern const uint8_t OUTPUTS[] = { SORTIE_1, SORTIE_2, SORTIE_3, SORTIE_4 };
extern const int N_OUTPUTS = sizeof(OUTPUTS) / sizeof(OUTPUTS[0]);

void cablageTest();

void run() {
    cablageTest();
}

int main() {
    sim_init();
    run();
    return 0;
}
