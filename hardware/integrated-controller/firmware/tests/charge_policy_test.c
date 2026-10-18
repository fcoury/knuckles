#include "../src/charge_policy.h"
#include <assert.h>
#include <errno.h>
#include <stdio.h>
#include <string.h>

static uint8_t regs[13];
static bool allowed, fail_gpio;
static int writes, enables, fail_read = -1, fail_write = -1, corrupt_write = -1;
static int read_reg(uint8_t reg, uint8_t *value) {
    if (reg == fail_read) return -EIO;
    *value = regs[reg];
    if (reg == 1) regs[reg] &= ~4; // Safety fault is read-to-clear in silicon.
    return 0;
}
static int write_reg(uint8_t reg, uint8_t value) {
    if (reg == fail_write) return -EIO;
    ++writes;
    regs[reg] = value ^ (reg == corrupt_write ? 1 : 0);
    return 0;
}
static int allow(bool value) {
    if (fail_gpio) return -EIO;
    if (allowed != value) regs[1] &= ~4; // CE edges may clear the timer flag.
    allowed = value;
    if (value) {
        ++enables;
        assert(regs[3] == 0x46 && !(regs[4] & 0x80));
        assert(regs[7] == 0x89 && regs[8] == 0x4a);
        assert(regs[10] == 0x40 && regs[11] == 0xc0);
    }
    return 0;
}
static struct charge_io io = {read_reg, write_reg, allow};
static void reset(void) {
    memset(regs,0,sizeof(regs)); regs[12] = 0x41; regs[0] = 1;
    allowed = fail_gpio = false; writes = enables = 0;
    fail_read = fail_write = corrupt_write = -1;
}
int main(void) {
    struct charge_policy p;
    const unsigned capacities[] = {110,250,500};
    const uint8_t codes[] = {15,32,37};
    for (unsigned i = 0; i < 3; ++i) {
        reset(); assert(!charge_init(&p,io,capacities[i],true));
        assert(regs[4] == (0x80 | codes[i]) && !allowed);
        assert(!charge_step(&p,USB_UNCONFIGURED) && !allowed);
        assert(!charge_step(&p,USB_CONFIGURED) && allowed);
        int before = writes, start_count = enables;
        for (unsigned j = 0; j < 500; ++j) assert(!charge_step(&p,USB_CONFIGURED));
        assert(writes == before && enables == start_count); // No timer restarts while polling.
        assert(!charge_step(&p,USB_SUSPENDED) && !allowed && regs[10] == 0x44);
        assert(!charge_step(&p,USB_CONFIGURED) && allowed);
        regs[1] = 4;
        assert(charge_step(&p,USB_CONFIGURED) < 0 && !allowed && p.fault);
        assert(charge_step(&p,USB_CONFIGURED) < 0 && !allowed); // Read-clear does not erase latch.
    }
    reset(); assert(!charge_init(&p,io,110,false));
    assert(!charge_step(&p,USB_CONFIGURED) && !allowed);
    reset(); assert(charge_init(&p,io,1000,true) < 0 && !allowed);
    reset(); regs[12] = 0x40; assert(charge_init(&p,io,110,true) < 0 && !allowed);
    reset(); regs[1] = 4; assert(charge_init(&p,io,110,true) < 0 && !allowed);
    for (int reg = 3; reg <= 11; ++reg) {
        reset(); fail_write=reg;
        assert(charge_init(&p,io,110,true) < 0 && !allowed);
        reset(); corrupt_write=reg;
        assert(charge_init(&p,io,110,true) < 0 && !allowed);
        reset(); assert(!charge_init(&p,io,110,true));
        assert(!charge_step(&p,USB_CONFIGURED)); regs[reg] ^= 1;
        assert(charge_step(&p,USB_CONFIGURED) < 0 && !allowed);
        reset(); assert(!charge_init(&p,io,110,true));
        assert(!charge_step(&p,USB_CONFIGURED)); fail_read=reg;
        assert(charge_step(&p,USB_CONFIGURED) < 0 && !allowed);
    }
    reset(); assert(!charge_init(&p,io,500,true));
    assert(!charge_step(&p,USB_CONFIGURED)); regs[1]=0x40;
    assert(!charge_step(&p,USB_SUSPENDED));
    assert(!allowed && p.powered_off && regs[10] == 0x4c && regs[7] == 0x8b);
    reset(); assert(!charge_init(&p,io,110,true));
    assert(!charge_step(&p,USB_SUSPENDED));
    regs[10]=0x40; // Documented auto-clear after VIN unplug/replug.
    assert(!charge_step(&p,USB_UNCONFIGURED) && !allowed);
    assert(!charge_step(&p,USB_CONFIGURED) && allowed);
    reset(); assert(!charge_init(&p,io,110,true)); regs[0] = 0x81;
    assert(charge_step(&p,USB_CONFIGURED) < 0 && !allowed);
    reset(); assert(!charge_init(&p,io,110,true)); regs[0] = 0;
    assert(!charge_step(&p,USB_CONFIGURED) && !allowed);
    reset(); assert(!charge_init(&p,io,110,true));
    assert(!charge_step(&p,USB_CONFIGURED)); regs[1]=4;
    assert(charge_step(&p,USB_SUSPENDED) < 0 && p.fault && !allowed);
    assert(charge_step(&p,USB_CONFIGURED) < 0 && !allowed);
    reset(); assert(!charge_init(&p,io,110,true));
    assert(!charge_step(&p,USB_CONFIGURED)); fail_gpio=true;
    assert(charge_step(&p,USB_SUSPENDED) < 0 && (regs[4] & 0x80));
    puts("Charging policy: profiles, authorization, no periodic restarts, readback/I2C faults, timer latch, suspend and UVLO passed.");
}
