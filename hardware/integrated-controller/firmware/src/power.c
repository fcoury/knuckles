#include <zephyr/device.h>
#include <zephyr/drivers/gpio.h>
#include <zephyr/drivers/i2c.h>
#include <zephyr/init.h>
#include <zephyr/kernel.h>
#include <zephyr/logging/log.h>
#include <zephyr/usb/usb_device.h>
#include <zephyr/sys/atomic.h>
#include "charge_policy.h"
#if IS_ENABLED(CONFIG_ZMK_USB)
#include <zmk/usb.h>
#include <zmk/event_manager.h>
#include <zmk/events/usb_conn_state_changed.h>
#endif

LOG_MODULE_REGISTER(knuckles_power, LOG_LEVEL_INF);
static const struct device *bus = DEVICE_DT_GET(DT_NODELABEL(i2c1));
static const struct gpio_dt_spec allow_pin = GPIO_DT_SPEC_GET(DT_NODELABEL(power_control), enable_gpios);
static const struct gpio_dt_spec interrupt_pin = GPIO_DT_SPEC_GET(DT_NODELABEL(power_control), interrupt_gpios);
static struct gpio_callback interrupt_cb;
static struct charge_policy policy;
#if !IS_ENABLED(CONFIG_ZMK_USB)
static atomic_t usb_flags; // bit 0: configured, bit 1: suspended
#endif
static bool ready;
static int read_reg(uint8_t reg, uint8_t *value) { return i2c_reg_read_byte(bus, 0x6a, reg, value); }
static int write_reg(uint8_t reg, uint8_t value) { return i2c_reg_write_byte(bus, 0x6a, reg, value); }
static int allow_charge(bool allow) { return gpio_pin_set_dt(&allow_pin, allow); }
static void service(struct k_work *work);
K_WORK_DEFINE(service_work, service);
static void poll(struct k_timer *timer) { k_work_submit(&service_work); }
K_TIMER_DEFINE(poll_timer, poll, NULL);

static void service(struct k_work *work) {
    if (!ready) return;
#if IS_ENABLED(CONFIG_ZMK_USB)
    enum usb_power power = zmk_usb_get_status() == USB_DC_SUSPEND ? USB_SUSPENDED :
                           zmk_usb_is_hid_ready() ? USB_CONFIGURED : USB_UNCONFIGURED;
#else
    atomic_val_t flags = atomic_get(&usb_flags);
    enum usb_power power = (flags & 2) ? USB_SUSPENDED :
                           (flags & 1) ? USB_CONFIGURED : USB_UNCONFIGURED;
#endif
    if (charge_step(&policy, power)) {
        LOG_ERR("Charger disabled; fault=%d, SYS off=%d. Inspect before reset.", policy.fault, policy.powered_off);
        return;
    }

}
static void interrupt_handler(const struct device *port, struct gpio_callback *cb, uint32_t pins) {
    k_work_submit(&service_work);
}
#if IS_ENABLED(CONFIG_ZMK_USB)
static int usb_event(const zmk_event_t *event) {
    k_work_submit(&service_work);
    return ZMK_EV_EVENT_BUBBLE;
}
ZMK_LISTENER(knuckles_power, usb_event);
ZMK_SUBSCRIPTION(knuckles_power, zmk_usb_conn_state_changed);
#else
static void usb_event(enum usb_dc_status_code status, const uint8_t *param) {
    if (status == USB_DC_SOF) return;
    switch (status) {
    case USB_DC_CONFIGURED: atomic_set(&usb_flags, 1); break;
    case USB_DC_SUSPEND: atomic_set_bit(&usb_flags, 1); break;
    case USB_DC_RESUME: atomic_clear_bit(&usb_flags, 1); break;
    case USB_DC_RESET:
    case USB_DC_DISCONNECTED:
    case USB_DC_ERROR: atomic_set(&usb_flags, 0); break;
    default: break;
    }
    k_work_submit(&service_work);
}
#endif
static int init_power(void) {
    if (!gpio_is_ready_dt(&allow_pin)) return -ENODEV;
    int rc = gpio_pin_configure_dt(&allow_pin, GPIO_OUTPUT_INACTIVE);
    if (rc || !device_is_ready(bus)) return rc ? rc : -ENODEV;
    unsigned capacity = IS_ENABLED(CONFIG_KNUCKLES_BATTERY_500) ? 500 :
                        IS_ENABLED(CONFIG_KNUCKLES_BATTERY_250) ? 250 : 110;
    struct charge_io io = {.read = read_reg, .write = write_reg, .allow = allow_charge};
    rc = charge_init(&policy, io, capacity, IS_ENABLED(CONFIG_KNUCKLES_BATTERY_VERIFIED));
    if (rc) return rc;
    rc = gpio_pin_configure_dt(&interrupt_pin, GPIO_INPUT);
    if (rc) goto failed;
    gpio_init_callback(&interrupt_cb, interrupt_handler, BIT(interrupt_pin.pin));
    rc = gpio_add_callback(interrupt_pin.port, &interrupt_cb);
    if (rc) goto failed;
    rc = gpio_pin_interrupt_configure_dt(&interrupt_pin, GPIO_INT_EDGE_TO_ACTIVE);
    if (rc) goto failed;
#if !IS_ENABLED(CONFIG_ZMK_USB)
    rc = usb_enable(usb_event);
    if (rc) goto failed;
#endif
    ready = true;
    k_timer_start(&poll_timer, K_SECONDS(30), K_SECONDS(30));
    k_work_submit(&service_work);
    LOG_INF("BQ25186 profile %u mAh; charging authorization %s", capacity,
            IS_ENABLED(CONFIG_KNUCKLES_BATTERY_VERIFIED) ? "enabled" : "disabled");
    return 0;
failed:
    allow_charge(false);
    return rc;
}
SYS_INIT(init_power, APPLICATION, 90);
