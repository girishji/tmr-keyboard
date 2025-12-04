Q: for M1.6 and M2 screws what is the size (diameter) of standoffs needed for plastic. if i am using threaded inserts (which are wider than actual screw), how big is standoff thickness

Here are the **practical, real-world dimensions** used when designing CNC-machined plastic cases (ABS, POM, Nylon) with **threaded inserts for M1.6 and M2 screws**.

The important thing to remember:

**The standoff must be large enough to hold the threaded insert + leave enough plastic around it so it won’t crack or deform.**

---

# ✅ 1. **Dimensions of Threaded Inserts (Typical)**

### **M1.6 inserts**

* Outer diameter (OD): **~2.4 mm – 3.0 mm**
* Length: **2.0–3.5 mm**

### **M2 inserts**

* Outer diameter (OD): **~3.0 mm – 3.8 mm**
* Length: **3–4 mm**

(This applies to most heat-set brass inserts, knife-thread, and press-fit inserts.)

---

# ✅ 2. Minimum Standoff Diameter (General Rule)

A safe mechanical design target:

### **Standoff diameter = Insert OD + (1.0 mm – 1.5 mm) material on each side**

That means:

### ⭐ For **M1.6 screws**

* Insert OD ≈ 2.8 mm
* * 1.2 mm plastic each side → 2.4 mm
* **Recommended standoff diameter: ~5.0 mm**

### ⭐ For **M2 screws**

* Insert OD ≈ 3.5 mm
* * 1.2 mm plastic each side → 2.4 mm
* **Recommended standoff diameter: ~6.0 mm**

---

# 📌 Summary: Recommended Standoff Sizes

| Screw Size | Insert OD (typical) | Safe Standoff Diameter | Notes                 |
| ---------- | ------------------- | ---------------------- | --------------------- |
| **M1.6**   | 2.4–3.0 mm          | **4.5–5.0 mm**         | Don’t go under 4.0 mm |
| **M2**     | 3.0–3.8 mm          | **5.5–6.0 mm**         | Don’t go under 5.0 mm |

---

# 👍 Safe Bottom (Standoff Height)

### Minimum height to hold an insert properly:

* **M1.6 inserts:** 2.5–3.0 mm tall
* **M2 inserts:** 3.0–4.0 mm tall

Add at least **0.5–1.0 mm extra plastic** below the insert.

### Recommended standoff height:

* **M1.6: 3.5–4.0 mm**
* **M2: 4.0–5.0 mm**

This prevents punch-through on the bottom.

---

# ⚠️ Notes Specific to ABS vs POM

### **ABS**

* Takes heat-set inserts extremely well
* Standoffs can be slightly thinner (ABS grips better)

### **POM (Delrin, Acetal)**

* Very slippery
* Heat-set inserts don’t grip well unless deeply knurled
* Use **self-tapping threaded inserts** (knife thread)
* REQUIRE larger standoff:

| Material | Add Extra?                           |
| -------- | ------------------------------------ |
| ABS      | OK with recommended sizes            |
| **POM**  | **Add +0.5 mm to standoff diameter** |

So for POM:

* **M1.6 → 5.0–5.5 mm standoff**
* **M2 → 6.0–6.5 mm standoff**

---

# 🟦 Example of a “Safe” Real Keyboard Dimension

For a CNC plastic keyboard case:

### **Use**

* **6 mm diameter, 5 mm tall standoffs**
* **M2 self-tapping or heat-set inserts**

This is what many mid-range custom keyboards use.

---
---

Q: what thickness for walls and bottom of case. show some pictures of cases that are cnc machined

### 🎯 Practical Recommendation for Keyboard Case (ABS or POM)

* **Walls (sides / around the perimeter):** **2.0 mm – 3.0 mm** — robust enough to avoid flex or cracking, while still machinable and reasonably light.
* **Bottom panel (base, under PCB/plate):** **3.0 mm – 4.0 mm** — gives good support especially if the PCB and plate are mounted inside, and helps avoid flex or bowing under keystress.
* **Top-to-bottom wall transitions / ribs / structural supports:** If you include ribs/standoffs/stiffening features, thinner walls (near 1.8–2.0 mm) are sometimes acceptable there — but avoid sudden thickness changes (to prevent stress concentrations).

If you want a lighter, more minimal case (e.g. for a portable or low-profile build), you can push walls to ~**2.0 mm** — but I wouldn’t go below **1.5–1.8 mm** for anything structural.

