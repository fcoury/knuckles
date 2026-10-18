#pragma once
// Private engineering tests only: 1209:0001 is not a unique product PID.
// Obtain a product allocation before distributing or manufacturing devices.
#define USB_DESC_VID 0x1209
#define USB_DESC_UF2_PID 0x0001
#define USB_DESC_CDC_ONLY_PID 0x0001
#define UF2_PRODUCT_NAME "Knuckles integrated prototype"
#define UF2_VOLUME_LABEL "KNUCKLES"
#define UF2_BOARD_ID "nRF52840-knuckles-integrated-prototype"
#define UF2_INDEX_URL "https://github.com/fcoury/knuckles"
#define BLEDIS_MANUFACTURER "Knuckles prototype"
#define BLEDIS_MODEL "Integrated nRF52840"
#define LEDS_NUMBER 0
#define LED_STATE_ON 1
#define BUTTONS_NUMBER 2
// Unconnected GPIOs: double-tap RESET is the normal DFU entry method.
#define BUTTON_1 13
#define BUTTON_2 14
#define BUTTON_PULL NRF_GPIO_PIN_PULLUP
#define ENABLE_DCDC_0 0
#define ENABLE_DCDC_1 1
