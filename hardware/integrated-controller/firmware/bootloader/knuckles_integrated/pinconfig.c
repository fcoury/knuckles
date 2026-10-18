#include "boards.h"
#include "uf2/configkeys.h"
__attribute__((used, section(".bootloaderConfig")))
const uint32_t bootloaderConfig[] = {
    CFG_MAGIC0, CFG_MAGIC1, 5, 100,
    204, 0x100000, 205, 0x40000,
    208, (USB_DESC_VID << 16) | USB_DESC_UF2_PID,
    209, 0xada52840, 210, 0x20,
    0, 0, 0, 0, 0, 0, 0, 0
};
