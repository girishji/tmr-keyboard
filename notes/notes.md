
With low depth activation of key there will be less spurious key presses since
springs are light

----------------------------------------------------------------------
todo:

- left top key is 1u
- remove wall from left top and 2 keys on right top
- fn key can be 1.25u
- two holes in the front -- a pcb with standoffs to act as stopper (sometimes
  25mm is ok, sometimes (at night where knuckes obstruct screen) 30mm is
  needed, this is distance from the top of key)
- bottom depression may not be necessary (over engineering), just use a thin
  rubber tape if needed

----------------------------------------------------------------------

https://www.waveshare.com/wiki/RP2040-Tiny

https://jlccnc.com/help/article/CNC-Machining-Design-Guideline

----------------------------------------------------------------------

https://www.youtube.com/watch?v=wz2ZO3kSfNE

omnipolar response: sensor responds to N or S pole with equally magnitude.

You can use unipolar sensor, in which case offset is not necessary.

https://www.youtube.com/watch?v=Laexij_rioU

Pay attention to frequency. The smaller it is the better the power
consumption, but lower the sensitivity. He quoted 330k Hz as max (3us).

https://www.youtube.com/watch?v=vwzUx7oq-f0

analog vs digital sensors

------------------------------------------------------------------------


 7G = 0.7mT

------------------------------------------------------------------------

We show how a new tunneling magnetoresistance sensor can be used for perpendicular proximity sensing such as a keyboard switch.

Most keyboard switches are designed for Hall effect sensors, where the magnetic field is perpendicular to the sensor. But TMR sensors are preferred because of their precision.

Unlike Hall effect, TMR sensors are sensitive in the plane of the package. But with the small size and spacial precision of NVE sensors, we can use an off-axis perpendicular orientation. There's plenty of signal with no amplification. In this configuration the output is linear with distance over the four millimeter switch travel, rather than dropping off with the square of the distance in an in-plane configuration.

The sensor is just 1.1 mm square so it's ideal for precise proximity sensing. We mounted it on a circuit board under the switch. The sensor's low impedance and large output allows it connect directly to a microcontroller. We have a linear stepper motor for testing.

With an analog sensor, we can set the activate and release points with a comparator or in software. In this demo we used an Arduino and set constants for the activate and release points in software.

We can set it for standard thresholds, tight thresholds for Rapid-Trigger fast typing or gaming, or anywhere in between.

The sensors have best-in-class sensitivity and precision, large outputs and low impedance for direct interface to microprocessors, high speed for fast polling, and small packages.

https://www.nve.com/Downloads/ALTxxx-10.pdf
https://www.youtube.com/watch?v=0Ic7X9gRbFE
https://www.snapeda.com/parts/ALT025-14E/NVE/view-part/

https://www.youtube.com/watch?v=3HGQzlyUNsI

------------------------------------------------------------------------

Use a comparator:
A comparator is an electronic component that compares two analog input voltages
and produces a digital output signal to indicate which voltage is larger. It is
essentially a high-gain differential amplifier with a binary output that is
either a logic high or low. This makes it useful for tasks like measuring and
digitizing signals, such as in analog-to-digital converters (ADCs), or for
creating simple switches, like turning a fan on when a temperature gets too
high.

------------------------------------------------------------------------

The battery life is very good - I'm using full RGB and used it heavily for at
least 8 hrs a day, and it was lasting up to a week. But if you want to max it
out, turn off the RGB. It also decreases latency (RGB increases latency). Then
it can last even 2 weeks.

Now I'm testing a TMR with an 8000 mAh battery unit, and I can see it will be
doubled.

------------------------------------------------------------------------

Travel distance of low profile switches:
Keychron optical: 2.5 mm
Kailh choc: 3 mm
Kailh magnetic: 2.8 mm
Gateron magnetic: 3.5 mm

