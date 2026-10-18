/* BQ25186 board policy; units and register values follow TI SLUSF69A. */
#pragma once
#include <stdbool.h>
#include <stdint.h>

enum usb_power { USB_UNCONFIGURED, USB_CONFIGURED, USB_SUSPENDED };
struct charge_io {
    int (*read)(uint8_t reg, uint8_t *value);
    int (*write)(uint8_t reg, uint8_t value);
    int (*allow)(bool allow);
};
struct charge_policy {
    struct charge_io io;
    uint8_t expected[12];
    bool verified, fault, initialized, powered_off, allowing;
};
int charge_init(struct charge_policy *p, struct charge_io io, unsigned capacity, bool verified);
int charge_step(struct charge_policy *p, enum usb_power usb);