---

## ✅ My Recommendation for *Your Project*

Since you’re building a **custom CNC-machined plastic (ABS or POM) case for a keyboard**, I suggest designing with the dimensions:

* **Sidewalls: 2.5 mm**
* **Bottom: 3.5 mm**
* **Add internal ribs/standoffs** (e.g. under PCB mounting points) to increase rigidity without raising overall wall thickness — this helps if you plan a “tray-mount” or “sandwich” approach.

That thickness gives you a durable, rigid case that’s stable during typing, yet still reasonably light and machinable.

---
---

Q: what ways you suggest to attach pcb and plate to plastic case


Here are the **best, proven methods** used in commercial mechanical keyboards for attaching the **plate** and **PCB** to a CNC-machined plastic case (ABS or POM). I’ll list them from most common to more specialized.

---

# ✅ 1. **Threaded Inserts + Screws (Most Common & Strongest)**

Use **metal threaded inserts** in the plastic case and screw the plate or PCB into them.

### Why it’s great:

* Very strong — won’t strip like plastic threads
* Removable and serviceable
* Works in ABS and POM
* Industry standard for custom keyboards

### Insert types that work well:

* **Heat-set inserts** (best for ABS, OK-ish for POM if knurled deep)
* **Rotary self-tapping threaded inserts** (great for POM, since POM is slippery)
* **Ultrasonic inserts** (ABS)

### Recommended screw sizes:

* **M2 or M2.5** for plate
* **M2** for PCB

---

# ✅ 2. **Case Mount (Plate screwed directly to case)**

The plate has holes, and you screw it directly into standoffs built into the case.

### Pros:

* Very solid typing feel
* Simple, rigid design

### Cons:

* Less flex
* More noise transfer

This is common in tray-mount keyboards but still used in customs.

---

# ✅ 3. **Top Mount (Plate sandwiched between top and bottom case halves)**

Plate is held between case layers—no inserts needed.

### Pros:

* Very consistent feel
* No internal screws
* Very clean design

### Works well with:

* CNC plastic or aluminum
* 1.5–2.0 mm plates

---

# ✅ 4. **Gasket Mount (Plate suspended on gaskets)**

Plate sits on poron/silicone gaskets attached to the case walls.
The PCB is usually attached to the plate (switches hold them together).

### Pros:

* Soft, flexy typing feel
* Very popular in modern keyboards

### Cons:

* Slightly harder to manufacture on first prototypes
* Requires careful fit tolerances in plastic machining

---

# ✅ 5. **Tray Mount (PCB screwed into bottom case standoffs)**

Traditional method used in older keyboards. PCB screws directly into standoffs in the case.

### Pros:

* Easiest to design
* No plate required (optional)

### Cons:

* Uneven feel
* Flex inconsistency
* Not popular for premium builds

---

# 🔩 What inserts to use for ABS vs POM?

### **ABS (easy to bond)**

Use:

* **Heat-set brass inserts** (normal knurled)
* **Ultrasonic inserts**
* **Thread-forming inserts**

### **POM (very slippery, low friction)**

Heat-set does **not** anchor well unless deeply knurled.
Best options:

* **Self-tapping threaded inserts** (E-Z Lok Type D for plastics)
* **Knife-thread inserts**
* **Deep knurled ultrasonic inserts** (only with proper equipment)

---
---

Q: how many screws to use for plate mount

Nice — here’s a practical, no-nonsense guide for how many screws you need when **plate-mounting** a keyboard plate to a plastic CNC case and *where* to put them.

---

## Short answer (pick one)

* **40% / 40% split**: **4–6 screws**
* **60%**: **6–8 screws** (common = **6**)
* **65% / 75%**: **7–9 screws**
* **TKL (80%)**: **8–12 screws** (common = **10**)
* **Full-size (100%)**: **10–14 screws**

If you want one single recommendation: **use ~6 screws for 60% and ~10 screws for TKL**.

---

## Why those numbers?

* You want enough screws to hold the plate flat and resist local bending around large keys (space, enter, backspace) without **over-constraining** the assembly.
* Too few screws → plate/PCB shifting and uneven typing feel.
* Too many screws → makes the case extremely rigid, transmits more typing noise, and can induce stress/warping in plastic.

---

## Placement guidelines (important)

