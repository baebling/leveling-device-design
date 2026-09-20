"""Rev M2R1 review CAD. Nominal interfaces only; NOT FOR FABRICATION.

Reuses M2 geometry/kinematics and replaces the simplified upper joints.
Supplier-dependent values live in JointParameters, not hidden tolerances.
"""
from dataclasses import dataclass, asdict
from functools import lru_cache
from math import degrees, sqrt
import cadquery as cq
from cad import manual_turnbuckle_rev_m2 as base
from calculations import manual_turnbuckle_rev_m2_screen as data

Component = base.Component
SILVER = (0.76, 0.79, 0.82)
STEEL = (0.12, 0.15, 0.18)
BLUE = (0.04, 0.36, 0.65)
BRONZE = (0.65, 0.46, 0.22)


@dataclass(frozen=True)
class JointParameters:
    # All fits/ball housing dimensions are provisional, not supplier approval.
    fork_gap: float = 22.4
    ear_width: float = 11.0
    fork_bore: float = 20.1
    bush_od: float = 19.98
    bush_id: float = 12.1
    bush_flange_od: float = 26.0
    bush_flange_thickness: float = 1.5
    pin_diameter: float = 12.0
    pin_length: float = 80.0
    pin_smooth_length: float = 50.0
    washer_thickness: float = 2.0
    washer_od: float = 24.0
    nut_height: float = 12.0
    inner_ring_width: float = 16.0
    ball_diameter: float = 24.0
    socket_diameter: float = 24.2
    housing_width: float = 12.0
    housing_od: float = 30.0
    inner_spacer_od: float = 17.0

    @property
    def inner_spacer_width(self):
        return (self.fork_gap - self.inner_ring_width) / 2

    @property
    def ear_outer(self):
        return self.fork_gap / 2 + self.ear_width

    @property
    def flange_outer(self):
        return self.ear_outer + self.bush_flange_thickness

    @property
    def head_plane(self):
        return -self.flange_outer - self.washer_thickness


J = JointParameters()


def comp(name, group, shape, color=SILVER, material="PROVISIONAL geometry"):
    return Component(name, group, shape, color, material)


def local_ring(y, od, id_, width):
    return base._ring((0, y, 0), (0, 1, 0), od, id_, width, (1, 0, 0))


def _upper_support():
    parts = []
    for s in (-1, 1):
        ear = base._box(50, J.ear_width, 52,
                        (0, s * (J.fork_gap / 2 + J.ear_width / 2), 6))
        bore = base._cylinder_between((0, -50, 0), (0, 50, 0), J.fork_bore / 2)
        parts.append(ear.cut(bore))
    parts.append(base._box(50, 2 * J.ear_outer, 8, (0, 0, 28)))
    parts.append(base._cylinder_between((0, 0, 32), (0, 0, 82), 10))
    shape = parts[0]
    for other in parts[1:]:
        shape = shape.fuse(other)
    return shape.clean()


