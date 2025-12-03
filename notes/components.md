To open readable html rendering: VSCode -> Open Preview to the Side icon (looks like a magnifying glass with a document) in the top-right corner (or Cmd-KV)

---

See the section below on comparators

---

The method you proposed using **Analog Multiplexers (Muxes)** is one of two common solutions. The other solution, using **ADC Expanders** (or external multi-channel ADCs), offers a different set of trade-offs in complexity, speed, and signal integrity.

For reading 72 analog inputs on an RP2040, using **ADC Expanders is generally the superior and cleaner solution**, especially for a complex application like a magnetic keyboard.

Here is a comparison of the two approaches:

---

## ⚖️ Analog Mux vs. ADC Expander Comparison

| Feature | Analog Multiplexer (Mux) (e.g., 74HC4051) | ADC Expander (e.g., MCP3208, ADS1115, MCP3008) |
| :--- | :--- | :--- |
| **Required Chip** | Mux IC (e.g., 74HC4051, CD74HC4067) | Multi-channel ADC IC (or breakout board) |
| **Core Function** | **Analog** switching/routing | **Digital** conversion and communication |
| **RP2040 ADC Use** | **Uses** the RP2040's built-in ADC pin(s). | **Bypasses** the RP2040's ADC entirely. |
| **Communication** | **Analog signals** must be routed; uses **Digital GPIO** for channel selection. | Communicates via **Digital Bus** (I²C or SPI). |
| **Pin Count for 72 Inputs** | **High:** $\approx 4 \text{ ADC pins} + 12 \text{ Digital GPIOs}$ (for 9 Muxes) | **Low:** **2 pins** (for I²C) or **4 pins** (for SPI) shared among ALL expanders. |
| **Signal Quality** | **Lower:** Subject to **channel crosstalk**, switch resistance ($R_{ON}$), and the quality of the RP2040's ADC. | **Higher:** Dedicated ADC per chip offers better **noise immunity** and less crosstalk. |
| **Scan Speed** | **Fastest Potential:** Conversion speed is limited only by the RP2040's high ADC sampling rate (up to 500 kS/s). | **Slower Potential:** Limited by the external ADC's sampling rate and the speed of the I²C/SPI bus. |
| **Resolution** | Limited to the RP2040's **12-bit** resolution. | Can select a higher resolution, often **16-bit** (e.g., ADS1115), providing greater analog precision. |

---

## ✅ Why ADC Expanders are Better for a Magnetic Keyboard

For a high-channel count, high-precision application like a magnetic keyboard (which uses Hall effect sensors to measure key position), ADC Expanders offer significant advantages:

### 1. Simplified Wiring and Pin Count

* **Massive Pin Savings:** Instead of using over a dozen digital and analog pins for control/readout, you can read **all 72 inputs** using just **two I²C pins** (SDA/SCL) on the RP2040.
* **Easier PCB Design:** Wiring is much simpler since you can daisy-chain multiple ADC Expanders (e.g., 9x 8-channel ADCs) onto the same I²C bus.

### 2. Improved Accuracy and Resolution

* **Higher Resolution:** Many external ADCs (like the **ADS1115**) offer **16-bit** resolution (65,536 steps), compared to the RP2040's **12-bit** (4,096 steps). This is crucial for precise magnetic key detection, as it provides a smoother, more detailed reading of the key's analog position.
* **Reduced Noise:** Dedicated external ADCs are often designed with better noise rejection and don't suffer from the internal switching artifacts, crosstalk, or power supply noise that can affect signals routed through an analog multiplexer.

### 3. Dedicated Conversion

* With a Mux, the single RP2040 ADC must **sample, settle, and convert** a signal after every channel switch. With an ADC Expander, the conversion happens on the expander chip itself, and the RP2040 simply requests the final digital data over a slow, robust bus (I²C).

**Recommendation:**

For a professional-grade 72-key magnetic keyboard project, use **multiple 8-channel I²C ADC Expanders** (e.g., the **ADS7830** or **ADS1115**). This will minimize wiring complexity and provide superior analog accuracy.

***

Would you like me to find a specific **8-channel I²C ADC expander** that would work well with the RP2040?

---
---

That's an excellent approach. To maximize **scan speed** and minimize **chip count/complexity** for 72 analog inputs, you'll want to focus on **SPI-based** ADC expanders with a high channel count.

