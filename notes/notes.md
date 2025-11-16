https://www.waveshare.com/wiki/RP2040-Tiny

https://jlccnc.com/help/article/CNC-Machining-Design-Guideline

======================================================================

https://www.youtube.com/watch?v=wz2ZO3kSfNE

omnipolar response: sensor responds to N or S pole with equally magnitude.

You can use unipolar sensor, in which case offset is not necessary.

https://www.youtube.com/watch?v=Laexij_rioU

Pay attention to frequency. The smaller it is the better the power
consumption, but lower the sensitivity. He quoted 330k Hz as max (3us).

https://www.youtube.com/watch?v=vwzUx7oq-f0

analog vs digital sensors

======================================================================


 7G = 0.7mT

======================================================================

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

======================================================================

Use a comparator:
A comparator is an electronic component that compares two analog input voltages
and produces a digital output signal to indicate which voltage is larger. It is
essentially a high-gain differential amplifier with a binary output that is
either a logic high or low. This makes it useful for tasks like measuring and
digitizing signals, such as in analog-to-digital converters (ADCs), or for
creating simple switches, like turning a fan on when a temperature gets too
high.

======================================================================
vim:tw=78:ts=4:ft=help:norl:ma:noro:ai:lcs=tab\:\ \ ,trail\:~:
