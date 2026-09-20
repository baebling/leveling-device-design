# YAW-A Gimbal Kinematic Summary

Status: Phase 1 preliminary. Not approved for fabrication.

The central YAW-A head now has an explicit physical axis order: fixed lower `+Y` pitch pin followed by an upper `+X` roll pin carried by the pitched yoke. The platform mapping is `R = Ry(pitch) * Rx(roll)`, which keeps the selected world-heading yaw at zero throughout the required +/-3 degree grid. This preserves exactly the intended three platform freedoms: Z, pitch, and roll.

The previous 8 degree design / 10 degree hard-stop figures apply to **combined total gimbal tilt**. They must not be duplicated as 10 degree limits at each pin. A simple preliminary implementation is four adjustable pitch/roll pin stops at +/-7 degrees each. Their worst diagonal pose is about 9.89 degrees total tilt, below the 10 degree envelope, while the required +/-3 degree diagonal pose plus 2 degrees margin is about 6.24 degrees.

At the active 16.39 Nm yaw design torque, the tilted yoke mechanically constrains the yaw direction but also produces a small coupled pitch/roll reaction. At 3 degrees pitch, about 16.37 Nm projects into the locked direction and about 0.86 Nm enters the pitch/roll holding path. This needs a later actuator-holding and structural check; it is not a free yaw degree of freedom.

The next required evidence is a non-load-bearing clearance/backlash mock-up with the actual yoke pin/washer/stop stack, followed by the separate real HRT8E 14 degree lower-bracket gauge. No detailed CAD or fabrication release follows from this calculation alone.
