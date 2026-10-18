#include "boards.h"

/* The bootloader owns TWI1 only while running. Bounded register transactions
 * use the Nordic peripheral directly; no RTOS or Zephyr driver exists here. */
static bool wait_event(volatile uint32_t *event) {
    for (unsigned us = 0; us < 1000; ++us) {
        if (*event) return true;
        if (NRF_TWI1->EVENTS_ERROR) return false;
        NRFX_DELAY_US(1);
    }
    return false;
}
static bool pmic_write(uint8_t reg, uint8_t value) {
    NRF_TWI1->ERRORSRC = 7;
    NRF_TWI1->EVENTS_ERROR = 0;
    NRF_TWI1->EVENTS_STOPPED = 0;
    NRF_TWI1->EVENTS_TXDSENT = 0;
    NRF_TWI1->ADDRESS = 0x6a;
    NRF_TWI1->TXD = reg;
    NRF_TWI1->TASKS_STARTTX = 1;
    bool ok = wait_event(&NRF_TWI1->EVENTS_TXDSENT);
    if (ok) {
        NRF_TWI1->EVENTS_TXDSENT = 0;
        NRF_TWI1->TXD = value;
        ok = wait_event(&NRF_TWI1->EVENTS_TXDSENT);
    }
    NRF_TWI1->TASKS_STOP = 1;
    bool stopped = wait_event(&NRF_TWI1->EVENTS_STOPPED);
    return ok && stopped;
}
void board_init2(void) {
    nrf_gpio_pin_clear(8); nrf_gpio_cfg_output(8); // CHG_ALLOW stays off.
    nrf_gpio_pin_clear(5); nrf_gpio_cfg_output(5); // BATT_SENSE_EN
    for (unsigned pin = 26; pin <= 27; ++pin)
        nrf_gpio_cfg(pin, NRF_GPIO_PIN_DIR_INPUT, NRF_GPIO_PIN_INPUT_CONNECT,
                     NRF_GPIO_PIN_NOPULL, NRF_GPIO_PIN_S0D1, NRF_GPIO_PIN_NOSENSE);
    NRF_TWI1->PSEL.SDA = 26; NRF_TWI1->PSEL.SCL = 27;
    NRF_TWI1->FREQUENCY = TWI_FREQUENCY_FREQUENCY_K100;
    NRF_TWI1->ENABLE = TWI_ENABLE_ENABLE_Enabled;
    // Disable a watchdog inherited from the application before a long DFU.
    // Hardware CE stays off even if the device is absent or the bus fails.
    pmic_write(4, 0x8f); // Charging disabled, 20 mA ceiling.
    pmic_write(7, 0x8b); // TS + 12 h timer; watchdog off during DFU.
    pmic_write(8, 0x49); // 100 mA USB input limit, including before enumeration.
    pmic_write(10, 0x40);
}
void board_teardown2(void) {
    NRF_TWI1->ENABLE = 0;
    nrf_gpio_cfg_default(26); nrf_gpio_cfg_default(27);
}
void tud_suspend_cb(bool remote_wakeup_en) {
    (void)remote_wakeup_en;
    // DFU has no need for Bluetooth wakeup. Power off on host suspend;
    // reconnect USB to restore SYS. Also works with an empty/absent battery.
    pmic_write(10, 0x4c);
}
