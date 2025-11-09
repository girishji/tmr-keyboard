# Calculations and TMR Sensor Concepts

---

## 🧭 Convert TMR Sensor Sensitivity to Gauss Units

**Q:** convert 22.5 mV/V/mT sensitivity of a TMR sensor to units of Gauss (instead of mT)

**Answer:**

Let's carefully go step–by–step.

### Given:

TMR sensor sensitivity = **22.5 mV/V/mT**

You want the sensitivity in **mV/V/Gauss**.

---

### Step 1. Recall the conversion between milliTesla (mT) and Gauss (G):

$$1~\text{T} = 10{,}000~\text{G}$$

$$1~\text{mT} = \frac{10{,}000~\text{G}}{1000} = 10~\text{G}$$

So:

$$1~\text{mT} = 10~\text{G}$$

---

### Step 2. Convert the sensitivity

Given:
$$22.5~\frac{\text{mV}}{\text{V}\cdot\text{mT}}$$

Since $(1~\text{mT} = 10~\text{G})$,

$$22.5~\frac{\text{mV}}{\text{V}\cdot\text{mT}} = \frac{22.5}{10}~\frac{\text{mV}}{\text{V}\cdot\text{G}}$$

---

### Step 3. Compute the numeric value

$$\frac{22.5}{10} = 2.25$$

---

✅ **Final Answer:**

$$\boxed{2.25~\text{mV/V/Gauss}}$$

**Interpretation:**
Your TMR sensor’s sensitivity is **2.25 mV per volt of excitation per Gauss**.

---

## ❓ What is 'Offset Voltage' in a TMR Sensor

**Q:** what is 'offset voltage' in a TMR sensor

**Answer:**

Great question — this is a key concept when working with **TMR (Tunneling Magnetoresistance)** sensors.

### ⚙️ **Definition**

**Offset voltage** in a TMR sensor is the **output voltage when no magnetic field is applied** (i.e., at 0 mT or 0 G).

Ideally, the sensor’s output should be exactly half of the supply voltage (for a Wheatstone-bridge type TMR) or **0 V differential** (for a perfectly balanced bridge).
However, in reality, **manufacturing tolerances**, **material asymmetries**, and **stress or temperature effects** cause a small nonzero output even when the magnetic field is zero.
That nonzero output is called the **offset voltage** (also known as **residual voltage** or **zero-field offset**).

---

### 📈 **In Formula Form**

If:
$$V_\text{out} = S \cdot B + V_\text{offset}$$

Where:

* $V_\text{out}$ = measured output voltage (mV/V),
* $S$ = sensitivity (e.g., 22.5 mV/V/mT),
* $B$ = applied magnetic field (mT or Gauss),
* $V_\text{offset}$ = output voltage at $B = 0$.

---

### 📊 **Typical Characteristics**

* Expressed in **mV/V** (output per supply voltage) or as an absolute voltage (e.g., ±10 mV).
* Often a small percentage of full-scale output.
* Can **drift** with **temperature** or **time**.
* May be **trimmed**, **calibrated out**, or **digitally compensated**.

---

### 🔧 **Example**

If a TMR sensor has:

* Sensitivity = 22.5 mV/V/mT
* Supply = 5 V
* Offset = +1 mV/V

Then at 0 mT:
$$V_\text{out} = 1~\text{mV/V} \times 5~\text{V} = 5~\text{mV}$$

Even with **no field**, you’ll see a **5 mV output** — that’s the offset voltage.

---

## ⌨️ Suitable Sensitivity for a TMR Switch in a Keyboard Application

**Q:** for keyboard switch application what is a suitable sensitivity for a TMR switch

**Answer:**

Nice — that surface spec is exactly the kind of starting point we need. I’ll assume **“75 Gs at 0 distance (N-pole)”** means the magnet’s pole-face field (surface field) is ~**75 Gauss**. Because you didn’t give magnet dimensions or the gap to the sensor, I’ll make a conservative, useful approximation and show what the field and expected sensor voltage look like for a couple of typical magnet sizes and gaps — that will let you pick a suitable TMR switch / sensitivity.

---

### Key assumptions & method

* **$B_\text{surface} = 75 \text{ G}$** at the pole face ($z = 0 \text{ mm}$).
* Magnetic field along the axis decays roughly like a dipole for distances larger than the magnet thickness. I use a simple axial decay model:
  $$B(z) \approx B_{0}\left(\frac{d_0}{d_0+z}\right)^3$$
  where $d_0$ is a characteristic size (approx. the magnet radius / effective pole distance). This is an approximation — real magnets deviate, but it’s good for order-of-magnitude estimates.
