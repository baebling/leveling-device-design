# Cart Profile Receiver Summary

Status: Phase 1 preliminary summary. Not approved for fabrication.

Hardpoint follow-up: `outputs/reports/cart_receiver_hardpoint_summary.md`

## Recommendation

Use `CR-01` as the next cart-side receiver candidate:

| Item | Candidate |
|---|---:|
| Receiver type | Two longitudinal aluminum-profile rails |
| Rail basis | HFS8-4040 or equivalent sourced 40 mm profile |
| Receiver zone | 760 mm L x 560 mm W |
| Rail centerline Y | +/-260 mm |
| Rest pads | 4 shim-adjustable pads |
| Locator topology | one master locator + one slotted/diamond secondary locator |
| Locator X span | 520 mm |
| Latches | 2 minimum, 4 placeholder |
| Hard points | local metal inserts/plates for pins, pads, latch keepers, and stops |

This keeps the receiver adjustable and easy to assemble while avoiding raw profile slots as the final wear or shear faces.

## Screened Values

| Screen | Result |
|---|---:|
| Two-rail HFS8 receiver kit mass | about 4.50 kg |
| Self-contained HFS8 rectangular receiver mass | about 6.43 kg |
| Two-rail GFS8 stiff reserve mass | about 5.16 kg |
| Active worst rest-pad max load | about 331 N |
| Active worst rest-pad minimum load | about 81 N |
| Guide/locator shear design load | about 154 N |
| Yaw couple force at 520 mm locator span | about 32 N |
| Per-latch uplift with 4 latches | about 31 N |

## Decision

- Prefer the two-rail HFS8 receiver kit because it stays below about 5 kg and leaves more of the 10 kg empty-cart basis for the rest of the cart.
- Keep the rectangular HFS8 receiver only if the future cart lower frame cannot provide cross support.
- Keep GFS8 as a stiffness reserve only.
- Do not freeze a 30 mm profile option until source-backed mass and stiffness values are added.
- Use CR-01-H1 as the next hardpoint seed, but do not treat it as fabrication detail.

```text
CR-01 CARRIED FORWARD
NOT READY FOR APPROVE PARAMETERS
NOT APPROVED FOR FABRICATION
```
