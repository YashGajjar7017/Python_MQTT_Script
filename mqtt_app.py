#!/usr/bin/env python3
"""
MQTT Remote Device Controller & Request Handler
Supports:
  - Interactive selection menu (YAML, XML, JSON, Wizard, Simulator)
  - Custom IMEI & Host Wizard with auto-generated 9-topic suite
  - Live MQTTS over TLS (e.g. iot.medha-res.com:8883)
  - Request/Response & ACK handshake tracking
  - Built-in Offline Device Simulator
"""

import sys
import os
import time
import json
import ssl
import glob
import argparse
import getpass
import xml.etree.ElementTree as ET
from datetime import datetime, timezone

try:
    import yaml
    HAS_YAML = True
except ImportError:
    HAS_YAML = False

try:
    import paho.mqtt.client as mqtt
    HAS_PAHO = True
except ImportError:
    HAS_PAHO = False

DEFAULT_CONFIG = {
    "broker": {
        "name": "Medha Server",
        "host": "iot.medha-res.com",
        "port": 8883,
        "protocol": "mqtts",
        "client_id": "f915acbe-0d4e-4de2-9204-134295a904bc",
        "append_timestamp": True,
        "username": "InternalUser",
        "password": "",
        "keepalive": 10,
        "clean_session": True,
        "use_tls": True
    },
    "topics": {
        "ondemand_sub_template": "rtsg-1/ongridrooftop/{imei}/ondemand/sub",
        "config_sub_template": "rtsg-1/ongridrooftop/{imei}/config/sub",
        "messagekey_sub_template": "rtsg-1/ongridrooftop/{imei}/messagekey/sub",
        "info_sub_template": "rtsg-1/ongridrooftop/{imei}/info/sub",
        "data_pub_template": "rtsg-1/ongridrooftop/{imei}/data/pub",
        "heartbeat_pub_template": "rtsg-1/ongridrooftop/{imei}/heartbeat/pub",
        "ondemand_pub_template": "rtsg-1/ongridrooftop/{imei}/ondemand/pub",
        "config_pub_template": "rtsg-1/ongridrooftop/{imei}/config/pub",
        "rtevent_pub_template": "rtsg-1/ongridrooftop/{imei}/rtevent/pub",
        "info_subscriptions": [
            "rtsg-1/ongridrooftop/866738083623411/data/pub",
            "rtsg-1/ongridrooftop/866738083623411/heartbeat/pub",
            "rtsg-1/ongridrooftop/866738083623411/ondemand/pub",
            "rtsg-1/ongridrooftop/866738083623411/config/pub",
            "rtsg-1/ongridrooftop/866738083623411/ondemand/sub",
            "rtsg-1/ongridrooftop/866738083623411/config/sub",
            "rtsg-1/ongridrooftop/866738083623411/messagekey/sub",
            "rtsg-1/ongridrooftop/866738083623411/info/sub",
            "rtsg-1/ongridrooftop/866738083623411/rtevent/pub",
            "rtsg-1/ongridrooftop/+/data/pub",
            "rtsg-1/ongridrooftop/+/heartbeat/pub",
            "rtsg-1/ongridrooftop/+/ondemand/pub",
            "rtsg-1/ongridrooftop/+/config/pub",
            "rtsg-1/ongridrooftop/+/rtevent/pub"
        ]
    },
    "settings": {
        "auto_poll": True,
        "poll_interval_seconds": 15,
        "response_timeout_seconds": 10,
        "payload_to_send": "asas"
    },
    "registered_devices": [
        {
            "imei": "866738083623411",
            "name": "Medha Ongrid Rooftop Solar Unit 1",
            "device_type": "ONGRID_ROOFTOP_SOLAR",
            "location": "RTSG Site 1",
            "enabled": True
        }
    ]
}