(with nuphy keycap on, Gateron is 15.2mm - 11.7mm

Use o-ring inside the shaft of the switch to reduce travel.

------------------------------------------------------------------------

Sensors:

MDT TMR2617S
Programmed at:
	sensitivity: 0.7 mv/V/Gs
	offset voltage: 300 mV/V
Output:
	0.8V - 0V (when key pressed)
NOTE: This is wrongly programmed, but still usable. Offset voltage should be
700 mv/V (or 500 mV/V if you don't want to worry about polarity).
If programmed at 700 mV/V, voltage range will be 2.4V-0V. If programmed at
500 mV/V, it will be 1.6V-0V (3.2V/2 = 1.6V).

MDT TMR2615 (1.6mm package)
Programmed at:
	sensitivity: 2 mV/V/Gs
	offset voltage: 300 mV/V
Output:
	1V - 0.75V (when key pressed)
NOTE: This is correctly programmed if (looking from above the switch), SMD is
orinted to the right of magnet with one pin above and 2 pins below. However
sensitivity can be increased further (or perhaps it can be moved a bit away from
magnet).

----------------------------------------------------------------------

For an M2 self-tapping screw (especially a fine one) in a typical ABS boss, the
threads will likely become significantly degraded, or the holding force
noticeably reduced, after:$$\text{**3 to 7 Re-insertions**}$$In critical
applications or where high clamping force is needed, designers will often assume
a maximum of 3 cycles to be safe. For non-critical panels, you might achieve 10+
cycles if extreme care is taken.

----------------------------------------------------------------------

That's a specific fastener! The **self-tapping nut (M2xM4x4)** is designed to be
installed *into* the plastic to provide a reusable **M2 internal thread**, using
an **M4 outer thread** to cut and secure itself into the plastic boss.

The boss diameter must be calculated based on the **outer diameter of the M4
self-tapping thread** that creates the connection with the plastic.

## 📐 Recommended Boss Diameter

General guidelines for boss design in ABS plastic recommend that the boss outer
diameter ($\mathbf{d_A}$) should be **2.0 to 2.5 times** the nominal outer
thread diameter ($\mathbf{d}$) of the screw or insert.

Since the **outer thread is M4** (nominal diameter $\mathbf{d} = 4.0 \text{
mm}$), the recommended minimum boss diameter is:

$$\text{Boss Outer Diameter} \approx 2.0 \times 4.0 \text{ mm} = \mathbf{8.0
\text{ mm}}$$

A safer, more robust boss would use the higher end of the range:

$$\text{Boss Outer Diameter} \approx 2.5 \times 4.0 \text{ mm} = \mathbf{10.0
\text{ mm}}$$

* **Best Practice Recommendation:** Design the boss outer diameter
  ($\mathbf{d_A}$) to be between **8.0 mm and 10.0 mm** for optimal strength and
  reduced risk of the boss cracking from the hoop stress created by the
  self-tapping action. 

---

## 🔩 Critical Design Parameters

In addition to the outer diameter, you must specify the correct inner hole
diameter and wall thickness:

### 1. Inner Pilot Hole Diameter ($\mathbf{d_H}$)

This is the diameter of the hole the M4 outer thread taps into. It must be
slightly smaller than the outer thread diameter but larger than the root (minor)
diameter of the thread.

* **Rule of Thumb:** $d_H \approx 0.8 \times d$ (nominal outer diameter). $$d_H
  \approx 0.8 \times 4.0 \text{ mm} = 3.2 \text{ mm}$$
* **Recommendation:** The pilot hole diameter ($\mathbf{d_H}$) should be
  approximately **3.2 mm** in ABS. Some sources suggest a range of $3.2 \text{
  mm}$ to $3.5 \text{ mm}$ depending on the exact material batch and thickness.

### 2. Boss Wall Thickness ($\mathbf{t}$)

The wall thickness of the boss should be strong enough to withstand the hoop
stress generated by the screw without cracking, but not so thick that it causes
sink marks in the surrounding plastic part.

* **Rule of Thumb:** Boss wall thickness ($\mathbf{t}$) is typically $40\%$ to
  $60\%$ of the nominal wall thickness of the plastic part, but must be strong
  enough for the screw.
* The thickness of the wall surrounding the hole is: $$\text{Wall Thickness} =
  (\text{Boss OD} - \text{Hole ID}) / 2$$ If you use the $8.0 \text{ mm}$ boss
  and $3.2 \text{ mm}$ hole: $$\text{Wall Thickness} = (8.0 \text{ mm} - 3.2
  \text{ mm}) / 2 = \mathbf{2.4 \text{ mm}}$$

The $2.4 \text{ mm}$ wall thickness provides adequate material to withstand the
radial stress from the M4 self-tapping thread.

------------------------------------------------------------------------
vim:tw=80:ts=4:ft=markdown:ai:
