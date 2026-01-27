#include <stdio.h>

/* GPIO specs for Bank A */
static const struct gpio_dt_spec mux_a[] = {
	GPIO_DT_SPEC_GET(DT_NODELABEL(mux_a0), gpios),
};

/* GPIO specs for Bank B */
static const struct gpio_dt_spec mux_b[] = {
	GPIO_DT_SPEC_GET(DT_NODELABEL(mux_b0), gpios),
	GPIO_DT_SPEC_GET(DT_NODELABEL(mux_b1), gpios),
	GPIO_DT_SPEC_GET(DT_NODELABEL(mux_b2), gpios),
};

void init_muxes(void) {
	gpio_pin_configure_dt(&mux_a[0], GPIO_OUTPUT_INACTIVE);
	for (int i = 0; i < 3; i++) {
		gpio_pin_configure_dt(&mux_b[i], GPIO_OUTPUT_INACTIVE);
	}
}

void set_bank_b_address(uint8_t addr) {
	for (int i = 0; i < 3; i++) {
		gpio_pin_set_dt(&mux_b[i], (addr >> i) & 1);
	}
}

int main(void)
{
	printf("Hello World! %s\n", CONFIG_BOARD_TARGET);

	return 0;
}

# if 0
Optimized C Code for 5ms Scanning
Since you're using enable-gpio-config = <2 ...>, the nPM1300 driver handles the GPIO2 work behind the scenes when you call the regulator API.

#include <zephyr/drivers/regulator.h>

const struct device *tmr_pwr = DEVICE_DT_GET(DT_NODELABEL(npm1300_ldsw1));

void scan_matrix(void) {
    // 1. Flip the switch (GPIO2 goes high internally)
    regulator_enable(tmr_pwr);

    // 2. Very short stabilization wait (Load switch is fast!)
    k_busy_wait(100); // 100 microseconds is usually plenty for LDSW

    // 3. Run your ADC scan logic
    read_all_tmr_sensors();

    // 4. Kill the power to the sensors immediately
    regulator_disable(tmr_pwr);
}
#endif