def load_yaml(filepath):
    if HAS_YAML:
        with open(filepath, "r", encoding="utf-8") as f:
            return yaml.safe_load(f)
    
    # Fallback YAML parser for basic structures when pyyaml is not yet installed
    with open(filepath, "r", encoding="utf-8") as f:
        lines = f.readlines()
    
    cfg = {"broker": {}, "topics": {"info_subscriptions": []}, "settings": {}, "registered_devices": []}
    curr_section = None
    curr_dev = None

    for line in lines:
        stripped = line.strip()
        if not stripped or stripped.startswith("#"):
            continue
        
        # Check top-level section
        if not line.startswith(" ") and not line.startswith("\t") and stripped.endswith(":"):
            curr_section = stripped[:-1].strip()
            continue
        
        if curr_section == "broker":
            if ":" in stripped:
                k, v = stripped.split(":", 1)
                k = k.strip()
                v = v.split("#")[0].strip().strip('"').strip("'")
                if v.isdigit():
                    cfg["broker"][k] = int(v)
                elif v.lower() in ["true", "false"]:
                    cfg["broker"][k] = v.lower() == "true"
                else:
                    cfg["broker"][k] = v
        elif curr_section == "topics":
            if stripped.startswith("-"):
                topic_val = stripped.lstrip("-").strip().strip('"').strip("'")
                if not isinstance(cfg["topics"].get("info_subscriptions"), list):
                    cfg["topics"]["info_subscriptions"] = []
                cfg["topics"]["info_subscriptions"].append(topic_val)
            elif ":" in stripped:
                k, v = stripped.split(":", 1)
                k = k.strip()
                v = v.split("#")[0].strip().strip('"').strip("'")
                if k == "info_subscriptions":
                    if not isinstance(cfg["topics"].get("info_subscriptions"), list):
                        cfg["topics"]["info_subscriptions"] = []
                else:
                    cfg["topics"][k] = v
        elif curr_section == "settings":
            if ":" in stripped:
                k, v = stripped.split(":", 1)
                k = k.strip()
                v = v.split("#")[0].strip().strip('"').strip("'")
                if v.isdigit():
                    cfg["settings"][k] = int(v)
                elif v.lower() in ["true", "false"]:
                    cfg["settings"][k] = v.lower() == "true"
                else:
                    cfg["settings"][k] = v
        elif curr_section == "registered_devices":
            if stripped.startswith("-"):
                curr_dev = {}
                cfg["registered_devices"].append(curr_dev)
                line_content = stripped.lstrip("-").strip()
                if ":" in line_content:
                    k, v = line_content.split(":", 1)
                    k = k.strip()
                    v = v.split("#")[0].strip().strip('"').strip("'")
                    curr_dev[k] = v
            elif curr_dev is not None and ":" in stripped:
                k, v = stripped.split(":", 1)
                k = k.strip()
                v = v.split("#")[0].strip().strip('"').strip("'")
                if v.lower() in ["true", "false"]:
                    curr_dev[k] = v.lower() == "true"
                else:
                    curr_dev[k] = v

    return cfg


def load_json(filepath):
    with open(filepath, "r", encoding="utf-8") as f:
        return json.load(f)