SPI is generally faster than I²C, and higher channel counts (like 8 channels) mean you need fewer chips in total ($\frac{72}{8} = 9$ chips).

Here are three suggested ADC expander chips suitable for your high-speed magnetic keyboard application:

---

## ⚡ High-Speed ADC Expander Suggestions

| Chip (Manufacturer) | Channels | Interface | Resolution | Max Sample Rate | Key Advantage for RP2040 |
| :--- | :--- | :--- | :--- | :--- | :--- |
| **1. Texas Instruments TLA2518** | **8** | **SPI** (up to 60 MHz) | **12-bit** (16-bit with averaging) | **1 MSPS** (Million Samples per Second) | **Fastest** per-channel scan rate and includes built-in **averaging filters** for noise reduction. |
| **2. Texas Instruments ADS7028** | **8** | **SPI** (up to 60 MHz) | **12-bit** | **1 MSPS** | Highly optimized for high-speed SPI communication and includes extra features like **Analog Watchdog** and **CRC**. |
| **3. Microchip MCP3208** | **8** | **SPI** | **12-bit** | **100 kSPS** | **Common and Simple.** Excellent starting point, widely supported by libraries, very low cost, and easy to interface. |

---

### In-Depth Chip Analysis

#### 1. Texas Instruments TLA2518 (Best Performance)

This chip is the best choice if **scan speed is your highest priority**.

* **Speed:** With 1 MSPS (Million Samples Per Second) and a 60 MHz SPI bus, you can potentially read all 9 chips (72 channels) extremely quickly. The RP2040's SPI peripheral can easily handle the clock speed.
* **Resolution:** Provides **12-bit** resolution natively, but a key feature is the **programmable averaging filter** which can output a **16-bit result**. This lets you improve the analog precision of the magnetic sensors without slowing down the RP2040's core.
* **Complexity:** Minimal. You only use **4 dedicated SPI pins** (SCK, MOSI, MISO, CS) plus a **Chip Select ($\overline{CS}$) pin** for *each* of the 9 chips, for a total of $3 + 9 = \mathbf{12}$ RP2040 pins.

#### 2. Texas Instruments ADS7028 (High-Speed Alternative)

A very close contender to the TLA2518, offering similar performance with slightly different features.

* **Speed & Resolution:** Also offers **8 channels, 12-bit, and 1 MSPS** over a high-speed SPI bus.
* **Unique Features:** It includes a built-in **Analog Watchdog** (programmable thresholds) which could be useful for quickly detecting if a key moves out of a calibrated range without needing continuous software checking. It also has a **CRC** (Cyclic Redundancy Check) for robust data integrity over the bus.
* **Complexity:** The same $\mathbf{12}$ pins are required as the TLA2518.

#### 3. Microchip MCP3208 (Easiest to Start)

The MCP3208 is a ubiquitous chip, highly recommended if you value simplicity and existing library support over raw speed.

* **Speed:** The 100 kSPS limit means your total scan time for 72 channels will be about **10 times slower** than the TI chips. While 100 kSPS is still fast for general microcontroller tasks, it might be a bottleneck for competitive high-speed analog keyboard scanning.
* **Simplicity:** It's a very simple SAR (Successive Approximation Register) ADC, requiring minimal external components and featuring widely available code examples. It's often available in a beginner-friendly DIP package.
* **Complexity:** The same $\mathbf{12}$ pins are required.

### Pin Count and Wiring Summary

Using a high-speed **SPI-based, 8-channel** solution is the most chip-efficient way to handle 72 inputs:

* **Required Chips:** **9x** 8-channel ADC Expanders.
* **Shared SPI Bus:** **4 RP2040 Pins** (SCK, MOSI, MISO, shared $\overline{CS}$ on bus 0).
* **Individual Chip Select:** **9 RP2040 Pins** (one for each of the 9 expanders).

This totals **13 RP2040 pins** to read all 72 analog inputs, which is highly efficient.

***

Do you want to focus on the **TLA2518** and look at how to implement the **16-bit averaging feature** on the RP2040?

---
---

That's a great question. Connecting multiple SPI ADC expanders (like the TLA2518 or MCP3208) to the RP2040 involves using a **shared bus architecture** for speed and a **separate Chip Select ($\overline{CS}$) line** for device addressing.

Here is how you connect $\mathbf{9}$ of these 8-channel SPI chips to read your 72 magnetic keyboard inputs using the RP2040.

---

## 🔌 Connection Strategy: Shared SPI Bus

The Serial Peripheral Interface (SPI) is ideal for this application because it allows multiple devices to share the clock, data in, and data out lines, simplifying the wiring.

### 1. Shared Bus Connections (4 RP2040 Pins)

The following four pins from the **RP2040's SPI peripheral** (e.g., SPI0 or SPI1) are connected to the corresponding pins on **all 9 ADC chips**:

| RP2040 Pin | ADC Pin (on all 9 chips) | Function |
| :--- | :--- | :--- |
| **SCK** (Serial Clock) | **SCK** | Synchronizes data transfer. |
| **MOSI** (Master Out, Slave In) | **SDI** or **DIN** (Data In) | RP2040 sends commands/configuration to the ADC. |
| **MISO** (Master In, Slave Out) | **SDO** or **DOUT** (Data Out) | ADC sends conversion data back to the RP2040. |
| **GND** | **GND** | Ground reference. |
| **3.3V** | **$V_{DD}$** | Power supply (RP2040 operates at 3.3V). |

### 2. Device Select Connections (9 RP2040 Pins)

The key to reading 72 inputs is the **Chip Select ($\overline{CS}$) pin**. This pin is used to tell the RP2040 which of the 9 ADC chips it wants to talk to at any given moment.

* You will use **9 separate Digital GPIO pins** on the RP2040.
* Each of these 9 GPIO pins is connected to the $\overline{CS}$ (or $\overline{SS}$ / $\overline{EN}$) pin of **one specific ADC chip**.

| RP2040 Pin | ADC Chip | Function |
| :--- | :--- | :--- |
| **GPIO Pin 1** | ADC Chip 1 ($\overline{CS}_1$) | Selects Chip 1 to read inputs 1-8. |
| **GPIO Pin 2** | ADC Chip 2 ($\overline{CS}_2$) | Selects Chip 2 to read inputs 9-16. |
| ... | ... | ... |
| **GPIO Pin 9** | ADC Chip 9 ($\overline{CS}_9$) | Selects Chip 9 to read inputs 65-72. |

### Total Pin Count on the RP2040

$$\text{Total Pins Used} = \underbrace{3 \text{ Shared SPI Data/Clock Pins}}_{\text{SCK, MOSI, MISO}} + \underbrace{9 \text{ Separate Chip Select Pins}}_{\text{CS}_1 \text{ to } \text{CS}_9} = \mathbf{12 \text{ RP2040 Pins}}$$

The remaining pins on the RP2040 (besides power and ground) are available for the rest of your keyboard's functions.

---

## 📚 Reading the Data (Software Protocol)

The reading process involves a simple protocol that the RP2040 must follow for every reading:

1.  **Set Chip Select (Active Low):** The RP2040 pulls the $\overline{CS}$ line for the target ADC chip **LOW**. This *activates* that single chip and puts it on the SPI bus. All other $\overline{CS}$ lines must be **HIGH** (inactive).
2.  **Send Command:** The RP2040 sends a digital command via the **MOSI** line. This command tells the ADC chip which of its 8 internal channels (e.g., Channel 5) to sample and convert.
3.  **Read Data:** The ADC chip performs the conversion and sends the 12-bit (or 16-bit) digital result back to the RP2040 via the **MISO** line.
4.  **Deselect Chip (Inactive High):** The RP2040 pulls the $\overline{CS}$ line **HIGH**. This deactivates the chip and frees the SPI bus for the next selected chip.

The RP2040 would run a scan loop, cycling through all 9 chips, and for each chip, cycling through all 8 channels, to read the position of all 72 magnetic keys.

---
Would you like to explore the specific **pin assignments** on the Raspberry Pi Pico/Pico W that are best suited for the SPI bus?

---
---

100 kSPS stands for **100 Kilo-Samples Per Second**.

It is a unit used to specify the **sampling rate** or **conversion speed** of an Analog-to-Digital Converter (ADC).

Here is a breakdown of what that means:

---

## 🔬 Understanding kSPS

* **SPS:** **Samples Per Second**. This is the fundamental unit of measurement.
* **k:** The metric prefix "kilo," which means $1,000$.
* **100 kSPS** means the ADC can take **100,000 measurements** (or samples) of an analog voltage input every **one second**.

### How It Relates to ADCs

The sampling rate dictates how quickly an ADC can convert a continuous analog signal into discrete digital values.

