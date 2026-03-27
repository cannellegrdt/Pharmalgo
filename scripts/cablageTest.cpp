/*
** EPITECH PROJECT, 2025
** Pharmalgo
** File description:
** cablageTest.cpp
*/

#include "../GivenSimu/sim.hpp"
#include <unistd.h>

extern const uint8_t OUTPUTS[];
extern const int N_OUTPUTS;

#define NB_LEDS = 8
#define TOTAL_NB_LEDS = 320

// Offset of each panel in the 320-element pixel vector
// Order confirmed by reverse engineering applyMatrix():
//   vec[0..63]   -> LEFT   (panel "2")
//   vec[64..127] -> RIGHT  (panel "4")
//   vec[128..191]-> TOP    (panel "1")
//   vec[192..255]-> CENTER (panel "3")
//   vec[256..319]-> BOTTOM (panel "5")
#define PANEL_LEFT 0
#define PANEL_RIGHT 64
#define PANEL_TOP 128
#define PANEL_CENTER 192
#define PANEL_BOTTOM 256

// 8x8 bitmaps — bit 7 = leftmost column (col 0), bit 0 = rightmost (col 7)
static const uint8_t DIGIT_1[NB_LEDS] = {
    0b00011000,
    0b00111000,
    0b01011000,
    0b00011000,
    0b00011000,
    0b00011000,
    0b00011000,
    0b01111110,
};

static const uint8_t DIGIT_2[NB_LEDS] = {
    0b00111100,
    0b01100110,
    0b00000110,
    0b00001100,
    0b00011000,
    0b00110000,
    0b01100000,
    0b01111110,
};

static const uint8_t DIGIT_3[NB_LEDS] = {
    0b00111100,
    0b01100110,
    0b00000110,
    0b00011100,
    0b00000110,
    0b00000110,
    0b01100110,
    0b00111100,
};

static const uint8_t DIGIT_4[NB_LEDS] = {
    0b00001100,
    0b00011100,
    0b00101100,
    0b01001100,
    0b01111110,
    0b00001100,
    0b00001100,
    0b00001100,
};

static const uint8_t DIGIT_5[NB_LEDS] = {
    0b01111110,
    0b01100000,
    0b01100000,
    0b01111100,
    0b00000110,
    0b00000110,
    0b01100110,
    0b00111100,
};

// Fill one 8x8 panel in the pixel array from a bitmap.
// Storage formula (from applyMatrix reverse engineering):
//   pixels[panel_start + row*8 + k] = pixel at (row, col=7-k)
// So iterating k=0..7 fills col 7 down to col 0, matching bit ordering.
static void fillPanel(uint8_t pixels[TOTAL_NB_LEDS], int panel_start, const uint8_t bitmap[NB_LEDS], uint8_t brightness) {
    for (int row = 0; row < NB_LEDS; row++) {
        for (int k = 0; k < NB_LEDS; k++)
            pixels[panel_start + row * NB_LEDS + k] = ((bitmap[row] >> k) & 1) ? brightness : 0;
    }
}

// Send one full frame through the shift register protocol:
//   SORTIE_3 (pin 14) -> leftOE = 1    (enable sending)
//   SORTIE_4 (pin 17) -> currentLeftBit = value
//   SORTIE_2 (pin 16) -> push_back(shiftLeft, currentLeftBit)  [xTOTAL_NB_LEDS]
//   SORTIE_1 (pin 15) -> size==TOTAL_NB_LEDS => applyMatrix + sendFrame(1)
static void sendFrame(const uint8_t pixels[TOTAL_NB_LEDS]) {
    sim(SORTIE_3, HIGH);

    for (int i = 0; i < TOTAL_NB_LEDS; i++) {
        sim(SORTIE_4, pixels[i]);
        sim(SORTIE_2, HIGH);
    }

    sim(SORTIE_1, HIGH);
}

void cablageTest() {
    uint8_t pixels[TOTAL_NB_LEDS] = {0};

    fillPanel(pixels, PANEL_TOP, DIGIT_1, 7);
    fillPanel(pixels, PANEL_LEFT, DIGIT_2, 7);
    fillPanel(pixels, PANEL_CENTER, DIGIT_3, 7);
    fillPanel(pixels, PANEL_RIGHT, DIGIT_4, 7);
    fillPanel(pixels, PANEL_BOTTOM, DIGIT_5, 7);

    sendFrame(pixels);
}