def load_xml(filepath):
    tree = ET.parse(filepath)
    root = tree.getroot()

    def get_text(node, tag, default=""):
        elem = node.find(tag)
        return elem.text.strip() if elem is not None and elem.text else default

    cfg = {"broker": {}, "topics": {"info_subscriptions": []}, "settings": {}, "registered_devices": []}
    b_node = root.find("broker")
    if b_node is not None:
        cfg["broker"]["name"] = get_text(b_node, "name", "MQTT Broker")
        cfg["broker"]["host"] = get_text(b_node, "host", "localhost")
        cfg["broker"]["port"] = int(get_text(b_node, "port", "1883"))
        cfg["broker"]["protocol"] = get_text(b_node, "protocol", "mqtt")
        cfg["broker"]["client_id"] = get_text(b_node, "client_id", "mqtt_client")
        cfg["broker"]["append_timestamp"] = get_text(b_node, "append_timestamp", "true").lower() == "true"
        cfg["broker"]["username"] = get_text(b_node, "username", "")
        cfg["broker"]["password"] = get_text(b_node, "password", "")
        cfg["broker"]["keepalive"] = int(get_text(b_node, "keepalive", "60"))
        cfg["broker"]["clean_session"] = get_text(b_node, "clean_session", "true").lower() == "true"
        cfg["broker"]["use_tls"] = get_text(b_node, "use_tls", "false").lower() == "true"

    t_node = root.find("topics")
    if t_node is not None:
        for child in t_node:
            if child.tag == "info_subscriptions":
                for top in child.findall("topic"):
                    if top.text:
                        cfg["topics"]["info_subscriptions"].append(top.text.strip())
            else:
                cfg["topics"][child.tag] = child.text.strip() if child.text else ""

    s_node = root.find("settings")
    if s_node is not None:
        cfg["settings"]["auto_poll"] = get_text(s_node, "auto_poll", "true").lower() == "true"
        cfg["settings"]["poll_interval_seconds"] = int(get_text(s_node, "poll_interval_seconds", "15"))
        cfg["settings"]["response_timeout_seconds"] = int(get_text(s_node, "response_timeout_seconds", "10"))
        cfg["settings"]["payload_to_send"] = get_text(s_node, "payload_to_send", "asas")

    rd_node = root.find("registered_devices")
    if rd_node is not None:
        for dev in rd_node.findall("device"):
            cfg["registered_devices"].append({
                "imei": get_text(dev, "imei", ""),
                "name": get_text(dev, "name", ""),
                "device_type": get_text(dev, "device_type", ""),
                "location": get_text(dev, "location", ""),
                "enabled": get_text(dev, "enabled", "true").lower() == "true"
            })
    return cfg


def load_config_file(filepath):
    ext = os.path.splitext(filepath)[1].lower()
    if ext in [".yaml", ".yml"]:
        return load_yaml(filepath)
    elif ext == ".json":
        return load_json(filepath)
    elif ext == ".xml":
        return load_xml(filepath)
    else:
        raise ValueError(f"Unsupported config extension: {ext}")