* I compute two representative **$d_0$** values:

  * **$d_0 = 2 \text{ mm}$** (small pellet / tiny magnet)
  * **$d_0 = 5 \text{ mm}$** (larger button / disk)
* For analog-sensor voltage estimates I use the sensitivity you mentioned earlier converted to Gauss: **$2.25 \text{ mV/V/G}$**, and **$V_{cc} = 3.3 \text{ V}$**. So per-Gauss output $\approx$ **$7.425 \text{ mV/G}$** $(2.25 \times 3.3)$.

---

### Estimated axial field vs gap (Gauss)

| gap $z \text{ (mm)}$ | $B \text{ (G)}, d_0=2 \text{ mm}$ | $B \text{ (G)}, d_0=5 \text{ mm}$ |
| -------------------: | ---------------------------------: | ---------------------------------: |
|          0 (surface) |                             75.0 |                             75.0 |
|               1 mm |                            22.22 |                            43.40 |
|               2 mm |                             9.38 |                            27.33 |
|               3 mm |                             4.80 |                            18.31 |
|               5 mm |                             1.75 |                             9.38 |
|              10 mm |                             0.35 |                             2.78 |

*(These are approximate; actual values depend strongly on magnet geometry and alignment.)*

---

### Expected analog voltage change (3.3 V supply, 2.25 mV/V/G)

Voltage change = $(2.25 \text{ mV/V/G}) \times 3.3 \text{ V} \times B(\text{G}) \rightarrow \text{shown in volts:}$

| gap $z \text{ (mm)}$ | $\Delta V, d_0=2 \text{ mm (V)}$ | $\Delta V, d_0=5 \text{ mm (V)}$ |
| -------------------: | -------------------------------: | -------------------------------: |
|                    0 |                         0.5569 V |                         0.5569 V |
|                 1 mm |                         0.1650 V |                         0.3223 V |
|                 2 mm |                         0.0696 V |                         0.2029 V |
|                 3 mm |                         0.0356 V |                         0.1360 V |
|                 5 mm |                         0.0130 V |                         0.0696 V |
|                10 mm |                         0.0026 V |                         0.0206 V |

So, for example, if your magnet is small ($d_0 \approx 2 \text{ mm}$) and the sensor sits **$2 \text{ mm}$** away you’d see $\approx$$\mathbf{9.4 \text{ G}} \rightarrow \approx$$\mathbf{70 \text{ mV}}$ change at 3.3 V. At **$3 \text{ mm}$** that drops to $\sim$$4.8 \text{ G} \rightarrow \sim 36 \text{ mV}$.

---

### What this means for a keyboard switch

* **Typical target $B_\text{op}$** for magnetic keyboard switches: **$\sim 5–10 \text{ G}$** (as I recommended earlier).
* From the table:

  * If your magnet is small ($d_0 \approx 2 \text{ mm}$), you’ll likely need the sensor $\sim$$\mathbf{2–3 \text{ mm}}$ from the magnet at actuation to be in the $5–10 \text{ G}$ window.
  * If the magnet is larger ($d_0 \approx 5 \text{ mm}$), the same $5–10 \text{ G}$ occurs further away ($3–5 \text{ mm}$).
* If you use an **analog TMR** with $\sim$$2.25 \text{ mV/V/G}$ and $3.3 \text{ V}$ supply, expect **$\sim 35–75 \text{ mV}$** of signal at the actuation point for $B = 4.8–10 \text{ G}$ — easily measurable by a 12-bit ADC ($\text{LSB} \approx 0.8 \text{ mV}$) and gives comfortable margin above typical noise/offset.
* If you prefer **plug-and-play**, pick a **digital TMR switch** ($B_\text{op} \sim 5–10 \text{ G}$, omnipolar if magnet orientation varies). That offloads hysteresis/debounce to the chip.

---

### Practical recommendations (pick one)

1. **No fuss (recommended):** Use a digital TMR switch IC with **$B_\text{op} = 5–10 \text{ G}$** (omnipolar if needed). Ensures stable switching and built-in hysteresis.
2. **Firmware-tunable:** Use an analog TMR/Hall with **$\sim 2–5 \text{ mV/V/G}$** sensitivity, $3.3 \text{ V}$ supply, and implement threshold/hysteresis in firmware. Aim for $\ge$$20–30 \text{ mV}$ signal at actuation for robust detection.
3. **If you want to optimize:** measure the actual field at the sensor position (a Gaussmeter or a cheap Hall probe) — that will beat any model. Small mechanical offsets and magnet tolerances can change fields a lot.

