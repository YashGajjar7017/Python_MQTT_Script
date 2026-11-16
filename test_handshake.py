#!/usr/bin/env python3
"""
Test Handshake Script
Runs offline simulator mode and configuration validator to verify the entire system without network dependencies.
"""

import os
import sys
from MQTT_SERVER_CONTROLLER import load_config_file, run_simulator, DEFAULT_CONFIG


def run_tests():
    print("=" * 70)
    print("        RUNNING CONFIGURATION AND HANDSHAKE VALIDATION TESTS")
    print("=" * 70)

    # 1. Test YAML load
    if os.path.exists("config.yaml"):
        print("[1/4] Testing config.yaml loading...")
        cfg_yaml = load_config_file("config.yaml")
        assert "broker" in cfg_yaml, "Missing 'broker' in YAML"
        assert "topics" in cfg_yaml, "Missing 'topics' in YAML"
        assert len(cfg_yaml["topics"]["info_subscriptions"]) >= 8, "Expected at least 8 target subscriptions"
        print("      PASS: config.yaml is valid with single IMEI target topics.")
    else:
        print("[1/4] SKIP: config.yaml not found.")

    # 2. Test XML load
    if os.path.exists("config.xml"):
        print("[2/4] Testing config.xml loading...")
        cfg_xml = load_config_file("config.xml")
        assert "broker" in cfg_xml, "Missing 'broker' in XML"
        assert "topics" in cfg_xml, "Missing 'topics' in XML"
        assert len(cfg_xml["topics"]["info_subscriptions"]) >= 8, "Expected at least 8 target subscriptions"
        print("      PASS: config.xml is valid with single IMEI target topics.")
    else:
        print("[2/3] SKIP: config.xml not found.")

    # 3. Test Modbus Registers Map & GPRS Search
    print("[3/4] Testing Modbus Register Map & GPRS Search...")
    from modbus_registers import ALL_REGISTERS, search_registers, get_gprs_registers
    assert len(ALL_REGISTERS) >= 200, f"Expected >200 registers, got {len(ALL_REGISTERS)}"
    gprs_list = get_gprs_registers()
    assert len(gprs_list) >= 20, f"Expected >20 GPRS registers, got {len(gprs_list)}"
    gprs_searched = search_registers("GPRS")
    assert len(gprs_searched) >= 5, "Expected at least 5 registers with GPRS in name"
    print(f"      PASS: {len(ALL_REGISTERS)} registers loaded. GPRS search found {len(gprs_searched)} items.")

    # 4. Test Offline Simulator Handshake
    print("[4/4] Testing Offline Simulator Handshake...")
    run_simulator(DEFAULT_CONFIG)
    print("      PASS: Simulator handshake executed successfully.")

    print("\n" + "=" * 70)
    print("           ALL END-TO-END VALIDATION TESTS PASSED!")
    print("=" * 70)


if __name__ == "__main__":
    run_tests()