def custom_wizard():
    print("\n" + "=" * 70)
    print("           CUSTOM IMEI & HOST WIZARD")
    print("=" * 70)
    print("This wizard configures a custom device, generates all 9 MQTT topics,")
    print("and saves the settings to a clean JSON configuration file.\n")

    imei = input("Enter Target Device IMEI (e.g. 866738083623999): ").strip()
    if not imei:
        imei = "866738083623999"
        print(f"  -> Using default: {imei}")

    host = input("Enter Broker Host (default: iot.medha-res.com): ").strip()
    if not host:
        host = "iot.medha-res.com"

    port_in = input("Enter Broker Port (default: 8883): ").strip()
    port = int(port_in) if port_in else 8883

    tls_in = input("Enable TLS/SSL? (y/n, default: y): ").strip().lower()
    use_tls = tls_in != "n"

    username = input("Enter Username (default: InternalUser): ").strip()
    if not username:
        username = "InternalUser"

    password = getpass.getpass("Enter Password (leave empty if none): ")

    out_file = input(f"Destination JSON filename (default: config_{imei}.json): ").strip()
    if not out_file:
        out_file = f"config_{imei}.json"

    cfg = {
        "broker": {
            "name": f"Broker-{host}",
            "host": host,
            "port": port,
            "protocol": "mqtts" if use_tls else "mqtt",
            "client_id": "f915acbe-0d4e-4de2-9204-134295a904bc",
            "append_timestamp": True,
            "username": username,
            "password": password,
            "keepalive": 10,
            "clean_session": True,
            "use_tls": use_tls
        },
        "topics": {
            "ondemand_sub_template": f"rtsg-1/ongridrooftop/{imei}/ondemand/sub",
            "config_sub_template": f"rtsg-1/ongridrooftop/{imei}/config/sub",
            "messagekey_sub_template": f"rtsg-1/ongridrooftop/{imei}/messagekey/sub",
            "info_sub_template": f"rtsg-1/ongridrooftop/{imei}/info/sub",
            "data_pub_template": f"rtsg-1/ongridrooftop/{imei}/data/pub",
            "heartbeat_pub_template": f"rtsg-1/ongridrooftop/{imei}/heartbeat/pub",
            "ondemand_pub_template": f"rtsg-1/ongridrooftop/{imei}/ondemand/pub",
            "config_pub_template": f"rtsg-1/ongridrooftop/{imei}/config/pub",
            "rtevent_pub_template": f"rtsg-1/ongridrooftop/{imei}/rtevent/pub",
            "info_subscriptions": [
                f"rtsg-1/ongridrooftop/{imei}/data/pub",
                f"rtsg-1/ongridrooftop/{imei}/heartbeat/pub",
                f"rtsg-1/ongridrooftop/{imei}/ondemand/pub",
                f"rtsg-1/ongridrooftop/{imei}/config/pub",
                f"rtsg-1/ongridrooftop/{imei}/ondemand/sub",
                f"rtsg-1/ongridrooftop/{imei}/config/sub",
                f"rtsg-1/ongridrooftop/{imei}/messagekey/sub",
                f"rtsg-1/ongridrooftop/{imei}/info/sub",
                f"rtsg-1/ongridrooftop/{imei}/rtevent/pub",
                "rtsg-1/ongridrooftop/+/data/pub",
                "rtsg-1/ongridrooftop/+/heartbeat/pub",
                "rtsg-1/ongridrooftop/+/ondemand/pub",
                "rtsg-1/ongridrooftop/+/config/pub",
                "rtsg-1/ongridrooftop/+/rtevent/pub"
            ]
        },
        "settings": {
            "auto_poll": True,
            "poll_interval_seconds": 15,
            "response_timeout_seconds": 10,
            "payload_to_send": "asas"
        },
        "registered_devices": [
            {
                "imei": imei,
                "name": f"Device {imei}",
                "device_type": "ONGRID_ROOFTOP_SOLAR",
                "location": "Custom Site",
                "enabled": True
            }
        ]
    }

    with open(out_file, "w", encoding="utf-8") as f:
        json.dump(cfg, f, indent=2)

    print("\n" + "=" * 70)
    print(f"[+] Success: Custom configuration saved to '{out_file}'!")
    print(f"  * Configured IMEI : {imei}")
    print(f"  * Configured Host : {host}:{port}")
    print(f"  * Publish Topic   : rtsg-1/ongridrooftop/{imei}/ondemand/sub")
    print(f"  * Subscribe Topic : rtsg-1/ongridrooftop/{imei}/ondemand/pub")
    print(f"  * Total Info Subs : {len(cfg['topics']['info_subscriptions'])} topics")
    print("-" * 70)

    cont = input("Do you want to continue and run with this configuration? (yes/no): ").strip().lower()
    if cont in ["y", "yes"]:
        return cfg
    else:
        print(f"Saved. You can run it anytime with: python mqtt_app.py -c {out_file}")
        return None


