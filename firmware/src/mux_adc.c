#include <zephyr/kernel.h>
#include <zephyr/drivers/gpio.h>
#include <zephyr/drivers/adc.h>

/* Define the MUX address pins from your DeviceTree */
static const struct gpio_dt_spec mux_b0 = GPIO_DT_SPEC_GET(DT_NODELABEL(mux_b0), gpios);
static const struct gpio_dt_spec mux_b1 = GPIO_DT_SPEC_GET(DT_NODELABEL(mux_b1), gpios);
static const struct gpio_dt_spec mux_b2 = GPIO_DT_SPEC_GET(DT_NODELABEL(mux_b2), gpios);

/* Define the ADC device */
static const struct device *adc_dev = DEVICE_DT_GET(DT_NODELABEL(adc));

#define ADC_RESOLUTION 12
#define ADC_CHANNEL_COUNT 8

// Buffer to store one full "sweep" of 8 sensors across 8 ADC pins
static int16_t sample_buffer[ADC_CHANNEL_COUNT];

void set_mux_address(uint8_t addr) {
    gpio_pin_set_dt(&mux_b0, (addr >> 0) & 1);
    gpio_pin_set_dt(&mux_b1, (addr >> 1) & 1);
    gpio_pin_set_dt(&mux_b2, (addr >> 2) & 1);
    // TMR sensors are fast, but MUXes need a tiny bit of time to settle
    k_busy_wait(10); 
}

void read_all_tmr_sensors() {
    for (uint8_t mux_addr = 0; mux_addr < 8; mux_addr++) {
        set_mux_address(mux_addr);

        for (uint8_t adc_ch = 0; adc_ch < ADC_CHANNEL_COUNT; adc_ch++) {
            struct adc_sequence sequence = {
                .channels    = BIT(adc_ch),
                .buffer      = &sample_buffer[adc_ch],
                .buffer_size = sizeof(sample_buffer[adc_ch]),
                .resolution  = ADC_RESOLUTION,
            };

            int err = adc_read(adc_dev, &sequence);
            if (err) {
                printk("ADC read failed: %d\n", err);
            }
        }
        // At this point, sample_buffer contains data for 8 sensors 
        // at the current MUX address. Process them here!
    }
}
