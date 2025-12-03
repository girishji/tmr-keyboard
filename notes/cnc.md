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