def run_simulator(config):
    print("\n" + "=" * 80)
    print("       OFFLINE SIMULATOR MODE (No Live Server Required)")
    print("=" * 80)
    devs = config.get("registered_devices", [])
    if not devs:
        devs = [{"imei": "866738083623411", "name": "Simulated Solar Node", "device_type": "ONGRID_ROOFTOP_SOLAR", "location": "Lab"}]

    target = devs[0]
    imei = target.get("imei", "866738083623411")
    name = target.get("name", "Solar Node")
    sub_topic = f"rtsg-1/ongridrooftop/{imei}/ondemand/sub"
    pub_topic = f"rtsg-1/ongridrooftop/{imei}/ondemand/pub"
    payload = config.get("settings", {}).get("payload_to_send", "asas")

    print(f"Target Device : {name} (IMEI: {imei})")
    print(f"Simulating publish of '{payload}' to -> {sub_topic}")
    time.sleep(1)
    print(f"\n>>> [ONDEMAND FETCH REQUEST DISPATCHED] >>>")
    print(f"  Target Device : {name} (IMEI: {imei})")
    print(f"  Publish Topic : {sub_topic}")
    print(f"  Payload Sent  : {payload}")
    print(f"  Status        : Payload sent. Waiting for remote device response on '{pub_topic}'...")

    time.sleep(1.2)
    simulated_payload = {
        "MSGID": 3307,
        "CMKEY": 398962,
        "timestamp": datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M:%S"),
        "CMD": "read",
        "type": "ondemand",
        "imei": imei,
        "registers": {
            "3345": 208,
            "3365": 1,
            "3747": 935451,
            "3799": 18,
            "4013": 14181439,
            "4109": 18,
            "4113": 49
        }
    }

    print("\n" + "=" * 80)
    print(f"[REGISTERED DEVICE DATA RECEIVED] Topic: {pub_topic}")
    print(f"Device Name : {name}")
    print(f"Device IMEI : {imei} | Type: {target.get('device_type', 'N/A')} | Location: {target.get('location', 'N/A')}")
    print(f"Timestamp   : {simulated_payload['timestamp']} UTC | RTT: 642.1 ms")
    print("-" * 80)
    print("Parsed Payload Breakdown:")
    print(f"  Metadata  : MSGID: {simulated_payload['MSGID']}, CMKEY: {simulated_payload['CMKEY']}, CMD: {simulated_payload['CMD']}, type: {simulated_payload['type']}")
    print("  Registers / Metrics:")
    for reg, val in simulated_payload["registers"].items():
        print(f"    * Register [{reg}]: {val}")
    print("=" * 80)
    print("\nSimulator test completed successfully.")


