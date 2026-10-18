#include "charge_policy.h"
#include <errno.h>
#include <string.h>

static int set_allow(struct charge_policy *p, bool value) {
    int rc = p->io.allow(value);
    if (!rc) p->allowing = value;
    return rc;
}
static int write_checked(struct charge_policy *p, uint8_t reg, uint8_t value) {
    uint8_t actual;
    int rc = p->io.write(reg, value);
    if (!rc) rc = p->io.read(reg, &actual);
    if (!rc && actual != value) rc = -EIO;
    if (!rc) p->expected[reg] = value;
    return rc;
}
static int fail(struct charge_policy *p) {
    p->fault = true;
    int gate_rc = set_allow(p, false);
    int disable_rc = p->io.write(4, 0x80 | (p->expected[4] & 0x7f));
    /* Keep the timer/temperature protection, but stop a watchdog reset from
     * automatically clearing this fault latch. If I2C is broken, the HW
     * watchdog still removes SYS; CE defaults off on reset. */
    if (!gate_rc || !disable_rc) p->io.write(7, 0x8b);
    return -EIO;
}
int charge_init(struct charge_policy *p, struct charge_io io, unsigned capacity, bool verified) {
    memset(p, 0, sizeof(*p)); p->io = io; p->verified = verified;
    if (set_allow(p, false)) return fail(p);
    uint8_t code;
    switch (capacity) {
    case 110: code = 15; break; // 20 mA
    case 250: code = 32; break; // 50 mA
    case 500: code = 37; break; // 100 mA
    default: return fail(p);
    }
    uint8_t id, status;
    if (io.read(12, &id) || (id & 15) != 1 || io.read(1, &status) || (status & 4))
        return fail(p);
    // 4.2 V; disabled; 20% precharge/10% termination; 3.0 V UVLO;
    // TS enabled, 12 h safety timer, 160 s HW watchdog; 100 mA input;
    // no TS pushbutton polling; SYS 4.5 V; 0..45 C charging window.
    uint8_t values[] = {0x46, (uint8_t)(0x80 | code), 0x24, 0x16,
                        0x89, 0x49, 0x10, 0x40, 0xc0};
    for (unsigned reg = 3; reg <= 11; ++reg)
        if (write_checked(p, reg, values[reg - 3])) return fail(p);
    p->initialized = true;
    return 0;
}
int charge_step(struct charge_policy *p, enum usb_power usb) {
    if (!p->initialized || p->fault || p->powered_off) return -EIO;
    bool enable = p->verified && usb == USB_CONFIGURED;
    uint8_t status, status0;
    // Read the timer fault before changing CE: CE toggles can clear that flag.
    // Read failures take the hardware/software disable paths in fail().
    if (p->io.read(1, &status) || (status & 4) || p->io.read(0, &status0)) return fail(p);
    if (!(status0 & 1)) enable = false; // Require physical VIN power-good too.
    if (!enable && p->allowing && set_allow(p, false)) return fail(p);
    if (enable && (status0 & 0x80)) return fail(p); // Open NTC or VBAT below HALT.
    if (usb == USB_SUSPENDED && (status & 0x40)) {
        // Force-BAT is ignored below UVLO. Shut SYS off instead; reconnect USB
        // to recover. Do not let the watchdog periodically wake the system.
        if (set_allow(p, false) || write_checked(p, 7, 0x8b)) return fail(p);
        p->powered_off = true;
        return p->io.write(10, 0x4c); // Power disappears; cannot read back.
    }
    // Unexpected register reset/corruption must not silently restart charging.
    for (unsigned reg = 3; reg <= 11; ++reg) {
        uint8_t actual;
        if (p->io.read(reg, &actual)) return fail(p);
        // VIN removal/reinsertion automatically clears force-BAT mode.
        if (reg == 10 && usb != USB_SUSPENDED && p->expected[10] == 0x44 && actual == 0x40)
            p->expected[10] = 0x40;
        if (actual != p->expected[reg]) return fail(p);
    }
    uint8_t input = usb == USB_CONFIGURED ? 0x4a : 0x49;
    uint8_t sys = usb == USB_SUSPENDED ? 0x44 : 0x40;
    uint8_t current = (p->expected[4] & 0x7f) | (enable ? 0 : 0x80);
    if (input != p->expected[8] || sys != p->expected[10] || current != p->expected[4]) {
        if (set_allow(p, false) || write_checked(p, 8, input) ||
            write_checked(p, 10, sys) || write_checked(p, 4, current)) return fail(p);
    }
    if (enable && !p->allowing && set_allow(p, true)) return fail(p);
    return 0;
}