@lru_cache(maxsize=1)
def joint_local_parts():
    parts = [comp("FORK", "upper_supports", _upper_support(), STEEL,
                  "BJ762-20001 nominal envelope; provisional bore/gap")]
    for s, tag in ((-1, "L"), (1, "R")):
        sleeve = local_ring(s * (J.fork_gap / 2 + J.ear_width / 2),
                            J.bush_od, J.bush_id, J.ear_width)
        flange = local_ring(s * (J.ear_outer + J.bush_flange_thickness / 2),
                            J.bush_flange_od, J.bush_id, J.bush_flange_thickness)
        parts.append(comp(f"BUSH_{tag}", "upper_bushes", sleeve.fuse(flange).clean(), BRONZE,
                          "6 flanged bushes total; material/fit supplier hold"))
        parts.append(comp(f"INNER_SPACER_{tag}", "upper_inner_spacers",
                          local_ring(s * (J.inner_ring_width / 2 + J.inner_spacer_width / 2),
                                     J.inner_spacer_od, J.bush_id, J.inner_spacer_width),
                          SILVER, "inner-ring side spacer; provisional new part"))
        parts.append(comp(f"WASHER_{tag}", "upper_pin_washers",
                          local_ring(s * (J.flange_outer + J.washer_thickness / 2),
                                     J.washer_od, 13.0, J.washer_thickness)))
    start = J.head_plane
    shaft = base._cylinder_between((0, start, 0), (0, start + J.pin_smooth_length, 0), J.pin_diameter / 2)
    thread_envelope = base._cylinder_between((0, start + J.pin_smooth_length, 0),
                                           (0, start + J.pin_length, 0), J.pin_diameter / 2)
    head = base._hex_prism_between((0, start - 7.5, 0), (0, start, 0), 21.94)
    parts.append(comp("PIN_M12X80", "upper_pins", shaft.fuse(thread_envelope).fuse(head).clean(), STEEL,
                      "candidate M12x80; 50 mm smooth grip MUST be verified; threads represented by envelope"))
    nut_start = J.flange_outer + J.washer_thickness
    nut = base._hex_prism_between((0, nut_start, 0), (0, nut_start + J.nut_height, 0), 21.94)
    bore = base._cylinder_between((0, nut_start - 1, 0), (0, nut_start + J.nut_height + 1, 0), 6.15)
    parts.append(comp("LOCK_NUT", "upper_pin_nuts", nut.cut(bore), STEEL,
                      "M12 retaining nut; thread and locking geometry omitted"))
    return tuple(parts)


def _place_joint(shape, index, pitch, roll, solved):
    x, y = data.support_points(data.P.upper_support_radius_mm)[index - 1]
    shape = shape.rotate((0, 0, 0), (0, 0, 1), data.SUPPORT_ANGLES_DEG[index - 1])
    shape = shape.translate((x, y, 0))
    return base._transform_shape(shape, pitch, roll, solved["yaw_rad"],
                                 (solved["x_mm"], solved["y_mm"], data.P.upper_pin_z_mm))


def _bearing_and_link(index, lower, upper, tangent, upper_tangent):
    l, u = cq.Vector(*lower), cq.Vector(*upper)
    unit = (u - l).normalized()
    original = base._link_shape(lower, upper, tangent, upper_tangent).Solids()
    if len(original) != 16:
        raise ValueError("M2 link topology changed; reassess rod-end replacement")
    # Outer housing follows the link/lower hinge plane. Inner bearing follows upper pin.
    axis = cq.Vector(*tangent).normalized()
    # Revolved sections avoid the STEP round-trip defects observed for
    # globally translated boolean sphere pockets. Local Y is the pin axis.
    half = J.housing_width / 2
    rad = J.socket_diameter / 2
    edge = sqrt(rad**2 - half**2)
    shell = (cq.Workplane('XY').moveTo(J.housing_od/2, -half)
             .lineTo(J.housing_od/2, half).lineTo(edge, half)
             .threePointArc((rad, 0), (edge, -half)).close()
             .revolve(360, (0,0,0), (0,1,0)).val())
    neck = base._cylinder_between((-50,0,0), (-13,0,0), 9.5)
    housing_local = shell.fuse(neck).clean()
    plane = cq.Plane(origin=upper, xDir=unit.toTuple(), normal=unit.cross(axis).toTuple())
    housing = housing_local.located(cq.Location(plane))
    # Original final two solids were simplified neck/ring; replace them explicitly.
    link = cq.Compound.makeCompound(list(original[:-2]) + [housing])
    rad, half = J.ball_diameter/2, J.inner_ring_width/2
    edge = sqrt(rad**2-half**2)
    ball_local = (cq.Workplane('XY').moveTo(J.bush_id/2,-half).lineTo(edge,-half)
                  .threePointArc((rad,0),(edge,half)).lineTo(J.bush_id/2,half)
                  .close().revolve(360,(0,0,0),(0,1,0)).val())
    ut = cq.Vector(*upper_tangent).normalized()
    xx = ut.cross(unit).cross(ut).normalized()
    plane = cq.Plane(origin=upper, xDir=xx.toTuple(), normal=xx.cross(ut).toTuple())
    ball = ball_local.located(cq.Location(plane))
    return [comp(f"LEG_{index}_STB_M12_LINK", "links", link, STEEL,
                 "M2 threaded stack envelope; rod-end housing nominal, not vendor STEP"),
            comp(f"U{index}_INNER_BEARING", "upper_bearings", ball, SILVER,
                 "spherical inner bearing envelope, supplier geometry hold")]