def run_live_client(config, once=False, cli_password=None):
    if not HAS_PAHO:
        print("[!] Error: paho-mqtt package is not installed.")
        print("Please install dependencies: pip install -r requirements.txt")
        return

    broker = config.get("broker", {})
    host = broker.get("host", "iot.medha-res.com")
    port = broker.get("port", 8883)
    username = broker.get("username", "InternalUser")
    password = cli_password or broker.get("password", "")
    use_tls = broker.get("use_tls", True)
    keepalive = broker.get("keepalive", 10)
    clean_session = broker.get("clean_session", True)
    client_id_base = broker.get("client_id", "f915acbe-0d4e-4de2-9204-134295a904bc")

    if not password:
        password = getpass.getpass(f"Enter password for {username}@{host} (or press Enter to try unauthenticated): ")

    client_id = f"{client_id_base}_{int(time.time())}" if broker.get("append_timestamp", True) else client_id_base

    topics = config.get("topics", {})
    settings = config.get("settings", {})
    payload_to_send = settings.get("payload_to_send", "asas")
    devices = {d.get("imei"): d for d in config.get("registered_devices", [])}

    print("\n" + "=" * 80)
    print("     MEDHA SERVER ONGRID ROOFTOP MQTT REQUEST HANDLER & REGISTRY")
    print("=" * 80)
    print(f"Broker Endpoint: {host}:{port} (TLS: {use_tls})")
    print(f"MQTT Username  : {username}")
    print(f"KeepAlive      : {keepalive} seconds")
    print(f"Registered Devices Whitelist: {len(devices)} device(s)")
    for imei, d in devices.items():
        status = "ENABLED" if d.get("enabled", True) else "DISABLED"
        print(f"  * [{status}] IMEI: {imei} | {d.get('name', '')} ({d.get('device_type', '')})")
    print("=" * 80)

    # Initialize MQTT client
    try:
        # Paho v2 callback api support
        client = mqtt.Client(mqtt.CallbackAPIVersion.VERSION2, client_id=client_id, clean_session=clean_session)
    except AttributeError:
        # Paho v1 fallback
        client = mqtt.Client(client_id=client_id, clean_session=clean_session)

    if username:
        client.username_pw_set(username, password)

    if use_tls:
        context = ssl.create_default_context()
        context.check_hostname = False
        context.verify_mode = ssl.CERT_NONE
        client.tls_set_context(context)

    state = {
        "connected": False,
        "got_response": False,
        "last_dispatch_time": 0
    }

    def on_connect(cli, userdata, flags, rc, properties=None):
        rc_code = rc if isinstance(rc, int) else getattr(rc, "value", rc)
        if rc_code == 0:
            print("\n[+] Successfully connected to MQTT Broker!")
            state["connected"] = True
            # Subscribe to info subscriptions
            subs = topics.get("info_subscriptions", [])
            for s in subs:
                cli.subscribe(s, qos=0)
                print(f"  * Subscribed: {s}")
        else:
            print(f"[!] Connection failed with error code: {rc_code}")

    def on_message(cli, userdata, msg):
        topic = msg.topic
        payload_str = msg.payload.decode("utf-8", errors="ignore")
        rtt_str = ""
        if state["last_dispatch_time"] > 0:
            rtt = (time.time() - state["last_dispatch_time"]) * 1000
            rtt_str = f" | RTT: {rtt:.1f} ms"

        # Check matching registered device
        matched_dev = None
        for imei, d in devices.items():
            if imei in topic:
                matched_dev = d
                break

        print("\n" + "=" * 80)
        print(f"[REGISTERED DEVICE DATA RECEIVED] Topic: {topic}")
        if matched_dev:
            print(f"Device Name : {matched_dev.get('name', 'N/A')}")
            print(f"Device IMEI : {matched_dev.get('imei')} | Type: {matched_dev.get('device_type', 'N/A')} | Location: {matched_dev.get('location', 'N/A')}")
        print(f"Timestamp   : {datetime.now(timezone.utc).strftime('%Y-%m-%d %H:%M:%S')} UTC{rtt_str}")
        print("-" * 80)

        # Parse JSON or formatted string
        try:
            data = json.loads(payload_str)
            print("Parsed Payload Breakdown (JSON):")
            if isinstance(data, dict):
                registers = data.get("registers", {})
                for k, v in data.items():
                    if k != "registers":
                        print(f"  {k}: {v}")
                if registers:
                    print("  Registers / Metrics:")
                    for reg, val in registers.items():
                        print(f"    * Register [{reg}]: {val}")
            else:
                print(json.dumps(data, indent=2))
        except Exception:
            print("Raw Payload Content:")
            print(f"  {payload_str}")
        print("=" * 80)
        state["got_response"] = True

    client.on_connect = on_connect
    client.on_message = on_message

    try:
        print(f"\n[*] Connecting to {host}:{port} ...")
        client.connect(host, port, keepalive)
        client.loop_start()

        # Wait for connection
        t0 = time.time()
        while not state["connected"] and (time.time() - t0) < 8:
            time.sleep(0.2)

        if not state["connected"]:
            print("[!] Connection timeout. Check your network or credentials.")
            client.loop_stop()
            return

        # Dispatch ondemand requests to enabled registered devices
        target_imeis = [imei for imei, d in devices.items() if d.get("enabled", True)]
        if not target_imeis:
            target_imeis = ["866738083623411"]

        for imei in target_imeis:
            sub_template = topics.get("ondemand_sub_template", "rtsg-1/ongridrooftop/{imei}/ondemand/sub")
            target_topic = sub_template.format(imei=imei)
            print("\n>>> [ONDEMAND FETCH REQUEST DISPATCHED] >>>")
            dev_name = devices.get(imei, {}).get("name", "Unknown Device")
            print(f"  Target Device : {dev_name} (IMEI: {imei})")
            print(f"  Publish Topic : {target_topic}")
            print(f"  Payload Sent  : {payload_to_send}")
            print(f"  Status        : Payload sent. Waiting for remote device response on '.../ondemand/pub'...")
            state["last_dispatch_time"] = time.time()
            client.publish(target_topic, payload_to_send, qos=0)

        # Loop
        if once:
            timeout = settings.get("response_timeout_seconds", 10)
            wait_start = time.time()
            while not state["got_response"] and (time.time() - wait_start) < timeout:
                time.sleep(0.5)
            if not state["got_response"]:
                print(f"[!] No response received within {timeout}s.")
        else:
            print("\n[+] Listening for incoming device payloads. Press Ctrl+C to stop.\n")
            poll_interval = settings.get("poll_interval_seconds", 15)
            last_poll = time.time()
            while True:
                time.sleep(1)
                if settings.get("auto_poll", True) and (time.time() - last_poll) >= poll_interval:
                    for imei in target_imeis:
                        target_topic = topics.get("ondemand_sub_template", "rtsg-1/ongridrooftop/{imei}/ondemand/sub").format(imei=imei)
                        client.publish(target_topic, payload_to_send, qos=0)
                    last_poll = time.time()

    except KeyboardInterrupt:
        print("\n[*] Stopping listener...")
    finally:
        client.loop_stop()
        client.disconnect()
        print("[*] Disconnected.")


