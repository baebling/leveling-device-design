"""Rev F source baseline; screening only, NOT APPROVED FOR FABRICATION.

Dimensions are mm. Unknown manufacturer evidence remains None or an explicit
unresolved entry. Completing sources alone never authorizes a purchase.
"""
from dataclasses import dataclass
from math import isfinite


SOURCE_REFERENCES = {
    "eye_step": "references/vendor_cad/LM4075OE-1075-100mm.stp",
    "eye_sales_drawing": "web_research/evidence/2026-08-31/LM4075OE_detail_source_900x1530.jpg",
    "actuator": "https://www.motorbank.kr/goods/goods_view.php?goodsNo=1000035578",
    "phs": "https://image.trusco-sterra2.com/pdf/zumen/PHS6_4500__ZM.pdf",
    "pin": "https://kr.misumi-ec.com/pdf/press/2018_pr_1011.pdf",
    "pin_candidate": "https://kr.misumi-ec.com/vona2/detail/110100143940/?HissuCode=MSB6-35",
    "profile": "https://www.dycprofile.co.kr/3030%EC%8B%9C%EB%A6%AC%EC%A6%88/715834",
    "profile_seller": "https://alsw.co.kr/goods/goods_view.php?goodsNo=1000000079",
    "tnut_candidate": "https://www.navimro.com/p/K14671215/",
    "tnut_drawing": "https://img.navimro.com/img/pi/detail/1171730.jpg",
}
CHECKED_ON = "2026-10-02"


@dataclass(frozen=True)
class PocketInputs:
    bracket_count: int
    eye_hole_bounds_mm: tuple[float, float]
    pin_dmin_mm: float
    eye_offset_mm: float
    phs_outer_d_mm: float
    phs_outer_width_mm: float
    phs_ball_width_mm: float
    shoulder_contact_length_mm: float | None
    profile_slot_width_mm: float | None
    profile_slot_verified: bool
    purchase_release: bool
    # Required source/tolerance gaps, not a structural-approval checklist.
    unresolved_evidence: tuple[str, ...] = (
        "LM4075OE eye bore discrepancy and delivered eye dimensional tolerances",
        "TRUSCO PHS6 versus BOM THK PHS6 exact delivered order identity",
        "PHS6 housing outer diameter/width manufacturing tolerances",
        "Selected MSB6 order, continuous shoulder contact length and fillet geometry",
        "Delivered DNF3030 slot section and tolerances",
        "Selected T-nut manufacturer drawing, tolerances and slot compatibility",
    )


def load_inputs() -> PocketInputs:
    """Return nominal supplier bounds; no guessed values for unknown evidence."""
    return PocketInputs(
        bracket_count=3, eye_hole_bounds_mm=(6.0, 6.4), pin_dmin_mm=5.95,
        eye_offset_mm=16.0, phs_outer_d_mm=20.0, phs_outer_width_mm=6.75,
        phs_ball_width_mm=9.0, shoulder_contact_length_mm=None,
        profile_slot_width_mm=None, profile_slot_verified=False,
        purchase_release=False,
    )


def source_complete(inputs: PocketInputs) -> bool:
    """True only for a dimensionally valid record with all source gaps closed.

This is evidence completeness, not strength, interference or release approval.
Consumers must screen both conflicting eye bounds while this returns False.
"""
    values = (*inputs.eye_hole_bounds_mm, inputs.pin_dmin_mm,
              inputs.eye_offset_mm, inputs.phs_outer_d_mm,
              inputs.phs_outer_width_mm, inputs.phs_ball_width_mm,
              inputs.shoulder_contact_length_mm, inputs.profile_slot_width_mm)
    return (
        type(inputs.bracket_count) is int and inputs.bracket_count == 3
        and len(inputs.eye_hole_bounds_mm) == 2
        and all(value is not None and isfinite(value) and value > 0 for value in values)
        and inputs.eye_hole_bounds_mm[0] <= inputs.eye_hole_bounds_mm[1]
        and inputs.profile_slot_verified is True
        and not inputs.unresolved_evidence
    )