@lru_cache(maxsize=6)
def _label(text):
    # Adhesive film, not a machined structural plate.
    film = base._box(24, 0.15, 4, (0, 0, 0))
    plane = cq.Plane(origin=(0, -0.076, 0), xDir=(1, 0, 0), normal=(0, -1, 0))
    lettering = cq.Workplane(plane).text(text, 3.2, 0.04, font="Arial", combine=True).val()
    return film, lettering


def components_for_pose(pitch=0.0, roll=0.0, decoration=True):
    solved = data.solve_platform(pitch, roll)
    rotation = data.rotation_matrix(pitch, roll, solved["yaw_rad"])
    components = []
    for c in base.components_for_pose(pitch, roll):
        if c.group in ("links", "upper_supports") or (c.name.startswith("U") and c.group == "joint_pins"):
            continue
        color = SILVER if c.group in ("lower_frame", "upper_frame", "lower_adapters", "upper_adapters") else STEEL
        components.append(comp(c.name, c.group, c.shape, color, c.material))
    for i in range(1, 4):
        for c in joint_local_parts():
            components.append(comp(f"U{i}_{c.name}", c.group,
                                   _place_joint(c.shape, i, pitch, roll, solved), c.color, c.material))
    for i, (lower, upper, (_, tangent)) in enumerate(zip(data.lower_pin_points(),
                   data.upper_pin_points(pitch, roll), data.support_basis()), 1):
        ut = base._transform_vector(tangent, rotation).toTuple()
        components.extend(_bearing_and_link(i, lower, upper, tangent, ut))
    if decoration:
        for i in range(1, 4):
            film, text = _label(f"A{i}")
            for upper in (False, True):
                r = data.P.upper_support_radius_mm if upper else data.P.lower_support_radius_mm
                x, y = data.support_points(r)[i - 1]
                z = 247.5 - data.P.upper_pin_z_mm if upper else 57.5
                for tag, shape, color in (("FILM", film, BLUE), ("TEXT", text, (1, 1, 1))):
                    shape = shape.translate((x, y - 30.08, z))
                    if upper:
                        shape = base._transform_shape(shape, pitch, roll, solved["yaw_rad"],
                            (solved["x_mm"], solved["y_mm"], data.P.upper_pin_z_mm))
                    components.append(comp(f"{'U' if upper else 'L'}{i}_AXIS_{tag}", "labels", shape, color, "label film / ink"))
    return components


def assumptions():
    return {"joint_parameters_mm": asdict(J),
            "status": "PRELIMINARY_NOT_FOR_FABRICATION",
            "source_basis": "IMAO BJ762 nominal dimensions; remaining fits are provisional",
            "scope": "M2 upper-joint CAD correction and axis labels; original kinematics unchanged",
            "pin_smooth_margin_past_last_bush_mm": J.head_plane + J.pin_smooth_length - J.flange_outer,
            "original_simplifications_remaining": ["profile section envelopes", "lower pin retention not detailed",
                "frame bracket fasteners not fully modeled", "threads represented by envelopes",
                "cart receiver and lower mounting specifics unresolved", "mechanical travel stops unresolved"]}