def main_menu():
    while True:
        print("\n" + "=" * 80)
        print("              MQTT REMOTE DEVICE CONTROLLER - MAIN SELECTION MENU")
        print("=" * 80)
        print("\nPlease select a Configuration File or Action:\n")
        print("  [1] config.yaml                  (Default Medha Server YAML Config - 9 Topics)")
        print("  [2] config.xml                   (Medha Server XML Configuration)")
        print("  [3] custom_device_example.json   (Custom JSON Configuration)")
        print("  [4] Custom IMEI & Host Wizard    (Input custom IMEI & Host, save to JSON, then continue)")
        print("  [5] Offline Simulator Mode       (Test without connecting to live broker)")
        print("  [6] Exit\n")
        print("-" * 80)

        choice = input("Enter your choice (1-6): ").strip()
        if choice == "1":
            cfg_path = "config.yaml"
            if not os.path.exists(cfg_path):
                print(f"[!] {cfg_path} not found. Using defaults.")
                cfg = DEFAULT_CONFIG
            else:
                cfg = load_config_file(cfg_path)
            run_live_client(cfg)
        elif choice == "2":
            cfg_path = "config.xml"
            if not os.path.exists(cfg_path):
                print(f"[!] {cfg_path} not found.")
                continue
            cfg = load_config_file(cfg_path)
            run_live_client(cfg)
        elif choice == "3":
            # Search for available json configs
            json_files = glob.glob("*.json")
            if not json_files:
                print("[!] No JSON configuration files found in folder.")
                continue
            print("\nAvailable JSON Configurations:")
            for idx, jf in enumerate(json_files, 1):
                print(f"  [{idx}] {jf}")
            j_choice = input(f"Select file (1-{len(json_files)}): ").strip()
            try:
                sel_idx = int(j_choice) - 1
                if 0 <= sel_idx < len(json_files):
                    cfg = load_config_file(json_files[sel_idx])
                    run_live_client(cfg)
                else:
                    print("[!] Invalid index.")
            except ValueError:
                print("[!] Invalid input.")
        elif choice == "4":
            cfg = custom_wizard()
            if cfg:
                run_live_client(cfg)
        elif choice == "5":
            cfg_path = "config.yaml"
            cfg = load_config_file(cfg_path) if os.path.exists(cfg_path) else DEFAULT_CONFIG
            run_simulator(cfg)
        elif choice == "6":
            print("\nExiting MQTT Remote Device Controller. Goodbye!")
            sys.exit(0)
        else:
            print("\n[!] Invalid selection. Please enter a number between 1 and 6.")


def main():
    parser = argparse.ArgumentParser(description="MQTT Remote Device Request Handler & Controller")
    parser.add_argument("-c", "--config", help="Path to config file (.yaml, .xml, .json)")
    parser.add_argument("--wizard", action="store_true", help="Launch Custom IMEI & Host Wizard directly")
    parser.add_argument("--simulate", action="store_true", help="Run in offline simulation mode")
    parser.add_argument("--once", action="store_true", help="Fetch once and exit")
    parser.add_argument("--password", help="Broker password")
    args = parser.parse_args()

    if args.simulate:
        cfg = load_config_file(args.config) if args.config else DEFAULT_CONFIG
        run_simulator(cfg)
    elif args.wizard:
        cfg = custom_wizard()
        if cfg:
            run_live_client(cfg, once=args.once, cli_password=args.password)
    elif args.config:
        cfg = load_config_file(args.config)
        run_live_client(cfg, once=args.once, cli_password=args.password)
    else:
        main_menu()


if __name__ == "__main__":
    main()
