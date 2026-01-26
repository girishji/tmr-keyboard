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