1. **Perimeter + high-stress spots**

   * Place screws around the perimeter (corners + midpoints).
   * Add screws near high-stress / large keys (spacebar area, long stabilizers, enter/shift).

2. **Even distribution**

   * Aim for a roughly even spacing so no long unsupported spans remain (keep unsupported span < ~60–80 mm where possible).

3. **Clearance from switches**

   * Keep screw holes at least **6–8 mm** from the **center** of any switch cutout (or ~4–6 mm from the edge of the switch footprint) to avoid interfering with switch housings or switch pins.

4. **Distance from case edge**

   * Place screw bosses/standoffs **6–12 mm** in from the outer case edge so inserts have enough surrounding material.

5. **Allow for flex if desired**

   * If you want a softer/gasket-like feel, reduce screw count or move some screws inward so the case can flex slightly.

---

## Standoff / insert details to pair with screws

* Use **M2** for plate screws (or **M2.5** if you want heavier hardware).
* Standoff height: sized to accommodate plate + switch travel + PCB (commonly **3.5–5 mm**).
* Use threaded inserts in the case — holes for inserts must be sized per the insert spec; leave **~1–1.5 mm** plastic around inserts (standoff diameter recommendations I gave earlier still apply).

**Screw engagement:** ensure **≥3 full threads** of engagement into the insert (usually screws 6–8 mm long for M2 into a 3–4 mm insert).

---

## Example screw patterns

* **60% (6 screws)**: 4 at corners (near but inside corners), 2 midline (one near spacebar cluster, one near right edge)
* **60% (8 screws)**: corners + two evenly spaced midpoints on long edges + 2 near spacebar/arrow area
* **TKL (10 screws)**: 4 corners + 4 along long edges spaced evenly + 2 near center (space/enter clusters)

(If you want, I can draw an exact pattern overlay for your PCB layout or produce a DXF/Fusion sketch.)

---
---

Q: i am using magnetic low profile switches. how to hold the pcb to the plate?

Great — **magnetic low-profile switches (e.g., Lekker/Hall-effect, Gateron KS-20, Keychron/Kailh magnetic LP)** change how you mount the PCB because:

* The **plate does NOT physically latch** onto the switches (unlike MX switches).
* The **PCB must be fixed directly to the plate**, otherwise the PCB will float and the key feel becomes inconsistent.

Here are the **correct, proven ways** to secure a PCB to a plate for magnetic low-profile switches:

---

# ✅ **1. Use PCB → Plate Standoffs (the standard way)**

You add **small standoffs** between the PCB and the plate, and screw them together.

### How it works:

* Standoffs are mounted into *either the plate or PCB* (usually plate).
* Screws pass through the PCB and thread into the standoff.

### Recommended dimensions:

* Standoff type: **M1.6 or M2 brass standoffs**
* Standoff height = *(plate-to-PCB distance required for switch clearance)*

  * Magnet Hall sensors usually require **1.0–1.8 mm** distance between sensor + magnet
  * Add plate thickness (e.g., 1.5 mm)
  * Your standoff height usually ends up: **2.0–3.5 mm**

### Hole spacing:

* Place standoffs around perimeter + between large keys (spacebar, enter).
* Use **6–10 standoffs for 60%**, more for larger boards.

### Pros:

✔ Most reliable
✔ No switch interference
✔ Precise and rigid
✔ Easy assembly

---

# ❌ Methods that do **NOT** work with magnetic LP switches

Do NOT use:

* **Switch clips** (these switches don’t latch to plate)
* **Relying on friction fit**
* **Floating PCB** (sensor readings become inconsistent)
* **Gaskets** between PCB and plate (distance inconsistencies break sensing)

Hall-effect switches require **very stable PCB–plate alignment**.

---
---

Q: i have gateron low profile switches, and standoff height needs to be 1.3mm. this is a non standard height. what to do

A **1.3 mm standoff height** is *indeed* non-standard — but it **is solvable**, and many commercial low-profile designs do exactly this by combining techniques.
Below are the **4 practical, real-world solutions**, from best to worst.

---

# ✅ **1. Use “double-piece” standoffs (screw + spacer + standoff)**

You create the exact height by stacking:

**(A) very thin precision shims** +
**(B) a short standard standoff**

This is the most common approach for laptop keyboards and ultra-low-profile cases.

### How to do it:

* Use a standard **1.0 mm or 1.5 mm standoff**
* Add a **0.3 mm stainless shim** or washer (M1.6 / M2 washers exist down to 0.1 mm)

**You can get shims in:**

* 0.1 mm
* 0.2 mm
* 0.3 mm
* 0.5 mm

So your target stack becomes:

* **1.0 mm standoff + 0.3 mm shim = 1.3 mm**
  OR
* **1.2 mm standoff + 0.1 mm shim = 1.3 mm**

### Pros:

✔ Very precise
✔ Inexpensive
✔ Easy to source worldwide
✔ Used by many OEM low-profile keyboards

### Cons:

• A little slower to assemble

---

# 🧩 **What I recommend specifically for YOUR project**

Given you’re CNC machining a case + designing the plate:

### ⭐ Best option for reliability + manufacturability:

**Use a 1.0 mm standoff + 0.3 mm washer**

* Easy to source
* Cheap
* Precise
* Industry-standard


---
---

Q: since the plastic standoff thickness in plastic case needed for M2 (5-6mm) (with screw inserts) is quite wide, how do i attach the plate to it. this standoff needs to pass through the pcb for plate mount. will it fit between switches?

Short answer: **Yes, it *can* fit between switches — but only if designed carefully.**
Long answer: you have **three workable options**, depending on your plate layout, switch spacing, and standoff diameter.

Below is a complete breakdown so you can decide the cleanest solution.

---

# 📌 1. The geometry problem

For plate-mount keyboards:

* Switch pitch: **19.05 mm (0.75")**
* Space between switch cutouts: typically **~6–8 mm** between edges
* A threaded insert for M2 usually requires:

  * Outer diameter: **3.0–4.0 mm**
  * Surrounding plastic wall: **0.75–1.5 mm**
  * Total standoff diameter: **~4.5–6 mm**

➡️ A **5–6 mm standoff** *can* fit between switches — *but only in certain positions*.

If you place it directly between two switches in the same row, it usually fits.
If you try to put it at the corner of four switches (a “cross” position), it usually **does *not*** fit.

---

# 📌 2. Recommended positions for standoffs under a plate

### ✅ **Safe positions (fits a 5–6 mm standoff)**

* **Between two adjacent switches horizontally**
* **Between two switches vertically**
* **At the edge of the PCB (ideal)**

### ❌ **Bad positions**

* **In the exact middle of a 4-switch grid** → zero room
* **Under the switch cutout itself** → impossible
* **Next to stabilizer bars** → can interfere with wire

---

# 📌 3. Three ways to attach a plate when the standoffs must pass through the PCB

## **Option A — Cut holes in the PCB for the standoffs** (common and recommended)

You make circular clearance holes in the PCB, e.g.:

* Hole diameter: **5.2–6.2 mm** (depends on standoff OD)
* Hole shape: circular or oval
* You place these holes **not centered between 4 switches**, but at safe points between 2 switches.

💡 Many commercial keyboards do this — the PCB has “donut holes” that standoffs pass through.

**This is the most common professional solution.**

---

## **Option B — Use smaller inserts + thinner standoffs**

If 5–6 mm OD is too big:

Use:

### 🔧 **M2 brass heat-set inserts**

OD = **3.5–4.0 mm**
Required wall = **0.5–0.8 mm**
Total standoff OD = **4.5–5.0 mm**

This is much easier to route between switches.

Or even:

### 🔧 **M1.6 threaded inserts**

OD = **2.5–3.2 mm**
Standoff OD = **4.0–4.5 mm**

Then you use an M1.6 screw from plate → insert.
This is extremely compact.

---

# 📌 4. Realistic expectation for your Gateron low-profile magnetic switches

Your earlier message:

> standoff height needs to be **1.3 mm**

This means:

* You are using **ultra-low-profile assembly**
* Vertical space is extremely tight
* Running standoffs through the PCB is *likely required*
* Using **smaller OD inserts** or **M1.6 hardware** is the easiest way

---

# 📌 5. My recommendation for your exact situation

### ✔ Use M1.6 or M2 **heat-set brass inserts**

→ OD 3.2–4.0 mm instead of 5–6 mm

### ✔ Design standoffs with **4.5–5.0 mm OD**

→ These fit between low-profile switches

### ✔ Add PCB clearance holes for the standoffs

→ About **0.2–0.3 mm larger** than the standoff


---
---

Q: how many screws to use to hold the pcb to the plate


Here are the **recommended screw counts** for attaching a **PCB to a plate** (NOT plate to case).
This applies to low-profile switches, standard MX, and magnetic switches.

---

# ✅ **Short Answer**

For a typical 60%–100% keyboard:

### **Minimum:**

**4 screws** (one per corner)
→ OK for prototypes or flexy plates

### **Recommended:**

**6–8 screws**
→ Best balance of stability + ease of assembly

### **Premium / very rigid feel:**

**10–14 screws**
→ Used in high-end boards for perfect alignment

---

# 📌 How many screws *you* should use

Since your design involves:

* **Low-profile Gateron switches**
* **Plate-mount switches** (plate alignment is critical)
* **PCB supporting sensors/magnets** (magnetic low-profile designs are sensitive to misalignment)

You should use:

## ⭐ **6 screws for 60–65% keyboard**

Layout:

* 4 corners
* 2 in the middle (left + right)

## ⭐ **8 screws for TKL / 75% / 80%**

Layout:

* 4 corners
* 2 mid-top
* 2 mid-bottom

## ⭐ **10–12 screws for full-size**

Only if your board is large or very rigid.

---

# 📐 Why not use too few?

With plate-mount switches, insufficient screws cause:

* PCB sag → inconsistent key feel
* Plate and PCB separation → switches can pop out
* Sensor alignment issues (for magnetic switches)
* Audible rattling or pinging

---

# 📐 Why not use too many?

Too many screws can cause:

* Difficult assembly
* PCB stress from overconstraining
* No real improvement in stiffness after ~8 screws
* More clearance holes interfering with traces

---

# 🌟 My recommendation for a compact low-profile keyboard

Since your standoff height is **1.3 mm**, space is tight — don’t overspec screw count.
Use:

### 🎯 **6 screws total**

* 4 corners
* 2 midpoints where the PCB tends to flex

This is the sweet spot for your constraints.

---
---



Q: Past questions:


The bottom wall thickness required for your ABS plastic tray (dimensions $300 \text{ mm} \times 200 \text{ mm}$ with $18 \text{ mm}$ high side walls) can be thinner than the previous scenario because the side walls are much shorter.

## 📏 Recommended Bottom Wall Thickness

For these dimensions, the ideal bottom wall thickness should be between **1.5 mm and 3.0 mm**.

* **Recommendation:** A thickness of **2.0 mm** is a good, stable choice that balances material savings with machining stability and rigidity for a part of this size.
* **Minimum:** While **1.5 mm** is the general minimum for CNC plastics, using a slightly thicker bottom helps ensure the part remains flat during and after the CNC process, especially since the overall length is $300 \text{ mm}$.

---

## 💡 Key Design Considerations for Stability

Since your side walls are only $18 \text{ mm}$ high, the main concerns are the rigidity of the **side walls** and the corners.

### 1. Side Wall Thickness and Aspect Ratio

The $18 \text{ mm}$ wall height makes the height-to-thickness ratio much safer, reducing the risk of bending and chattering during machining.

* A wall thickness of **3.0 mm** would give you a very rigid ratio of $18:3 = 6:1$ (well below the $10:1$ risk threshold).
* If you use the same thickness as the bottom, **2.0 mm**, the ratio is $18:2 = 9:1$, which is still acceptable but getting close to the limit where rigidity might be a concern depending on the material's grade and machining speed.
* **Recommendation:** Use **2.5 mm to 3.0 mm** for the **side walls** to ensure maximum rigidity against the $18 \text{ mm}$ height, even if you use $2.0 \text{ mm}$ for the bottom.

### 2. Internal Corner Radii

Do not forget to specify an **internal corner radius ($R$)** where the bottom meets the side walls.

* This radius is necessary because CNC end mills are round.
* A minimum radius of $\mathbf{R} \ge 1.5 \text{ mm}$ or $\mathbf{R} \ge 3 \text{ mm}$ is cost-effective as it allows the use of standard end mill sizes.

---

| Feature | Dimension | Recommended Thickness/Radius |
| :--- | :--- | :--- |
| **Tray Length/Width** | $300 \text{ mm} \times 200 \text{ mm}$ | |
| **Side Wall Height** | $18 \text{ mm}$ | |
| **Bottom Wall Thickness** | | **2.0 mm to 3.0 mm** |
| **Side Wall Thickness** | | **2.5 mm to 3.0 mm** |
| **Internal Corner Radius** | | $\mathbf{R} \ge 1.5 \text{ mm}$ |