---

### Caveats & next steps

* My numbers are **estimates** based on a simple decay law. Real magnets + housings + ferrous parts will change the field.
* If you tell me (or measure) the magnet diameter/thickness and the intended sensor-to-magnet gap at rest and at actuation, I can convert that to a more concrete $B$ value and the expected voltage swing for your chosen $V_{CC}$ and sensitivity — then pick a specific TMR part or ADC resolution to match.

---

## ⚖️ Interpreting Offset Voltage of 300–700 mV/V

**Q:** in this context, what does 'offset voltage' of 300-700 mv/V mean. Which is better for keyboard switch

**Answer:**

Excellent question — this goes right to **how you interpret the “offset voltage” spec** for a TMR sensor **and how it affects switch design** (keyboard or otherwise).

Let’s unpack it clearly:

---

### 🧭 What "offset voltage" = 300–700 mV/V means

That number is **the zero-field output**, *normalized to the supply voltage.*

So:

* **$300–700 \text{ mV/V}$** means **when no magnetic field is applied**, the sensor outputs between
  $(0.3 \times V_{CC})$ and $(0.7 \times V_{CC})$.

If $(V_{CC} = 3.3 \text{ V})$:

* Offset = $0.3 \times 3.3 \text{ V} \rightarrow 0.99 \text{ V}$
  to
  $0.7 \times 3.3 \text{ V} \rightarrow 2.31 \text{ V}$
  $\rightarrow$ the zero-field output will be somewhere in that range.

This is typical of **ratiometric analog magnetic sensors**, where the output sits near mid-supply at zero field and moves up/down symmetrically with positive/negative magnetic fields.

---

### ⚖️ Why there’s a range (300–700 mV/V)

That **$\pm 20\%$ tolerance** exists because:

* Each sensor has small mismatches in its bridge resistances.
* It drifts slightly with temperature and mechanical stress.

So one chip might idle at $1.0 \text{ V}$, another at $2.2 \text{ V}$ — both “normal.”

---

### 🧮 Example in numbers

You said your sensor has a **sensitivity of $22.5 \text{ mV/V/mT}$} = **$2.25 \text{ mV/V/G}$**.

At $3.3 \text{ V}$:

* Sensitivity = $2.25 \times 3.3 = 7.425 \text{ mV/G}$.

Let’s say the offset is $0.5 \text{ V/V} \rightarrow 0.5 \times 3.3 = 1.65 \text{ V}$ baseline.
At a $+5 \text{ G}$ field, output = $1.65 \text{ V} + (7.425 \text{ mV/G} \times 5 \text{ G}) = \mathbf{1.687 \text{ V}}$.
At $-5 \text{ G}$, output = $1.613 \text{ V}$.
So you get a $\pm 37 \text{ mV}$ swing around $1.65 \text{ V}$.

---

### 💡 Which offset is *better* for a keyboard switch?

It depends on **your signal processing**:

#### 🧩 Case 1: **Digital comparator or MCU ADC (single-ended)**

* You’ll typically compare the sensor voltage against a **threshold** (or mid-supply reference).
* It’s easiest if the **zero-field offset** is **near mid-supply** — $\sim 0.5 \text{ V/V} (\approx 1.65 \text{ V for } 3.3 \text{ V})$.
* That gives maximum headroom for positive and negative swings.
  ✅ **Best offset:** around **$0.5 \text{ V/V}$**.

#### 🧩 Case 2: **Differential bridge / instrumentation amplifier**

* Offset can be digitally subtracted or hardware-trimmed, so it doesn’t matter much.
* In this case, stability (low drift) matters more than the absolute value.

---

### 🧘‍♂️ Practical takeaway for a keyboard switch

| Spec                                         | Good for keyboard?      | Why                                                      |
| -------------------------------------------- | ----------------------- | -------------------------------------------------------- |
| **Offset $\sim 0.5 \text{ V/V}$ (mid-supply)** | ✅ Excellent             | Gives symmetric range up/down for both magnet polarities |
| **Offset far from mid ($0.3 \text{ V/V}$ or $0.7 \text{ V/V}$)** | ⚠️ Usable but not ideal | Reduces available swing before clipping                  |
| **Offset drift (vs temperature)** | Important!              | Causes key threshold drift if not compensated            |

So — when comparing parts:

> Choose a TMR sensor with **offset near $0.5 \text{ V/V}$** and **good thermal stability**, rather than focusing only on absolute offset magnitude.
