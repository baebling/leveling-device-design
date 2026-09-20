"""Electrical data contract: catch bypassed cutoff, floating pins and bus mixups."""
import csv
import unittest
from collections import Counter, defaultdict
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
PREFIX = ROOT / "fabrication"


def rows(kind):
    path = PREFIX / f"portenta_dmc200_{kind}_2026-09-18.csv"
    assert path.is_file(), f"Electrical map missing: {path.name}"
    with path.open(encoding="utf-8-sig", newline="") as stream:
        return list(csv.DictReader(stream))


class ElectricalPackageTest(unittest.TestCase):
    def setUp(self):
        self.io = rows("io_map")
        self.term = rows("terminal_map")
        self.wire = rows("point_to_point")
        self.pins = {r["terminal_id"]: r for r in self.term}

    def reachable(self, start, excluded=()):
        graph = defaultdict(set)
        for r in self.wire:
            if r["connection_type"] not in excluded:
                graph[r["from_terminal"]].add(r["to_terminal"])
                graph[r["to_terminal"]].add(r["from_terminal"])
        seen, todo = set(), [start]
        while todo:
            node = todo.pop()
            if node not in seen:
                seen.add(node)
                todo.extend(graph[node] - seen)
        return seen

    def test_machine_readable_contract_and_unique_ownership(self):
        self.assertEqual(set(self.io[0]), {"signal_id", "device_id", "bom_id", "axis", "function", "interface", "address", "endpoint", "net", "status", "source"})
        self.assertEqual(set(self.term[0]), {"terminal_id", "device_id", "bom_id", "pin", "net", "role", "mandatory", "status", "source"})
        self.assertEqual(set(self.wire[0]), {"wire_id", "from_terminal", "to_terminal", "net", "connection_type", "segment", "status", "note"})
        for data, key in ((self.io, "signal_id"), (self.term, "terminal_id"), (self.wire, "wire_id")):
            self.assertEqual(len(data), len({r[key] for r in data}))
        self.assertEqual(len(self.term), len({(r["device_id"], r["pin"]) for r in self.term}))
        with (ROOT / "procurement/reve_portenta_order_bom_2026-09-18.csv").open(encoding="utf-8-sig") as stream:
            bom = {r["ID"] for r in csv.DictReader(stream)}
        for r in self.term + self.io:
            self.assertIn(r["bom_id"], bom | {"EXISTING", "TBD"})
            self.assertNotEqual(r["bom_id"], "AL01")
            self.assertTrue(r["source"])
        for data in (self.io, self.term, self.wire):
            for row in data:
                self.assertNotIn(None, row)
                self.assertNotIn(None, row.values())

    def test_bus_addresses_and_axes_have_real_endpoints(self):
        for interface, wanted in (("DMC_RS485", {1, 2, 3}), ("SENSOR_RS485", {11, 12})):
            self.assertEqual({int(r["address"]) for r in self.io if r["interface"] == interface}, wanted)
        for axis in ("A1", "A2", "A3"):
            for function in ("MOTOR_P", "MOTOR_N", "ENC_A", "ENC_B"):
                matches = [r for r in self.io if r["axis"] == axis and r["function"] == function]
                self.assertEqual(len(matches), 1)
                self.assertIn(matches[0]["endpoint"], self.pins)

    def test_cutoff_disconnects_every_motor_but_not_controller_or_logger(self):
        on = self.reachable("E04.VPLUS", ("LOAD", "TERMINATOR", "CONVERTER", "SIGNAL"))
        off = self.reachable("E04.VPLUS", ("RELAY_NO", "LOAD", "TERMINATOR", "CONVERTER", "SIGNAL"))
        for dev in ("DC01", "DC02", "DC03"):
            self.assertIn(dev + ".VPLUS", on)
            self.assertNotIn(dev + ".VPLUS", off)
        for pin in ("PC01.J4_1", "HM01.PWR_PLUS", "IF01.9"):
            self.assertIn(pin, off)
        coil_on = self.reachable("PC01.J6_2", ("LOAD", "SIGNAL"))
        coil_estop = self.reachable("PC01.J6_2", ("ESTOP_NC", "LOAD", "SIGNAL"))
        self.assertIn("E11.COIL_PLUS", coil_on)
        self.assertNotIn("E11.COIL_PLUS", coil_estop)

    def test_every_mandatory_terminal_is_accounted_for_and_wires_match_nets(self):
        used = Counter()
        for wire in self.wire:
            ends = (wire["from_terminal"], wire["to_terminal"])
            for endpoint in ends:
                self.assertIn(endpoint, self.pins)
                used[endpoint] += 1
            if wire["connection_type"] == "WIRE":
                for endpoint in ends:
                    self.assertEqual(self.pins[endpoint]["net"], wire["net"])
        for pin in self.term:
            if pin["mandatory"] == "YES":
                self.assertGreater(used[pin["terminal_id"]], 0, pin)
        for signal in self.io:
            self.assertIn(signal["endpoint"], self.pins)
            pin = self.pins[signal["endpoint"]]
            self.assertEqual(signal["device_id"], pin["device_id"])
            self.assertEqual(signal["net"], pin["net"])

    def test_pe_and_external_limit_exclusion(self):
        for pin in self.term:
            if pin["net"] == "PE":
                self.assertIn(pin["role"], {"PROTECTIVE_EARTH", "SHIELD_BOND"})
            self.assertNotIn("EXT_LIMIT", pin["net"])
        pe_reach = self.reachable("E07.PE", ("LOAD", "CONVERTER", "SIGNAL"))
        self.assertNotIn("PC01.J4_3", pe_reach)
        self.assertNotIn("DC01.GND", pe_reach)

    def test_terminators_are_two_per_continuous_segment(self):
        resistors = [r for r in self.wire if r["connection_type"] == "TERMINATOR"]
        self.assertEqual(Counter(r["segment"] for r in resistors), {"DMC_HOST": 2, "DMC_FIELD": 2, "SENSOR": 2})
        self.assertEqual(len({(r["from_terminal"], r["to_terminal"]) for r in resistors}), 6)
        for wire in resistors:
            self.assertIn("120", wire["note"])

    def test_hmi_ethernet_and_sensor_bus_are_not_dmc_bus(self):
        self.assertTrue(any(r["device_id"] == "HM01" and r["interface"] == "MODBUS_TCP" for r in self.io))
        dmc = self.reachable("PC01.J5_3", ("LOAD", "TERMINATOR", "CONVERTER", "SIGNAL"))
        self.assertNotIn("HM01.COM2_2", dmc)
        self.assertNotIn("IS01.A", dmc)
        for r in self.io:
            if r["function"] == "SENSOR_GATEWAY":
                self.assertTrue(r["status"].startswith("HOLD"))
        gateways = [r for r in self.io if r["function"] == "SENSOR_GATEWAY"]
        self.assertEqual(len(gateways), 1)
        self.assertEqual(gateways[0]["device_id"], "HM01")
        self.assertFalse(any(r["device_id"] == "PC01" and r["interface"] == "SENSOR_RS485" for r in self.io))

    def test_no_hidden_cutoff_bypass_or_unfused_motor_feed(self):
        excluded = ("RELAY_NO", "LOAD", "TERMINATOR", "CONVERTER", "SIGNAL", "USB", "ETHERNET")
        for start in ("E04.VPLUS", "PC01.J4_1", "HM01.PWR_PLUS"):
            off = self.reachable(start, excluded)
            for axis in range(1, 4):
                self.assertNotIn(f"DC0{axis}.VPLUS", off)
        unfused = self.reachable("E04.VPLUS", ("FUSE", "LOAD", "TERMINATOR", "CONVERTER", "SIGNAL"))
        for axis in range(1, 4):
            self.assertNotIn(f"DC0{axis}.VPLUS", unfused)

    def test_termination_is_at_segment_ends_and_not_a_series_wire(self):
        expected = {
            "DMC_HOST": {"PC01", "IF01"},
            "DMC_FIELD": {"IF01", "DC03"},
            "SENSOR": {"HM01", "IS02"},
        }
        for segment, devices in expected.items():
            ends = [r for r in self.wire if r["connection_type"] == "TERMINATOR" and r["segment"] == segment]
            self.assertEqual({self.pins[r["from_terminal"]]["device_id"] for r in ends}, devices)
            for row in ends:
                a, b = self.pins[row["from_terminal"]], self.pins[row["to_terminal"]]
                self.assertEqual(a["device_id"], b["device_id"])
                self.assertNotEqual(a["net"], b["net"])

    def test_signal_and_motor_common_are_never_protective_earth(self):
        signal_pins = [r for r in self.term if r["role"] in {"SIGNAL_COMMON", "ENCODER_RETURN", "POWER_RETURN"}]
        self.assertTrue(signal_pins)
        for pin in signal_pins:
            self.assertNotEqual(pin["net"], "PE")
        for pin in self.term:
            self.assertNotIn("LIMIT", pin["net"])
        for axis in range(1, 4):
            self.assertTrue(any(r["net"] == f"5V_ENCODER_A{axis}" for r in self.term))

    def test_vendor_dependent_details_are_not_released(self):
        for pin in self.term:
            if pin["device_id"].startswith("DC") or pin["device_id"].startswith("ACT") or pin["device_id"] in {"E09C", "E11"}:
                self.assertTrue(pin["status"].startswith("HOLD"), pin)
            if "TBD" in pin["pin"]:
                self.assertTrue(pin["status"].startswith("HOLD"), pin)


if __name__ == "__main__":
    unittest.main()