1.  **Speed:** A higher kSPS rate means the ADC is faster and can handle higher-frequency analog signals without losing information.
2.  **Conversion Time:** If an ADC runs at 100 kSPS, the time it takes to complete one single conversion is:
    $$\frac{1 \text{ second}}{100,000 \text{ samples}} = 0.00001 \text{ seconds} = \mathbf{10 \text{ microseconds} (10 \mu\text{s})}$$
3.  **Nyquist Theorem:** The sampling rate must be at least **twice** the highest frequency component of the analog signal you are trying to measure. For a magnetic keyboard, while the physical movement is slow, a high sampling rate is useful for fast polling and high-precision detection (as discussed with the TLA2518's 1 MSPS rate).

In the context of the **MCP3208** ADC chip mentioned earlier (which has a 100 kSPS maximum rate), it means that each of its 8 channels can be sampled at a maximum combined rate of 100,000 times per second.

---
---

The total **scan time** for your 72 analog inputs depends entirely on the **sampling rate (kSPS)** of the ADC chip you choose and the **overhead time** required to communicate with all 9 chips.

Assuming you use the high-speed **TLA2518** (or a similar 1 MSPS chip) and an efficient coding approach on the RP2040, the theoretical scan time can be calculated as follows:

---

## ⏱️ Theoretical Scan Time Calculation

The scan time is calculated by determining the time it takes for **all 72 channels** to complete one full conversion cycle.

### 1. Conversion Time (TLA2518)

The TLA2518 has a maximum sampling rate of **1 MSPS** (Million Samples Per Second).

$$\text{Time per Sample } (T_{\text{sample}}) = \frac{1 \text{ second}}{1,000,000 \text{ samples}} = 1 \text{ microsecond } (1 \mu\text{s})$$

### 2. Total Channels

$$\text{Total Channels } (N) = 72$$

### 3. Theoretical Minimum Scan Time

The absolute minimum time to convert all channels is the total number of channels multiplied by the time it takes for one sample:

$$\text{Minimum Scan Time} = N \times T_{\text{sample}}$$
$$\text{Minimum Scan Time} = 72 \text{ channels} \times 1 \mu\text{s/channel} = \mathbf{72 \mu\text{s}}$$

In theory, with the **TLA2518**, you could capture a complete snapshot of all 72 key positions in just **72 microseconds**.

---

## 🚀 Realistic Scan Time (Including Overhead)

The theoretical minimum rarely reflects the real-world performance because you must account for **communication overhead** on the SPI bus.

The total realistic scan time ($\mathbf{T_{\text{Scan}}}$) is the sum of the time spent converting signals and the time spent transferring the digital data via SPI:

$$\mathbf{T_{\text{Scan}}} = \text{Conversion Time} + \text{Communication Time}$$

### A. Communication Time (Dominant Factor)

The RP2040 needs to:
1.  **Assert** the Chip Select ($\overline{CS}$) line (digital operation, very fast).
2.  **Send a Command** (via MOSI) to tell the ADC which of the 8 channels to convert (e.g., 1 byte).
3.  **Read the Data** (via MISO) after the conversion is complete (e.g., 2 bytes for 16-bit data).
4.  **Deassert** the Chip Select ($\overline{CS}$) line (very fast).

Using the RP2040's high-speed SPI (up to 60 MHz), the data transfer for one 16-bit reading (2 bytes) is extremely fast, likely only taking **tens of nanoseconds**.

### B. Realistic Estimate

A realistic time estimate for the *combined* conversion and full SPI read/write cycle for a high-speed chip often falls in the range of **5-10 $\mu$s per channel** due to required software overhead (context switching, loop processing, etc.).

$$\text{Realistic Scan Time} \approx 72 \text{ channels} \times 5 \mu\text{s/channel} = \mathbf{360 \mu\text{s}}$$

A complete scan of all 72 inputs is likely to take between **$72 \mu$s** (ideal minimum) and **$400 \mu$s** (realistic maximum for a fast chip).

### Comparing Scan Rates

| ADC Chip | Sample Rate | Estimated $\mathbf{T_{\text{Scan}}}$ for 72 Inputs | Scan Frequency (Hz) |
| :--- | :--- | :--- | :--- |
| **TLA2518** (1 MSPS) | $\mathbf{1 \mu\text{s/channel}}$ | $\approx 72 - 400 \mu\text{s}$ | **2,500 - 14,000 Hz** |
| **MCP3208** (100 kSPS) | $10 \mu\text{s/channel}$ | $\approx 720 \mu\text{s} - 1.5 \text{ ms}$ | **650 - 1,400 Hz** |

Even the slower **MCP3208** provides a scan frequency of over **650 Hz**, meaning you get a full, high-resolution update of all 72 keys 650 times every second, which is **significantly faster** than needed for any human input. The **TLA2518** offers overkill speed but ensures minimal latency.

---
Would you like to look at the specific **SPI pin mappings** on the Raspberry Pi Pico/Pico W to start your wiring diagram?

---
---

Short answer — **SPI is almost certainly the better choice** for nine 8-channel ADC boards (72 channels) on an RP2040, unless you have a specific reason to prefer I²C (very low sample rates, extremely simple wiring, or must use I²C-only ADC chips).

# Practical ways to attach 9 SPI ADCs to an RP2040

Options (ranked by simplicity / reliability):

1. **SPI with 9 CS lines (simplest conceptually)**

   * Share SCLK, MOSI, MISO. Use 9 GPIOs on the RP2040 as CS lines (RP2040 has plenty of GPIOs).
   * Use hardware SPI + DMA to collect samples quickly and reduce CPU load.
   * Decent PCB or tidy ribbon wiring recommended so CS lines don’t pick up noise.

2. **SPI + decoder / demux (fewer MCU pins)**

   * Use a 3-to-8 decoder (74HC138) or 74HC237 plus one extra GPIO for the 9th device. This reduces CS pins to 3 (plus maybe an enable pin).
   * Good when you want to conserve GPIOs.

3. **SPI + GPIO-shift register / SPI-GPIO expander**

   * Use a shift register (74HC595) or SPI GPIO expander to generate CS lines — fewer MCU pins, but adds latency and an extra SPI transaction to change CS state. OK if sample rate is modest.

4. **Daisy-chainable ADCs or ADCs that support multi-device chaining**

   * Some ADC boards support daisy-chaining, letting you read many devices with fewer CS toggles. Check datasheets if you want this optimization.

# Noise, grounding, and analog considerations

* Keep analog inputs short and shielded where possible and use proper decoupling on every ADC board.
* Share analog ground carefully (star ground) if you have many channels.
* Clock lines (SCLK) and CS toggles can inject glitches — use proper routing or small series resistors on digital lines if you experience noise.

# RP2040 tips

* Use the RP2040’s **hardware SPI** and **DMA** to read many channels with minimal CPU usage. You can schedule transfers to read each ADC sequentially and fill a buffer fast.
* If you pick SPI, run it from a dedicated SPI port (or two) and use DMA with a big buffer for bursts of samples.

---
---

# Analog Mux


For 72 analog inputs there are a few common, practical approaches. Below I list popular multiplexer choices, how many chips you’d need, their pros/cons for keyboard/magnetic-switch sensing, and a short recommendation.

---

# Top candidate parts (with citations)

### 1) **CD74HC4067 / 74HC4067 — 16:1 analog MUX**

* You’d need **5 chips** (5×16 = 80 channels, leaves 8 spare).
* Pros: high channel density (fewer ICs/PCB area), cheap and widely available. Typical ON-resistance is fairly high (tens of ohms; TI lists ~70 Ω typ at 4.5 V). Good for general analog routing. ([Texas Instruments][1])

### 2) **74HC4051 — 8:1 analog MUX**

* You’d need **9 chips** (9×8 = 72 exactly).
* Pros: very common, simple, low cost, easy to wire. ON-resistance and performance similar to HC4067 family (tens of ohms depending on VCC). Good if you prefer fewer channels-per-chip for routing/PCB layout control. ([Nexperia][2])

### 3) **ADG704 (Analog Devices) — 4 × SPST CMOS MUX / low-RON options**

* This family is for when you need **very low on-resistance and low leakage**. ADG704 shows **~2.5 Ω typ RON** and very low power — great for preserving analog accuracy and low noise. You’d need **18 devices** if using 4:1 channels (18×4 = 72). Use this when signal integrity/linearity matters (e.g. small sensor voltages). ([Analog Devices][3])

### 4) **Discrete low-RON analog switches (TS5A3159, etc.)**

* SPDT or dual switches with very low RON (single-digit ohms) — useful if you want best linearity/lowest distortion. These typically increase BOM and PCB routing compared to 16:1 parts. ([Texas Instruments][4])

---

# How to choose (tradeoffs)

* **Channel density vs. signal quality:** 16:1 parts (4067) minimize PCB real estate and MCU IO required but have higher RON (tens of Ω). That’s usually fine if your sensor source impedance is low or the ADC input buffers the signal.
* **Low RON matters** when sensor output is high-impedance or you need very accurate small-voltage readings — choose ADG-series or low-RON switches.
* **Power & leakage:** HC family CMOS parts draw µA static ICC; AD parts often advertise nA–µW standby — useful for battery keyboards. Check datasheets for standby/leakage if battery life is critical. ([Analog Devices][3])
* **Switching speed:** not usually critical for keyboards (kHz or slower), but check tON/tOFF if you plan to multiplex quickly for scanning. ([Analog Devices][3])

---

# Practical recommendation for a magnetic keyboard (72 switches)

* If you want **fewer chips and simpler routing**, go **CD74HC4067 (5 chips)** and feed outputs to your ADC(s). Add a small buffer (op-amp or the ADC’s sample-and-hold input) if sensor impedance is high. ([Texas Instruments][1])
* If your magnetic sensors produce **small, high-impedance analog voltages** and you need best accuracy/noise performance, use **low-RON analog MUXes (ADG704 or similar)** and accept more chips (18 devices). ([Analog Devices][3])

---

# Other tips

* Consider grouping channels to match ADC inputs (e.g., 4× MCP3208 or a single higher-channel ADC).
* Use the MUX enable lines to power down unused banks if you want lower idle current.
* Add small input series resistors or buffering to avoid the MUX’s RON and channel capacitance distorting readings.
* Prototype quickly: try one 4067 on a breadboard to validate signal accuracy before committing to layout.

---

If you want, I can:

* compute **expected total RON + divider error** for your specific sensor source impedance,
* calculate **total static current** for 5×4067 vs 18×ADG704, or
* find **exact part numbers and distributors** with pricing and footprints for your region. Which would you like?

[1]: https://www.ti.com/lit/ds/symlink/cd74hc4067.pdf?utm_source=chatgpt.com "cd74hc4067.pdf"
[2]: https://assets.nexperia.com/documents/data-sheet/74HC_HCT4051.pdf?utm_source=chatgpt.com "74HC4051; 74HCT4051"
[3]: https://www.analog.com/en/products/adg704.html?utm_source=chatgpt.com "ADG704 Datasheet and Product Info"
[4]: https://www.ti.com/lit/gpn/TS5A3159?utm_source=chatgpt.com "TS5A3159 1-Ω SPDT Analog Switch datasheet (Rev. D)"

---
---

Yes — what you’re asking for is basically a **comparator** (or a 1-bit ADC). Instead of a full ADC that returns a multi-bit value, a comparator outputs a **digital 0 or 1** depending on whether the analog input is above or below a set threshold voltage. ([ScienceDirect][1])

Here are some popular comparator ICs (or small modules) that do exactly that — analog input → digital output based on threshold:

## ✅ Example comparator chips/modules

### [LM393 Low Power Dual Comparator](https://kitsguru.com/products/in-line-lm393-17393-low-power-voltage-dual-comparator-dip-8?variant=44661530362108&country=AE&currency=INR&utm_source=chatgpt.com)

#### Dual comparator

*0,24 PLN*

### [LM339 Quad Voltage Comparator IC](https://kitsguru.com/products/ic-gen-pur-comp-quad-1-3-s-dip-14-lm339ng-on-semiconductor?variant=40708906844341&country=AE&currency=INR&utm_source=chatgpt.com)

#### Quad comparator

*0,85 PLN*

### [MCP6541T-E/OT Microchip Ultra‑Low‑Power Comparator](https://www.digikey.pl/pl/products/detail/microchip-technology/MCP6541T-E-OT/1969572?utm_source=chatgpt.com)

#### Ultra‑low power

*1,76 PLN*

### [TLV3501 Ultra‑High Speed Comparator](https://www.ebay.com/itm/194883792726?utm_source=chatgpt.com)

#### High‑speed comparator

*157,11 PLN*

### [LM393D Dual Comparator (STMicroelectronics)](https://estore.st.com/en/lm393d-cpn.html?utm_source=chatgpt.com)

#### Dual comparator

*9,78 PLN*

### [LM2901Q4T CMOS Comparator Pack of 10](https://www.ebay.com/itm/134451534712?utm_source=chatgpt.com)

#### Comparator pack

*21,86 PLN*

### [LM393 Comparator Module High/Low Output](https://www.ebay.com/itm/314183117410?utm_source=chatgpt.com)

#### Comparator module

*9,81 PLN*

### [TSX339 Compact Quad Comparator](https://estore.st.com/en/tsx339iypt-cpn.html?utm_source=chatgpt.com)

#### Quad comparator

*5,84 PLN*

### Quick notes on some:

* **[LM393 Low Power Dual Comparator](https://kitsguru.com/products/in-line-lm393-17393-low-power-voltage-dual-comparator-dip-8?variant=44661530362108&country=AE&currency=INR&utm_source=chatgpt.com)** — a classic, widely used dual comparator. It compares an analog input to a reference (which you set with a resistor divider or a DAC) and outputs a digital signal (HIGH if input > threshold, else LOW). Good for simple threshold-detection on sensor lines, battery voltage monitoring, etc.
* **[LM339 Quad Voltage Comparator IC](https://kitsguru.com/products/ic-gen-pur-comp-quad-1-3-s-dip-14-lm339ng-on-semiconductor?variant=40708906844341&country=AE&currency=INR&utm_source=chatgpt.com)** — offers four comparators in one IC. Useful if you need multiple threshold-detectors in a design.
* **[MCP6541T-E/OT Ultra‑Low‑Power Comparator](https://www.digikey.pl/pl/products/detail/microchip-technology/MCP6541T-E-OT/1969572?utm_source=chatgpt.com)** — if you care about power consumption (battery-powered device), this low-power comparator is a good choice.
* **[TLV3501 Ultra‑High Speed Comparator](https://www.ebay.com/itm/194883792726?utm_source=chatgpt.com)** — suitable when you need fast threshold detection (high-speed analog signals, rapid events).

---

## 🧠 Why comparators are good for “analog → ON/OFF” use-cases

* A comparator is effectively a **1-bit ADC**: it only tells you whether the signal is above or below a threshold. ([ScienceDirect][1])
* You set the threshold either via a fixed resistor divider, a potentiometer, or — in more advanced ICs — an internal/reference input.
* When input crosses threshold, output toggles digital — easy to feed into a microcontroller’s GPIO, interrupt line, or logic gate.

---

## ⚠️ When a full ADC still makes sense

If you need more than “above/below threshold” — e.g. to **measure exact voltage**, **read continuously varying analog sensors**, or **compute value changes over time** — a full ADC (multi-bit) is better. Comparators are ideal for binary decisions (on/off, above/below), not precise measurements.

---

If you like — I can search and list **3–5 modern comparator ICs with digitally programmable thresholds** (so you can change threshold via software or I²C/SPI rather than resistor dividers), which might be especially useful for your keyboard / sensor project.
Do you want me to build that list now?

[1]: https://www.sciencedirect.com/topics/engineering/comparator?utm_source=chatgpt.com "Comparator - an overview | ScienceDirect Topics"


---


Good — there *are* comparator / threshold-detector / “1-bit ADC”-style chips that let you set a threshold (or window) and get a digital output when analog input crosses it. Some are “fixed threshold + external resistors,” others let you adjust thresholds digitally (or with external reference). Below are a few representative ICs / modules.

---

## ✅ Example comparator / threshold-detector ICs & modules

### [LM2903N/P Dual Low‑Power Voltage Comparator](https://kitsguru.com/products/lm2903n-p-dip-8-dual-low-power-voltage-comparator-ic?variant=47395103179004&country=AE&currency=INR&utm_source=chatgpt.com)

#### Low‑power dual comparator

*0,45 PLN*

### [TSX339 Quad CMOS Comparator](https://estore.st.com/en/tsx339iypt-cpn.html?utm_source=chatgpt.com)

#### Quad comparator CMOS

*5,84 PLN*

### [TLV3501 High‑Speed Comparator Module](https://www.ebay.com/itm/388108148153?utm_source=chatgpt.com)

#### High‑speed comparator

*64,74 PLN*

### [TS881ICT Low‑Power Comparator]()

#### Low‑power comparator

*5,29 PLN*

### [Texas Instruments Dual Comparator (Open Collector Output)](https://www.ebay.com/itm/166316056090?var=465944675538&utm_source=chatgpt.com)

#### Dual comparator TTL

*16,24 PLN*

### [Dual Low‑Power Comparator (CMOS/TTL Output)](https://www.electromaker.io/shop/product/lo-pwr-dual-vltg-comparators?utm_source=chatgpt.com)

#### Dual comparator CMOS

*1,93 PLN*

### [ADC 16 Click – ADC with Window Comparator & Programmable Thresholds](https://www.mikroe.com/adc-16-click?utm_source=chatgpt.com)

#### ADC + window comparator

*54,73 PLN*

### [TLV3501 High‑Speed Comparator Module (Alternate Listing)](https://www.elecbee.com/en-32691-TLV3501-High-Speed-Comparator-Frequency-Meter-Front-end-Shaping-Module-4.5ns-High-speed-Comparator?utm_source=chatgpt.com)

#### High‑speed comparator

*61,99 PLN*

### Highlights

* **[LM2903N/P Dual Low‑Power Voltage Comparator](https://kitsguru.com/products/lm2903n-p-dip-8-dual-low-power-voltage-comparator-ic?variant=47395103179004&country=AE&currency=INR&utm_source=chatgpt.com)** — a classic, very low-cost dual comparator. You set the threshold manually (via a resistor divider or reference), and it outputs a digital ON/OFF depending on whether the input is above or below threshold. Good for battery-powered, low-speed tasks.
* **[TSX339 Quad CMOS Comparator](https://estore.st.com/en/tsx339iypt-cpn.html?utm_source=chatgpt.com)** — offers 4 comparators per chip; convenient if you need to monitor multiple analog lines for threshold crossings. CMOS output and low power.
* **[TLV3501 High‑Speed Comparator Module](https://www.ebay.com/itm/388108148153?utm_source=chatgpt.com)** — if you need fast detection (e.g. quick threshold crossing, fast switching), this comparator provides low latency and high speed. Useful if signals change rapidly.
* **[TS881ICT Low‑Power Comparator]()** — another low-power comparator suitable for simple threshold detection with minimal quiescent current.
* **[ADC 16 Click – ADC with Window Comparator & Programmable Thresholds](https://www.mikroe.com/adc-16-click?utm_source=chatgpt.com)** — this is a bit different: it’s a small module that features an ADC + built-in window comparator logic, allowing you to program high and low thresholds, with per-channel interrupt/event logic. This is especially useful if you want to detect “in range / out of range” events without continuously reading raw analog values.
* **Other comparators (like TSX339, TLV3501, generic dual comparators)**: Good building blocks if you want fine control, are comfortable building threshold circuits yourself, and just need “analog in → digital threshold output.”

---

## 🎯 Notes: What these chips *are* (and aren’t)

* These comparator ICs are **not full ADCs** — they don’t measure a voltage value precisely. Instead they give a **binary output**: on/off (above/below threshold). That’s exactly what you asked for.
* For many, the threshold is set by external resistors or a reference voltage. In modules like “ADC 16 Click,” the threshold (or window) is **programmatically configurable** (so you can change it via I²C or register write).
* You won’t get an exact numeric value — but if all you need is “is the analog signal > X?” or “has it crossed threshold?”, these are efficient and low-power.
* Comparators (and window comparators) are very power-efficient compared to doing full ADC conversions continuously — useful in battery-powered or always-on devices. ([ic-online.com][1])

---

## ✅ My recommendation for a keyboard / sensor matrix use-case

If I were you and I just want to detect “magnet present / magnet absent” (or “sensor above / below threshold”) for ~70+ inputs:

* I’d go with a **comparator / window-comparator solution** — lower overhead than a multi-channel ADC + MUX + software.
* A module like **ADC 16 Click** (with programmable threshold + interrupt logic) is especially attractive: you can tune threshold in firmware (rather than messing with resistor dividers), and get digital signals — simplifies wiring and coding.
* If I want minimal cost + minimal power + simple threshold detection, I’d pick **LM2903** or **TSX339** (or similar). These are cheap, easy to wire, and widely available.

---

If you like — I can **pull up 5–10 comparator / comparator-module ICs** available from **European distributors** (e.g. DigiKey EU, Mouser Germany, TME Poland) — that might make procurement easier for you. Do you want me to build that “ready-to-order” list now?

[1]: https://ic-online.com/news/post/comparator-integrated-circuits-essential-components-for-signal-processing-and-threshold-detection?utm_source=chatgpt.com "Comparator Integrated Circuits: Essential Components for Signal Processing and Threshold Detection"
