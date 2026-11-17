#!/usr/bin/env python3
"""
================================================================================
                    MQTT SCADA & RTEVENT SERVER CONTROLLER
================================================================================
Comprehensive MQTT IoT Controller & Telemetry Handler:
  - Subscribes to target device using 'rtsg-1/ongridrooftop/{imei}/#'
  - Captures 100% of packets from target device (exactly like in MQTTBox)
  - Displays compact 1-line telemetry for 'rtevent' (voltage, frequency, power)
  - Full detailed breakdown for 'ondemand' and 'data' responses
  - Interactive CLI: Press [Enter] anytime to dispatch ondemand request
  - Tkinter GUI with dedicated 'Send Ondemand Request' button & Live Response Viewer
  - Option 5: Lists all config files in the device cmd line (Run / View / Open)
  - Auto-saved credentials in server_credentials.json (1-time password entry)
  - Full MQTT v3.1.1 & MQTTS TLS support
"""

import sys
import os
import time
import json
import ssl
import csv
import glob
import argparse
import getpass
import threading
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

try:
    from modbus_registers import (
        ALL_REGISTERS,
        SECTIONS,
        search_registers,
        get_gprs_registers,
        get_registers_by_section,
        build_ondemand_payload
    )
except ImportError:
    ALL_REGISTERS = []
    SECTIONS = [
        "1. GPRS_Connection",
        "2. SPIFFS_Storage",
        "3. Restart_Count",
        "4. Solar_Power",
        "5. Meters_DLMS",
        "6. Control_Relays",
        "7. System_RTC",
        "8. All_Registers"
    ]
    search_registers = lambda q="", s="8. All_Registers": []
    get_gprs_registers = lambda: []
    get_registers_by_section = lambda s: []
    build_ondemand_payload = lambda n, v, c="155521", p="438266", cmd="read": {}

# Live Handshake Keys captured from device
LIVE_KEYS = {
    "CMKEY": "155521",
    "PMKEY": "438266"
}

# File Paths
CREDENTIALS_FILE = "server_credentials.json"
HISTORY_FILE = "connection_history.json"
RTEVENT_CSV_LOG = "rtevent_logs.csv"
RTEVENT_TXT_LOG = "rtevent_logs.txt"

DEFAULT_CONFIG = {
    "broker": {
        "name": "866738083619898",
        "host": "rms.iotscada-pmsg.com",
        "port": 8883,
        "protocol": "mqtts",
        "mqtt_version": "3.1.1",
        "client_id": "84e738ec-179a-4546-88af-cc3ba679d08d",
        "append_timestamp": False,
        "clean_session": False,
        "username": "test",
        "password": "",
        "keepalive": 10,
        "connect_timeout": 30,
        "reconnect_period_ms": 1000,
        "use_tls": True,
        "ssl_tls_version": "Auto",
        "ssl_cert_type": "CA signed server certificate",
        "queue_qos_zero": True,
        "reschedule_pings": False
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
            "rtsg-1/ongridrooftop/866738083619898/#",
            "rtsg-1/ongridrooftop/866738083619898/ondemand/pub",
            "rtsg-1/ongridrooftop/866738083619898/data/pub",
            "rtsg-1/ongridrooftop/866738083619898/heartbeat/pub",
            "rtsg-1/ongridrooftop/866738083619898/config/pub",
            "rtsg-1/ongridrooftop/866738083619898/rtevent/pub",
            "rtsg-1/ongridrooftop/866738083619898/ondemand/sub",
            "rtsg-1/ongridrooftop/866738083619898/config/sub",
            "rtsg-1/ongridrooftop/866738083619898/messagekey/sub",
            "rtsg-1/ongridrooftop/866738083619898/info/sub"
        ]
    },
    "settings": {
        "auto_poll": False,
        "poll_interval_seconds": 15,
        "response_timeout_seconds": 30,
        "payload_to_send": "asas",
        "auto_reply_messagekey": True,
        "target_imei_only": True,
        "rtevent_display_mode": "compact"
    },
    "registered_devices": [
        {
            "imei": "866738083619898",
            "name": "Rooftop Solar Unit 866738083619898",
            "device_type": "ONGRID_ROOFTOP_SOLAR",
            "location": "Site Main",
            "enabled": True
        }
    ]
}


# ==============================================================================
#                  AUTOMATIC CREDENTIAL PERSISTENCE
# ==============================================================================

def load_server_credentials():
    """Loads saved server credentials from JSON."""
    if os.path.exists(CREDENTIALS_FILE):
        try:
            with open(CREDENTIALS_FILE, "r", encoding="utf-8") as f:
                return json.load(f)
        except Exception:
            pass
    return {}


def save_server_credential(host, username, password, port=8883, client_id=""):
    """Automatically saves host and credentials into JSON file."""
    if not password:
        return
    creds = load_server_credentials()
    key = f"{username}@{host}:{port}"
    creds[key] = {
        "host": host,
        "port": port,
        "username": username,
        "password": password,
        "client_id": client_id,
        "updated_at": datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M:%S UTC")
    }
    creds[host] = {
        "host": host,
        "port": port,
        "username": username,
        "password": password,
        "client_id": client_id,
        "updated_at": datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M:%S UTC")
    }
    try:
        with open(CREDENTIALS_FILE, "w", encoding="utf-8") as f:
            json.dump(creds, f, indent=2)
    except Exception as e:
        print(f"[!] Warning: Could not save credentials to {CREDENTIALS_FILE}: {e}")


def get_saved_password(host, username="", port=8883):
    """Retrieves saved password for a host/user if available."""
    creds = load_server_credentials()
    key = f"{username}@{host}:{port}"
    if key in creds and creds[key].get("password"):
        return creds[key]["password"]
    if host in creds and creds[host].get("password"):
        return creds[host]["password"]
    return ""


# ==============================================================================
#                  RTEVENT EXCEL (CSV) & TEXT LOGGING
# ==============================================================================

CSV_HEADERS = [
    "Log_Timestamp_UTC",
    "Topic",
    "IMEI",
    "Device_Timestamp",
    "Voltage_VN",
    "Frequency_FREQ",
    "Power_POW",
    "Reactive_Power_RPOW",
    "CMKEY",
    "PMKEY",
    "INDEX",
    "STINTERVAL",
    "VD",
    "Raw_JSON"
]


def init_rtevent_csv():
    """Initializes CSV header if file does not exist."""
    if not os.path.exists(RTEVENT_CSV_LOG):
        try:
            with open(RTEVENT_CSV_LOG, "w", newline="", encoding="utf-8") as f:
                writer = csv.writer(f)
                writer.writerow(CSV_HEADERS)
        except Exception as e:
            print(f"[!] Could not init {RTEVENT_CSV_LOG}: {e}")


def log_rtevent_data(topic, payload_str, data_dict=None):
    """Appends an incoming 'rtevent' record to rtevent_logs.csv and rtevent_logs.txt."""
    now_utc = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M:%S")

    d = data_dict or {}
    imei = str(d.get("IMEI", "") or "")
    if not imei:
        parts = topic.split("/")
        if len(parts) >= 3:
            imei = parts[2]

    dev_ts = str(d.get("TIMESTAMP", "") or d.get("DATE", "") or "")
    vn = d.get("IS-1-0---VN", "")
    freq = d.get("IS-1-0---FREQ", "")
    pow_w = d.get("IS-1-0---POW", "")
    rpow = d.get("IS-1-0---RPOW", "")
    cmkey = d.get("CMKEY", "")
    pmkey = d.get("PMKEY", "")
    idx = d.get("INDEX", "")
    stinterval = d.get("STINTERVAL", "")
    vd = d.get("VD", "")

    init_rtevent_csv()
    try:
        with open(RTEVENT_CSV_LOG, "a", newline="", encoding="utf-8") as f:
            writer = csv.writer(f)
            writer.writerow([
                now_utc,
                topic,
                imei,
                dev_ts,
                vn,
                freq,
                pow_w,
                rpow,
                cmkey,
                pmkey,
                idx,
                stinterval,
                vd,
                payload_str
            ])
    except Exception as e:
        print(f"[!] Error writing to {RTEVENT_CSV_LOG}: {e}")

    try:
        with open(RTEVENT_TXT_LOG, "a", encoding="utf-8") as f:
            f.write(f"[{now_utc} UTC] Topic: {topic}\n")
            f.write(f"  IMEI: {imei} | Timestamp: {dev_ts}\n")
            f.write(f"  Voltage: {vn} V | Frequency: {freq} Hz | Power: {pow_w} W | RPower: {rpow} VAR\n")
            f.write(f"  INDEX: {idx} | CMKEY: {cmkey} | PMKEY: {pmkey} | STINTERVAL: {stinterval}\n")
            f.write(f"  Payload: {payload_str}\n")
            f.write("-" * 80 + "\n")
    except Exception as e:
        print(f"[!] Error writing to {RTEVENT_TXT_LOG}: {e}")


# ==============================================================================
#                  CONNECTION HISTORY & CONFIG LOADERS
# ==============================================================================

def load_connection_history():
    """Loads connection history from JSON file or initializes with default connection #1."""
    if os.path.exists(HISTORY_FILE):
        try:
            with open(HISTORY_FILE, "r", encoding="utf-8") as f:
                history = json.load(f)
                if isinstance(history, list) and len(history) > 0:
                    return history
        except Exception:
            pass

    initial_history = [
        {
            "connection_num": 1,
            "name": "RMS IoT SCADA (866738083619898)",
            "host": "rms.iotscada-pmsg.com",
            "port": 8883,
            "use_tls": True,
            "username": "test",
            "imei": "866738083619898",
            "timestamp": datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M:%S UTC"),
            "config": DEFAULT_CONFIG
        }
    ]
    save_connection_history(initial_history)
    return initial_history


def save_connection_history(history):
    """Saves connection history list to JSON file."""
    try:
        with open(HISTORY_FILE, "w", encoding="utf-8") as f:
            json.dump(history, f, indent=2)
    except Exception as e:
        print(f"[!] Warning: Could not save connection history: {e}")


def add_to_connection_history(name, host, port, use_tls, username, imei, config):
    """Adds a new connection record to history and returns the updated history and entry."""
    history = load_connection_history()
    next_num = len(history) + 1
    new_entry = {
        "connection_num": next_num,
        "name": name or f"Connection #{next_num} ({host})",
        "host": host,
        "port": port,
        "use_tls": use_tls,
        "username": username,
        "imei": imei,
        "timestamp": datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M:%S UTC"),
        "config": config
    }
    history.append(new_entry)
    save_connection_history(history)
    return history, new_entry


def print_previous_connections(history):
    """Lists all previous connections formatted with their connection numbers."""
    print("\n" + "=" * 80)
    print("                    PREVIOUS SAVED CONNECTIONS")
    print("=" * 80)
    for item in history:
        c_num = item.get("connection_num", 1)
        c_name = item.get("name", "Unnamed Connection")
        host = item.get("host", "N/A")
        port = item.get("port", "N/A")
        tls = item.get("use_tls", False)
        imei = item.get("imei", "N/A")
        user = item.get("username", "None")
        ts = item.get("timestamp", "N/A")
        topic_count = len(item.get("config", {}).get("topics", {}).get("info_subscriptions", []))

        print(f"  [Connection #{c_num}] {c_name}")
        print(f"    * Endpoint    : {host}:{port} (TLS: {tls})")
        print(f"    * Device IMEI : {imei}")
        print(f"    * Username    : {user}")
        print(f"    * Topics      : {topic_count} subscription topic(s)")
        print(f"    * Saved Date  : {ts}")
        print("-" * 80)


def generate_single_imei_topics(imei):
    """Generates subscription topics for a SINGLE IMEI including device-level wildcard #."""
    subs = [
        f"rtsg-1/ongridrooftop/{imei}/#",
        f"rtsg-1/ongridrooftop/{imei}/ondemand/pub",
        f"rtsg-1/ongridrooftop/{imei}/data/pub",
        f"rtsg-1/ongridrooftop/{imei}/heartbeat/pub",
        f"rtsg-1/ongridrooftop/{imei}/config/pub",
        f"rtsg-1/ongridrooftop/{imei}/rtevent/pub",
        f"rtsg-1/ongridrooftop/{imei}/ondemand/sub",
        f"rtsg-1/ongridrooftop/{imei}/config/sub",
        f"rtsg-1/ongridrooftop/{imei}/messagekey/sub",
        f"rtsg-1/ongridrooftop/{imei}/info/sub"
    ]

    return {
        "ondemand_sub_template": f"rtsg-1/ongridrooftop/{imei}/ondemand/sub",
        "config_sub_template": f"rtsg-1/ongridrooftop/{imei}/config/sub",
        "messagekey_sub_template": f"rtsg-1/ongridrooftop/{imei}/messagekey/sub",
        "info_sub_template": f"rtsg-1/ongridrooftop/{imei}/info/sub",
        "data_pub_template": f"rtsg-1/ongridrooftop/{imei}/data/pub",
        "heartbeat_pub_template": f"rtsg-1/ongridrooftop/{imei}/heartbeat/pub",
        "ondemand_pub_template": f"rtsg-1/ongridrooftop/{imei}/ondemand/pub",
        "config_pub_template": f"rtsg-1/ongridrooftop/{imei}/config/pub",
        "rtevent_pub_template": f"rtsg-1/ongridrooftop/{imei}/rtevent/pub",
        "info_subscriptions": subs
    }


def load_yaml(filepath):
    if HAS_YAML:
        with open(filepath, "r", encoding="utf-8") as f:
            return yaml.safe_load(f)

    with open(filepath, "r", encoding="utf-8") as f:
        lines = f.readlines()

    cfg = {"broker": {}, "topics": {"info_subscriptions": []}, "settings": {}, "registered_devices": []}
    curr_section = None
    curr_dev = None

    for line in lines:
        stripped = line.strip()
        if not stripped or stripped.startswith("#"):
            continue

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
        cfg["broker"]["host"] = get_text(b_node, "host", "rms.iotscada-pmsg.com")
        cfg["broker"]["port"] = int(get_text(b_node, "port", "8883"))
        cfg["broker"]["protocol"] = get_text(b_node, "protocol", "mqtts")
        cfg["broker"]["client_id"] = get_text(b_node, "client_id", "84e738ec-179a-4546-88af-cc3ba679d08d")
        cfg["broker"]["append_timestamp"] = get_text(b_node, "append_timestamp", "false").lower() == "true"
        cfg["broker"]["username"] = get_text(b_node, "username", "test")
        cfg["broker"]["password"] = get_text(b_node, "password", "")
        cfg["broker"]["keepalive"] = int(get_text(b_node, "keepalive", "10"))
        cfg["broker"]["clean_session"] = get_text(b_node, "clean_session", "false").lower() == "true"
        cfg["broker"]["use_tls"] = get_text(b_node, "use_tls", "true").lower() == "true"

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
        cfg["settings"]["response_timeout_seconds"] = int(get_text(s_node, "response_timeout_seconds", "30"))
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


# ==============================================================================
#                  CORE LIVE CLIENT (MQTTS & TARGET IMEI FILTER)
# ==============================================================================

def run_live_client(config, once=False, cli_password=None, on_message_callback=None, stop_event=None, on_client_ready=None):
    """
    Connects to MQTT Broker with TLS and MQTT v3.1.1 protocol.
    Subscribes to target device using '#', capturing 100% of telemetry and ondemand data.
    Provides interactive terminal dispatch so pressing [Enter] publishes ondemand requests.
    """
    if not HAS_PAHO:
        print("[!] Error: paho-mqtt package is not installed.")
        print("Please install dependencies: pip install -r requirements.txt")
        return

    broker = config.get("broker", {})
    host = broker.get("host", "rms.iotscada-pmsg.com")
    port = int(broker.get("port", 8883))
    username = broker.get("username", "test")
    use_tls = broker.get("use_tls", True)
    keepalive = int(broker.get("keepalive", 10))
    clean_session = bool(broker.get("clean_session", False))
    client_id_base = broker.get("client_id", "84e738ec-179a-4546-88af-cc3ba679d08d")
    append_ts = bool(broker.get("append_timestamp", False))
    connect_timeout = int(broker.get("connect_timeout", 30))

    settings = config.get("settings", {})
    payload_to_send = settings.get("payload_to_send", "asas")
    target_imei_only = bool(settings.get("target_imei_only", True))
    rtevent_mode = settings.get("rtevent_display_mode", "compact").lower()

    devices = {str(d.get("imei")): d for d in config.get("registered_devices", [])}
    target_imei_list = list(devices.keys())
    if not target_imei_list:
        target_imei_list = [str(broker.get("name", "866738083619898"))]

    primary_imei = target_imei_list[0]

    password = cli_password or broker.get("password", "")
    if not password:
        password = get_saved_password(host, username, port)

    if not password and sys.stdin.isatty():
        password = getpass.getpass(f"Enter password for {username}@{host} (saved automatically): ")

    if password:
        save_server_credential(host, username, password, port, client_id_base)

    client_id = f"{client_id_base}_{int(time.time())}" if append_ts else client_id_base

    topics = config.get("topics", {})
    raw_subs = topics.get("info_subscriptions", [])

    # Filter subscriptions: remove global wildcards (+), keep device-level wildcard (#)
    clean_subs = []
    for s in raw_subs:
        if "+" in s:
            continue
        if s not in clean_subs:
            clean_subs.append(s)

    # Ensure device-level wildcard for target IMEI is included
    device_wildcard = f"rtsg-1/ongridrooftop/{primary_imei}/#"
    if device_wildcard not in clean_subs:
        clean_subs.insert(0, device_wildcard)

    print("\n" + "=" * 80)
    print("       MQTT SCADA & ONDEMAND CONTROLLER")
    print("=" * 80)
    print(f"Broker Endpoint   : {host}:{port} (TLS: {use_tls})")
    print(f"MQTT Client ID    : {client_id}")
    print(f"MQTT Username     : {username}")
    print(f"Target Device IMEI: {primary_imei} (Device-Scoped Wildcard: Enabled)")
    print(f"Telemetry Mode    : {rtevent_mode.upper()} (Auto-logged to rtevent_logs.csv)")
    print(f"Subscribed Topics ({len(clean_subs)} topics):")
    for s in clean_subs:
        print(f"  * {s}")
    print("=" * 80)

    try:
        client = mqtt.Client(
            callback_api_version=mqtt.CallbackAPIVersion.VERSION2,
            client_id=client_id,
            clean_session=clean_session,
            protocol=mqtt.MQTTv311
        )
    except (TypeError, AttributeError):
        try:
            client = mqtt.Client(
                mqtt.CallbackAPIVersion.VERSION2,
                client_id=client_id,
                clean_session=clean_session,
                protocol=mqtt.MQTTv311
            )
        except (TypeError, AttributeError):
            client = mqtt.Client(client_id=client_id, clean_session=clean_session, protocol=mqtt.MQTTv311)

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
            for s in clean_subs:
                cli.subscribe(s, qos=0)
        else:
            err_reasons = {
                1: "Connection refused: Incorrect protocol version",
                2: "Connection refused: Identifier rejected",
                3: "Connection refused: Server unavailable",
                4: "Connection refused: Bad username or password",
                5: "Connection refused: Not authorized",
                134: "Connection refused (0x86 / 134): Bad username, password, or unauthorized Client ID",
                135: "Connection refused (0x87 / 135): Not authorized"
            }
            err_desc = err_reasons.get(rc_code, f"Error Code {rc_code}")
            print(f"\n[!] Connection failed: {err_desc}")

    def on_message(cli, userdata, msg):
        topic = msg.topic
        payload_str = msg.payload.decode("utf-8", errors="ignore")
        rtt_str = ""
        if state["last_dispatch_time"] > 0:
            rtt = (time.time() - state["last_dispatch_time"]) * 1000
            rtt_str = f" | RTT: {rtt:.1f} ms"

        # Check if topic belongs to target IMEI
        is_for_target = any(imei in topic for imei in target_imei_list if imei)
        if target_imei_only and not is_for_target:
            return

        parsed_dict = None
        try:
            parsed_dict = json.loads(payload_str)
        except Exception:
            pass

        now_utc = datetime.now(timezone.utc).strftime("%H:%M:%S")
        is_rtevent = "rtevent" in topic.lower() or (parsed_dict and "rtevent" in str(parsed_dict).lower())

        if is_rtevent:
            # 1. Log to Excel/CSV in the background
            log_rtevent_data(topic, payload_str, parsed_dict)

            # 2. Console display
            if rtevent_mode == "compact":
                d = parsed_dict or {}
                vn = d.get("IS-1-0---VN", "N/A")
                freq = d.get("IS-1-0---FREQ", "N/A")
                pow_w = d.get("IS-1-0---POW", "N/A")
                idx = d.get("INDEX", "N/A")
                dev_ts = d.get("TIMESTAMP", d.get("DATE", now_utc))
                print(f"[{now_utc}] [LIVE TELEMETRY] IMEI: {primary_imei} | VN: {vn}V | FREQ: {freq}Hz | POW: {pow_w}W | INDEX: {idx} | DevTime: {dev_ts}")
            elif rtevent_mode == "full":
                print("\n" + "=" * 80)
                print(f"[RTEVENT TELEMETRY] Topic: {topic} | Time: {now_utc} UTC")
                print("-" * 80)
                if parsed_dict:
                    for k, v in parsed_dict.items():
                        print(f"  {k:15}: {v}")
                else:
                    print(f"  {payload_str}")
                print("=" * 80)

        elif "messagekey" in topic.lower():
            print("\n" + "=" * 80)
            print(f"[DEVICE MESSAGEKEY RECEIVED] Topic: {topic}")
            if parsed_dict:
                cm = str(parsed_dict.get("CMKEY", "") or "")
                pm = str(parsed_dict.get("PMKEY", "") or "")
                if cm:
                    LIVE_KEYS["CMKEY"] = cm
                if pm:
                    LIVE_KEYS["PMKEY"] = pm
                print(f"  CMKEY    : {cm or parsed_dict.get('CMKEY')}")
                print(f"  PMKEY    : {pm or parsed_dict.get('PMKEY')}")
                print(f"  Timestamp: {parsed_dict.get('timestamp')}")
            else:
                print(f"  Payload  : {payload_str}")
            print(f"  -> Device '{primary_imei}' is online and active!")

            # Auto-Dispatch ondemand trigger if configured (default True)
            auto_reply_messagekey = settings.get("auto_reply_messagekey", True)
            if auto_reply_messagekey:
                print(f">>> [AUTO-DISPATCH ONDEMAND] Handshake key received -> Sending '{payload_to_send}' to {target_topic} ...")
                state["last_dispatch_time"] = time.time()
                cli.publish(target_topic, payload_to_send, qos=0)
            print("=" * 80)

        else:
            # Ondemand, Data, Heartbeat, or other response
            print("\n" + "=" * 80)
            badge = "[ONDEMAND DATA RECEIVED]" if "ondemand" in topic.lower() else "[DEVICE DATA RECEIVED]"
            print(f"{badge} Topic: {topic}")
            print(f"Timestamp : {datetime.now(timezone.utc).strftime('%Y-%m-%d %H:%M:%S')} UTC{rtt_str}")
            print("-" * 80)

            if parsed_dict and isinstance(parsed_dict, dict):
                print("Parsed Payload Breakdown (JSON):")
                for k, v in parsed_dict.items():
                    if k != "registers":
                        print(f"  {k:15}: {v}")
                if "registers" in parsed_dict:
                    print("  Registers / Metrics:")
                    for reg, val in parsed_dict["registers"].items():
                        print(f"    * Register [{reg}]: {val}")
            else:
                print("Raw Payload Content:")
                print(f"  {payload_str}")
            print("=" * 80)

        state["got_response"] = True

        if on_message_callback:
            try:
                on_message_callback(topic, payload_str, parsed_dict, is_rtevent)
            except Exception:
                pass

    sub_template = topics.get("ondemand_sub_template", f"rtsg-1/ongridrooftop/{primary_imei}/ondemand/sub")
    target_topic = sub_template.format(imei=primary_imei) if "{imei}" in sub_template else sub_template

    client.on_connect = on_connect
    client.on_message = on_message

    def on_disconnect(cli, userdata, *args):
        state["connected"] = False
        rc = args[1] if len(args) > 1 else (args[0] if args else 0)
        rc_code = rc if isinstance(rc, int) else getattr(rc, "value", rc)
        now_utc = datetime.now(timezone.utc).strftime("%H:%M:%S")
        if rc_code != 0:
            print(f"\n[!] [{now_utc} UTC] Disconnected from broker (Reason Code: {rc_code})")
            print("=" * 80)
            print("⚠️  WARNING: BROKER TERMINATED CONNECTION!")
            print(f"  Configured Client ID: '{client_id}'")
            print("  The MQTT broker allows only ONE active connection per Client ID.")
            print("  If MQTTBox is currently connected with this Client ID,")
            print("  the broker automatically kicks Python offline!")
            print("  👉 SOLUTION: Close or disconnect MQTTBox while running Python,")
            print("     OR set append_timestamp: true in config.yaml to allow simultaneous connections.")
            print("=" * 80 + "\n")

    client.on_disconnect = on_disconnect

    try:
        print(f"\n[*] Connecting to {host}:{port} (timeout: {connect_timeout}s) ...")
        client.connect(host, port, keepalive)
        client.loop_start()

        t0 = time.time()
        while not state["connected"] and (time.time() - t0) < connect_timeout:
            if stop_event and stop_event.is_set():
                break
            time.sleep(0.3)

        if not state["connected"]:
            print(f"[!] Connection timeout after {connect_timeout}s. Check network or credentials.")
            client.loop_stop()
            return

        if on_client_ready:
            on_client_ready(client)

        # Initial dispatch
        print(f"\n>>> [DISPATCHING INITIAL ONDEMAND FETCH] >>>")
        print(f"  Publish Topic : {target_topic}")
        print(f"  Payload Sent  : {payload_to_send}")
        state["last_dispatch_time"] = time.time()
        client.publish(target_topic, payload_to_send, qos=0)

        if once:
            timeout = settings.get("response_timeout_seconds", 30)
            wait_start = time.time()
            while not state["got_response"] and (time.time() - wait_start) < timeout:
                time.sleep(0.5)
        else:
            print(f"\n[+] Listening for target IMEI '{primary_imei}'.")
            print("--------------------------------------------------------------------------------")
            print("  [KEYBOARD SHORTCUT] Press [Enter] anytime to send Ondemand request ('asas')")
            print("  Type 'q' and press [Enter] to stop and disconnect.")
            print("--------------------------------------------------------------------------------\n")

            poll_interval = settings.get("poll_interval_seconds", 15)
            last_poll = time.time()

            # Interactive keyboard trigger thread
            def cli_input_worker():
                while not (stop_event and stop_event.is_set()):
                    try:
                        line = sys.stdin.readline()
                        if not line:
                            break
                        cmd = line.strip()
                        if cmd.lower() in ["q", "quit", "exit"]:
                            if stop_event:
                                stop_event.set()
                            break
                        else:
                            pay = cmd if cmd else payload_to_send
                            print(f"\n>>> [MANUAL ONDEMAND DISPATCH] >>> Topic: {target_topic} | Payload: '{pay}'")
                            state["last_dispatch_time"] = time.time()
                            client.publish(target_topic, pay, qos=0)
                    except Exception:
                        break

            if sys.stdin.isatty():
                in_thread = threading.Thread(target=cli_input_worker, daemon=True)
                in_thread.start()

            while True:
                if stop_event and stop_event.is_set():
                    break
                time.sleep(0.5)
                if settings.get("auto_poll", False) and (time.time() - last_poll) >= poll_interval:
                    client.publish(target_topic, payload_to_send, qos=0)
                    last_poll = time.time()

    except KeyboardInterrupt:
        print("\n[*] Stopping listener...")
    finally:
        client.loop_stop()
        client.disconnect()
        print("[*] Disconnected.")


# ==============================================================================
#                  TKINTER GUI APPLICATION WITH ONDEMAND BUTTON & VIEWER
# ==============================================================================

def launch_gui(initial_config=None):
    """Launches the Tkinter Graphical Interface."""
    try:
        import tkinter as tk
        from tkinter import ttk, messagebox, scrolledtext
    except ImportError:
        print("[!] Error: Tkinter is not installed on this system.")
        return

    root = tk.Tk()
    root.title("MQTT SCADA & Ondemand Controller")
    root.geometry("1100x740")
    root.minsize(920, 620)

    style = ttk.Style()
    style.theme_use("clam")

    current_config = initial_config or DEFAULT_CONFIG
    broker_cfg = current_config.get("broker", {})

    client_thread = None
    stop_event = threading.Event()
    is_connected = False
    active_client = None

    # Top Header
    top_frame = ttk.LabelFrame(root, text="MQTT Broker Connection & Auto-Saved Credentials", padding=10)
    top_frame.pack(fill=tk.X, padx=10, pady=5)

    ttk.Label(top_frame, text="Host:").grid(row=0, column=0, sticky=tk.W, padx=3)
    entry_host = ttk.Entry(top_frame, width=24)
    entry_host.insert(0, broker_cfg.get("host", "rms.iotscada-pmsg.com"))
    entry_host.grid(row=0, column=1, padx=3)

    ttk.Label(top_frame, text="Port:").grid(row=0, column=2, sticky=tk.W, padx=3)
    entry_port = ttk.Entry(top_frame, width=6)
    entry_port.insert(0, str(broker_cfg.get("port", 8883)))
    entry_port.grid(row=0, column=3, padx=3)

    var_tls = tk.BooleanVar(value=broker_cfg.get("use_tls", True))
    chk_tls = ttk.Checkbutton(top_frame, text="TLS/SSL", variable=var_tls)
    chk_tls.grid(row=0, column=4, padx=5)

    ttk.Label(top_frame, text="User:").grid(row=0, column=5, sticky=tk.W, padx=3)
    entry_user = ttk.Entry(top_frame, width=12)
    entry_user.insert(0, broker_cfg.get("username", "test"))
    entry_user.grid(row=0, column=6, padx=3)

    ttk.Label(top_frame, text="Pass:").grid(row=0, column=7, sticky=tk.W, padx=3)
    entry_pass = ttk.Entry(top_frame, width=14, show="*")
    saved_pwd = get_saved_password(entry_host.get(), entry_user.get(), int(entry_port.get() or 8883))
    if saved_pwd:
        entry_pass.insert(0, saved_pwd)
    entry_pass.grid(row=0, column=8, padx=3)

    lbl_status = tk.Label(top_frame, text="● DISCONNECTED", fg="red", font=("Segoe UI", 9, "bold"))
    lbl_status.grid(row=0, column=10, padx=10)

    btn_connect = ttk.Button(top_frame, text="Connect")
    btn_connect.grid(row=0, column=9, padx=5)

    # =========================================================================
    # REGISTER DATA CACHE, SECTIONS & MAPPER
    # =========================================================================
    REGISTER_CACHE = {r["address"]: dict(r) for r in ALL_REGISTERS}
    NAME_TO_ADDR = {r["name"].upper(): r["address"] for r in ALL_REGISTERS}
    current_section = tk.StringVar(value="1. GPRS_Connection")

    # Notebook Tabs
    notebook = ttk.Notebook(root)
    notebook.pack(fill=tk.BOTH, expand=True, padx=10, pady=5)

    # -------------------------------------------------------------------------
    # TAB 1: MODBUS & GPRS REGISTER EXPLORER (SECTIONS & DYNAMIC ONDEMAND FETCH)
    # -------------------------------------------------------------------------
    tab_regs = ttk.Frame(notebook)
    notebook.add(tab_regs, text="  🔌 Modbus & GPRS Register Explorer  ")

    # Section 1 Header: Direct Partition Selector
    f_sections = ttk.LabelFrame(tab_regs, text="1. Select Modbus Register Section / Partition", padding=6)
    f_sections.pack(fill=tk.X, padx=10, pady=3)

    sec_btn_frame = ttk.Frame(f_sections)
    sec_btn_frame.pack(fill=tk.X, pady=2)

    section_colors = {
        "1. GPRS_Connection": ("#e3f2fd", "#0d47a1"),
        "2. SPIFFS_Storage": ("#ffe0b2", "#e65100"),
        "3. Restart_Count": ("#ede7f6", "#4a148c"),
        "4. Solar_Power": ("#fff8e1", "#f57f17"),
        "5. Meters_DLMS": ("#e8f5e9", "#1b5e20"),
        "6. Control_Relays": ("#ffebee", "#b71c1c"),
        "7. System_RTC": ("#e0f2f1", "#004d40"),
        "8. All_Registers": ("#f5f5f5", "#212121"),
    }

    sec_buttons = {}

    def switch_section(sec_name):
        current_section.set(sec_name)
        for name, btn in sec_buttons.items():
            if name == sec_name:
                btn.config(relief=tk.SUNKEN, font=("Segoe UI", 9, "bold"), bd=3)
            else:
                btn.config(relief=tk.RAISED, font=("Segoe UI", 9), bd=1)
        apply_filter_regs()

    for sec in SECTIONS:
        bg_col, fg_col = section_colors.get(sec, ("#f5f5f5", "#333"))
        b = tk.Button(
            sec_btn_frame,
            text=sec,
            command=lambda s=sec: switch_section(s),
            bg=bg_col,
            fg=fg_col,
            font=("Segoe UI", 9, "bold" if sec == "1. GPRS_Connection" else "normal"),
            relief=tk.SUNKEN if sec == "1. GPRS_Connection" else tk.RAISED,
            bd=3 if sec == "1. GPRS_Connection" else 1,
            padx=6,
            pady=3
        )
        b.pack(side=tk.LEFT, padx=3, pady=2)
        sec_buttons[sec] = b

    # Search & Filter Toolbar
    f_search = ttk.Frame(f_sections)
    f_search.pack(fill=tk.X, pady=(4, 2))

    ttk.Label(f_search, text="🔍 Search within Section / All:", font=("Segoe UI", 9, "bold")).pack(side=tk.LEFT, padx=(2, 6))
    entry_reg_search = ttk.Entry(f_search, width=28, font=("Segoe UI", 9))
    entry_reg_search.pack(side=tk.LEFT, padx=4)

    def clear_search():
        entry_reg_search.delete(0, tk.END)
        apply_filter_regs()

    btn_clear_s = ttk.Button(f_search, text="Clear Search", command=clear_search)
    btn_clear_s.pack(side=tk.LEFT, padx=4)

    lbl_reg_count = ttk.Label(f_search, text="Showing 0 registers", font=("Segoe UI", 9, "italic"))
    lbl_reg_count.pack(side=tk.RIGHT, padx=10)

    # -------------------------------------------------------------------------
    # DYNAMIC ONDEMAND PAYLOAD BUILDER & IMMEDIATE FETCH TOOLBAR
    # -------------------------------------------------------------------------
    f_payload = ttk.LabelFrame(tab_regs, text="2. Dynamic Ondemand Device Command (Exact SCADA JSON Dispatcher)", padding=8)
    f_payload.pack(fill=tk.X, padx=10, pady=3)

    p_row1 = ttk.Frame(f_payload)
    p_row1.pack(fill=tk.X, pady=2)

    ttk.Label(p_row1, text="Target IMEI:").pack(side=tk.LEFT, padx=3)
    entry_imei_dyn = ttk.Entry(p_row1, width=17)
    entry_imei_dyn.insert(0, broker_cfg.get("name", "866738083619898"))
    entry_imei_dyn.pack(side=tk.LEFT, padx=3)

    ttk.Label(p_row1, text="MODBUS_REG_NAME:").pack(side=tk.LEFT, padx=(8, 3))
    entry_reg_name_dyn = ttk.Entry(p_row1, width=18, font=("Consolas", 9, "bold"))
    entry_reg_name_dyn.insert(0, "GPRS_S")
    entry_reg_name_dyn.pack(side=tk.LEFT, padx=3)

    ttk.Label(p_row1, text="VALUE_REG:").pack(side=tk.LEFT, padx=(8, 3))
    entry_reg_val_dyn = ttk.Entry(p_row1, width=8, font=("Consolas", 9, "bold"))
    entry_reg_val_dyn.insert(0, "3354")
    entry_reg_val_dyn.pack(side=tk.LEFT, padx=3)

    ttk.Label(p_row1, text="CMKEY:").pack(side=tk.LEFT, padx=(8, 3))
    entry_cmkey_dyn = ttk.Entry(p_row1, width=9, font=("Consolas", 9))
    entry_cmkey_dyn.insert(0, LIVE_KEYS.get("CMKEY", "155521"))
    entry_cmkey_dyn.pack(side=tk.LEFT, padx=3)

    ttk.Label(p_row1, text="PMKEY:").pack(side=tk.LEFT, padx=(8, 3))
    entry_pmkey_dyn = ttk.Entry(p_row1, width=9, font=("Consolas", 9))
    entry_pmkey_dyn.insert(0, LIVE_KEYS.get("PMKEY", "438266"))
    entry_pmkey_dyn.pack(side=tk.LEFT, padx=3)

    ttk.Label(p_row1, text="cmd:").pack(side=tk.LEFT, padx=(8, 3))
    combo_cmd_dyn = ttk.Combobox(p_row1, values=["read", "write"], width=6, state="readonly")
    combo_cmd_dyn.set("read")
    combo_cmd_dyn.pack(side=tk.LEFT, padx=3)

    # Payload Preview & Big Dispatch Button
    p_row2 = ttk.Frame(f_payload)
    p_row2.pack(fill=tk.X, pady=(6, 2))

    lbl_payload_preview = tk.Label(
        p_row2,
        text='Payload: {"msgid":"...","CMKEY":"...","PMKEY":"...","type":"ondemand","cmd":"read","GPRS_S":3354}',
        fg="#0d47a1",
        bg="#e8eaf6",
        font=("Consolas", 9),
        anchor=tk.W,
        relief=tk.SOLID,
        bd=1,
        padx=6,
        pady=3
    )
    lbl_payload_preview.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=(0, 8))

    def update_payload_preview(*args):
        r_name = entry_reg_name_dyn.get().strip() or "MODBUS_REG_NAME"
        r_val = entry_reg_val_dyn.get().strip() or "0"
        cm = entry_cmkey_dyn.get().strip() or LIVE_KEYS.get("CMKEY", "155521")
        pm = entry_pmkey_dyn.get().strip() or LIVE_KEYS.get("PMKEY", "438266")
        cmd_val = combo_cmd_dyn.get().strip() or "read"
        payload_obj = build_ondemand_payload(r_name, r_val, cmkey=cm, pmkey=pm, cmd=cmd_val)
        lbl_payload_preview.config(text=f"Payload: {json.dumps(payload_obj)}")

    entry_reg_name_dyn.bind("<KeyRelease>", update_payload_preview)
    entry_reg_val_dyn.bind("<KeyRelease>", update_payload_preview)
    entry_cmkey_dyn.bind("<KeyRelease>", update_payload_preview)
    entry_pmkey_dyn.bind("<KeyRelease>", update_payload_preview)
    combo_cmd_dyn.bind("<<ComboboxSelected>>", update_payload_preview)

    def dispatch_immediate_fetch():
        nonlocal active_client, is_connected
        if not is_connected or not active_client:
            messagebox.showwarning("Connection", "Please connect to the MQTT broker first using the 'Connect' button above.")
            return

        imei_target = entry_imei_dyn.get().strip() or broker_cfg.get("name", "866738083619898")
        top = f"rtsg-1/ongridrooftop/{imei_target}/ondemand/sub"

        r_name = entry_reg_name_dyn.get().strip() or "GPRS_S"
        r_val = entry_reg_val_dyn.get().strip() or "3354"
        cm = entry_cmkey_dyn.get().strip() or LIVE_KEYS.get("CMKEY", "155521")
        pm = entry_pmkey_dyn.get().strip() or LIVE_KEYS.get("PMKEY", "438266")
        cmd_val = combo_cmd_dyn.get().strip() or "read"

        payload_obj = build_ondemand_payload(r_name, r_val, cmkey=cm, pmkey=pm, cmd=cmd_val)
        payload_json = json.dumps(payload_obj)

        active_client.publish(top, payload_json, qos=0)
        now_str = datetime.now().strftime("%H:%M:%S")
        lbl_fetch_status.config(
            text=f"[✓] Dispatched ondemand '{r_name}' ({r_val}) to '{top}' at {now_str}! Awaiting device response...",
            fg="#2e7d32"
        )

    def dispatch_section_fetch():
        """Dispatches an ondemand fetch for registers in the current section."""
        nonlocal active_client, is_connected
        if not is_connected or not active_client:
            messagebox.showwarning("Connection", "Please connect to the MQTT broker first using the 'Connect' button above.")
            return

        imei_target = entry_imei_dyn.get().strip() or broker_cfg.get("name", "866738083619898")
        top = f"rtsg-1/ongridrooftop/{imei_target}/ondemand/sub"

        # Also trigger standard trigger to fetch all active registers
        active_client.publish(top, "asas", qos=0)
        now_str = datetime.now().strftime("%H:%M:%S")
        lbl_fetch_status.config(
            text=f"[✓] Dispatched batch ondemand query for section '{current_section.get()}' to '{top}' at {now_str}!",
            fg="#1565c0"
        )

    btn_fetch_immediate = tk.Button(
        p_row2,
        text="🚀 IMMEDIATELY FETCH REMOTE DEVICE (ONDEMAND)",
        command=dispatch_immediate_fetch,
        font=("Segoe UI", 10, "bold"),
        bg="#28a745",
        fg="white",
        relief=tk.RAISED,
        bd=2,
        padx=12,
        pady=4
    )
    btn_fetch_immediate.pack(side=tk.RIGHT, padx=4)

    btn_fetch_sec = tk.Button(
        p_row2,
        text="⚡ Fetch Section Batch",
        command=dispatch_section_fetch,
        font=("Segoe UI", 9, "bold"),
        bg="#007bff",
        fg="white",
        relief=tk.RAISED,
        bd=2,
        padx=8,
        pady=4
    )
    btn_fetch_sec.pack(side=tk.RIGHT, padx=4)

    lbl_fetch_status = tk.Label(
        f_payload,
        text="Select any register from the table below, then click 'IMMEDIATELY FETCH REMOTE DEVICE' to query over MQTT.",
        fg="#616161",
        font=("Segoe UI", 9)
    )
    lbl_fetch_status.pack(fill=tk.X, pady=(4, 0))

    # -------------------------------------------------------------------------
    # REGISTER TABLE (TREEVIEW WITH AUTO-MAPPER)
    # -------------------------------------------------------------------------
    reg_table_frame = ttk.Frame(tab_regs)
    reg_table_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=4)

    reg_cols = ("Address", "Register Name", "Section / Category", "Current Value", "Description", "Last Updated")
    tree_regs = ttk.Treeview(reg_table_frame, columns=reg_cols, show="headings", selectmode="browse")

    tree_regs.heading("Address", text="Modbus Addr", anchor=tk.CENTER)
    tree_regs.heading("Register Name", text="Register Name", anchor=tk.W)
    tree_regs.heading("Section / Category", text="Section / Category", anchor=tk.CENTER)
    tree_regs.heading("Current Value", text="Current Value (Live)", anchor=tk.CENTER)
    tree_regs.heading("Description", text="Description / Firmware Function", anchor=tk.W)
    tree_regs.heading("Last Updated", text="Last Updated", anchor=tk.CENTER)

    tree_regs.column("Address", width=95, anchor=tk.CENTER)
    tree_regs.column("Register Name", width=190, anchor=tk.W)
    tree_regs.column("Section / Category", width=150, anchor=tk.CENTER)
    tree_regs.column("Current Value", width=140, anchor=tk.CENTER)
    tree_regs.column("Description", width=340, anchor=tk.W)
    tree_regs.column("Last Updated", width=115, anchor=tk.CENTER)

    tree_regs.tag_configure("updated", background="#e8f5e9", foreground="#1b5e20")
    tree_regs.tag_configure("normal", background="#ffffff")

    reg_scroll_y = ttk.Scrollbar(reg_table_frame, orient=tk.VERTICAL, command=tree_regs.yview)
    tree_regs.configure(yscrollcommand=reg_scroll_y.set)
    tree_regs.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
    reg_scroll_y.pack(side=tk.RIGHT, fill=tk.Y)

    def on_tree_select(event):
        selected = tree_regs.selection()
        if not selected:
            return
        item = tree_regs.item(selected[0])
        vals = item.get("values", [])
        if vals:
            r_addr = str(vals[0])
            r_name = str(vals[1])
            entry_reg_name_dyn.delete(0, tk.END)
            entry_reg_name_dyn.insert(0, r_name)
            entry_reg_val_dyn.delete(0, tk.END)
            entry_reg_val_dyn.insert(0, r_addr)
            update_payload_preview()

    tree_regs.bind("<<TreeviewSelect>>", on_tree_select)
    tree_regs.bind("<Double-1>", lambda e: dispatch_immediate_fetch())

    def apply_filter_regs(*args):
        query = entry_reg_search.get().strip().upper()
        sec = current_section.get()

        for item in tree_regs.get_children():
            tree_regs.delete(item)

        matches = []
        for r in REGISTER_CACHE.values():
            if not sec.startswith("8") and "ALL" not in sec.upper() and r["category"] != sec:
                continue
            if not query:
                matches.append(r)
            elif (query in str(r["address"]) or 
                  query in r["name"].upper() or 
                  query in r["category"].upper() or 
                  query in r.get("description", "").upper()):
                matches.append(r)

        matches.sort(key=lambda x: x["address"])

        for r in matches:
            val = r.get("value", "---")
            ts = r.get("updated_at", "Never")
            tag = "updated" if val != "---" else "normal"
            tree_regs.insert("", tk.END, iid=str(r["address"]), values=(
                r["address"],
                r["name"],
                r["category"],
                val,
                r.get("description", ""),
                ts
            ), tags=(tag,))

        lbl_reg_count.config(text=f"Showing {len(matches)} / {len(REGISTER_CACHE)} registers in '{sec}'")

    entry_reg_search.bind("<KeyRelease>", apply_filter_regs)
    apply_filter_regs()
    update_payload_preview()

    def update_registers_table(data_dict, now_utc):
        updated_count = 0
        if not data_dict or not isinstance(data_dict, dict):
            return 0

        # Update dynamic CMKEY & PMKEY if present in incoming packet
        cm = str(data_dict.get("CMKEY", "") or "")
        pm = str(data_dict.get("PMKEY", "") or "")
        if cm:
            LIVE_KEYS["CMKEY"] = cm
            entry_cmkey_dyn.delete(0, tk.END)
            entry_cmkey_dyn.insert(0, cm)
        if pm:
            LIVE_KEYS["PMKEY"] = pm
            entry_pmkey_dyn.delete(0, tk.END)
            entry_pmkey_dyn.insert(0, pm)

        regs_dict = data_dict.get("registers", {})
        if isinstance(regs_dict, dict):
            for reg_k, reg_v in regs_dict.items():
                try:
                    reg_addr = int(reg_k)
                    if reg_addr in REGISTER_CACHE:
                        REGISTER_CACHE[reg_addr]["value"] = str(reg_v)
                        REGISTER_CACHE[reg_addr]["updated_at"] = now_utc
                        updated_count += 1
                except (ValueError, TypeError):
                    pass

        for k, v in data_dict.items():
            k_up = str(k).upper().replace("-", "_").replace(" ", "_")
            if k_up in NAME_TO_ADDR:
                addr = NAME_TO_ADDR[k_up]
                REGISTER_CACHE[addr]["value"] = str(v)
                REGISTER_CACHE[addr]["updated_at"] = now_utc
                updated_count += 1

        if "IS-1-0---VN" in data_dict and 3044 in REGISTER_CACHE:
            REGISTER_CACHE[3044]["value"] = f"{data_dict['IS-1-0---VN']} V"
            REGISTER_CACHE[3044]["updated_at"] = now_utc
            updated_count += 1
        if "IS-1-0---FREQ" in data_dict and 3052 in REGISTER_CACHE:
            REGISTER_CACHE[3052]["value"] = f"{data_dict['IS-1-0---FREQ']} Hz"
            REGISTER_CACHE[3052]["updated_at"] = now_utc
            updated_count += 1
        if "IS-1-0---POW" in data_dict and 2978 in REGISTER_CACHE:
            REGISTER_CACHE[2978]["value"] = f"{data_dict['IS-1-0---POW']} W"
            REGISTER_CACHE[2978]["updated_at"] = now_utc
            updated_count += 1
        if "CMKEY" in data_dict and 3554 in REGISTER_CACHE:
            REGISTER_CACHE[3554]["value"] = str(data_dict["CMKEY"])
            REGISTER_CACHE[3554]["updated_at"] = now_utc
            updated_count += 1

        apply_filter_regs()
        update_payload_preview()
        if updated_count > 0:
            lbl_fetch_status.config(
                text=f"[✓] Success: Received device response! Updated {updated_count} register values at {now_utc} UTC",
                fg="#1b5e20"
            )
        return updated_count

    # -------------------------------------------------------------------------
    # TAB 2: SEND ONDEMAND COMMAND & PACKET INSPECTOR
    # -------------------------------------------------------------------------
    tab2 = ttk.Frame(notebook)
    notebook.add(tab2, text="  🚀 Send Ondemand Command  ")

    t2_top = ttk.LabelFrame(tab2, text="Dispatch Command to Device", padding=12)
    t2_top.pack(fill=tk.X, padx=10, pady=5)

    ttk.Label(t2_top, text="Target IMEI:").grid(row=0, column=0, sticky=tk.W, pady=4, padx=5)
    entry_imei_cmd = ttk.Entry(t2_top, width=22)
    entry_imei_cmd.insert(0, broker_cfg.get("name", "866738083619898"))
    entry_imei_cmd.grid(row=0, column=1, sticky=tk.W, pady=4, padx=5)

    ttk.Label(t2_top, text="Publish Topic:").grid(row=0, column=2, sticky=tk.W, pady=4, padx=5)
    entry_topic_cmd = ttk.Entry(t2_top, width=42)
    entry_topic_cmd.insert(0, f"rtsg-1/ongridrooftop/{broker_cfg.get('name', '866738083619898')}/ondemand/sub")
    entry_topic_cmd.grid(row=0, column=3, sticky=tk.W, pady=4, padx=5)

    ttk.Label(t2_top, text="Payload:").grid(row=1, column=0, sticky=tk.W, pady=4, padx=5)
    entry_payload_cmd = ttk.Entry(t2_top, width=22)
    entry_payload_cmd.insert(0, "asas")
    entry_payload_cmd.grid(row=1, column=1, sticky=tk.W, pady=4, padx=5)

    lbl_send_status = tk.Label(t2_top, text="Ready to send.", fg="gray", font=("Segoe UI", 9))
    lbl_send_status.grid(row=1, column=3, sticky=tk.W, padx=5)

    def dispatch_ondemand():
        nonlocal active_client, is_connected
        if not is_connected or not active_client:
            messagebox.showwarning("Connection", "Please connect to the MQTT broker first.")
            return

        target_top = entry_topic_cmd.get().strip()
        payload = entry_payload_cmd.get().strip()
        active_client.publish(target_top, payload, qos=0)

        now_str = datetime.now().strftime("%H:%M:%S")
        lbl_send_status.config(text=f"[+] Dispatched '{payload}' at {now_str}! Waiting for response...", fg="blue")
        resp_box.delete("1.0", tk.END)
        resp_box.insert(tk.END, f"[*] Dispatched '{payload}' to {target_top} at {now_str}...\nWaiting for device response on '.../ondemand/pub' or '.../data/pub'...\n")

    btn_send_cmd = tk.Button(t2_top, text="🚀  SEND ONDEMAND REQUEST", command=dispatch_ondemand, bg="#28a745", fg="white", font=("Segoe UI", 10, "bold"), relief=tk.RAISED, padx=10, pady=4)
    btn_send_cmd.grid(row=1, column=2, padx=10, pady=5)

    # Automatic Response Viewer Frame
    t2_resp_frame = ttk.LabelFrame(tab2, text="Live Ondemand Response Data (Auto-Updated when Received)", padding=10)
    t2_resp_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=5)

    resp_box = scrolledtext.ScrolledText(t2_resp_frame, wrap=tk.WORD, font=("Consolas", 10), bg="#f8f9fa")
    resp_box.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
    resp_box.insert(tk.END, "No ondemand response received yet.\nConnect to broker and click 'SEND ONDEMAND REQUEST' above to fetch data.\n")

    # -------------------------------------------------------------------------
    # TAB 3: LIVE TELEMETRY & EXCEL LOGS
    # -------------------------------------------------------------------------
    tab1 = ttk.Frame(notebook)
    notebook.add(tab1, text="  📊 Live Telemetry Monitor  ")

    cols = ("Time (UTC)", "Topic", "IMEI", "Voltage (V)", "Freq (Hz)", "Power (W)", "INDEX", "CMKEY")
    tree = ttk.Treeview(tab1, columns=cols, show="headings", selectmode="browse")
    for col in cols:
        tree.heading(col, text=col)
        tree.column(col, width=110, anchor=tk.CENTER)
    tree.column("Topic", width=260, anchor=tk.W)

    tree_scroll = ttk.Scrollbar(tab1, orient=tk.VERTICAL, command=tree.yview)
    tree.configure(yscrollcommand=tree_scroll.set)
    tree.pack(side=tk.TOP, fill=tk.BOTH, expand=True, padx=5, pady=5)
    tree_scroll.pack(side=tk.RIGHT, fill=tk.Y)

    t1_btn_frame = ttk.Frame(tab1)
    t1_btn_frame.pack(fill=tk.X, padx=5, pady=5)

    lbl_excel = ttk.Label(t1_btn_frame, text=f"Auto-saving all RTEvent messages to: {RTEVENT_CSV_LOG} (Excel format)", foreground="green")
    lbl_excel.pack(side=tk.LEFT, padx=5)

    def open_csv():
        if os.path.exists(RTEVENT_CSV_LOG):
            os.system(f'start "" "{RTEVENT_CSV_LOG}"')
        else:
            messagebox.showinfo("Log File", "No logs created yet.")

    btn_open_excel = ttk.Button(t1_btn_frame, text="Open Excel Log (CSV)", command=open_csv)
    btn_open_excel.pack(side=tk.RIGHT, padx=5)

    def clear_tree():
        for item in tree.get_children():
            tree.delete(item)

    btn_clear_tree = ttk.Button(t1_btn_frame, text="Clear Table", command=clear_tree)
    btn_clear_tree.pack(side=tk.RIGHT, padx=5)

    # -------------------------------------------------------------------------
    # TAB 4: CONSOLE LOGS
    # -------------------------------------------------------------------------
    tab3 = ttk.Frame(notebook)
    notebook.add(tab3, text="  📝 Live Console Logs  ")

    log_box = scrolledtext.ScrolledText(tab3, wrap=tk.WORD, font=("Consolas", 9))
    log_box.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)

    def log_to_console(text):
        log_box.insert(tk.END, text + "\n")
        log_box.see(tk.END)

    def on_gui_message(topic, payload_str, data_dict, is_rtevent):
        now_utc = datetime.now(timezone.utc).strftime("%H:%M:%S")
        log_to_console(f"[{now_utc}] {topic} -> {payload_str}")

        # Update Register Table with live values
        if data_dict:
            root.after(0, lambda: update_registers_table(data_dict, now_utc))

        if "ondemand" in topic.lower() or "data" in topic.lower():
            root.after(0, lambda: update_ondemand_viewer(topic, payload_str, data_dict, now_utc))

        if data_dict:
            imei = data_dict.get("IMEI", "")
            vn = data_dict.get("IS-1-0---VN", "")
            freq = data_dict.get("IS-1-0---FREQ", "")
            pow_w = data_dict.get("IS-1-0---POW", "")
            idx = data_dict.get("INDEX", "")
            cmkey = data_dict.get("CMKEY", "")
            root.after(0, lambda: tree.insert("", 0, values=(now_utc, topic, imei, vn, freq, pow_w, idx, cmkey)))

    def update_ondemand_viewer(topic, payload_str, data_dict, now_utc):
        lbl_send_status.config(text=f"[✓] Response received at {now_utc} UTC!", fg="green")
        resp_box.delete("1.0", tk.END)
        resp_box.insert(tk.END, f"================================================================================\n")
        resp_box.insert(tk.END, f"[RESPONSE RECEIVED] Topic: {topic} | Time: {now_utc} UTC\n")
        resp_box.insert(tk.END, f"================================================================================\n\n")

        if data_dict and isinstance(data_dict, dict):
            resp_box.insert(tk.END, "PARSED REGISTERS & PARAMETERS:\n")
            for k, v in data_dict.items():
                if k != "registers":
                    resp_box.insert(tk.END, f"  * {k:20}: {v}\n")
            if "registers" in data_dict:
                resp_box.insert(tk.END, "\nREGISTERS BREAKDOWN:\n")
                for r, val in data_dict["registers"].items():
                    resp_box.insert(tk.END, f"  * Register [{r}]: {val}\n")
            resp_box.insert(tk.END, "\nFULL JSON PAYLOAD:\n")
            resp_box.insert(tk.END, json.dumps(data_dict, indent=2))
        else:
            resp_box.insert(tk.END, f"RAW PAYLOAD:\n{payload_str}\n")

    def on_ready(cli):
        nonlocal active_client
        active_client = cli

    def toggle_connection():
        nonlocal client_thread, stop_event, is_connected
        if not is_connected:
            host = entry_host.get().strip()
            port = int(entry_port.get().strip() or 8883)
            user = entry_user.get().strip()
            pwd = entry_pass.get().strip()
            tls = var_tls.get()

            if pwd:
                save_server_credential(host, user, pwd, port)

            cfg = json.loads(json.dumps(current_config))
            cfg["broker"]["host"] = host
            cfg["broker"]["port"] = port
            cfg["broker"]["username"] = user
            cfg["broker"]["password"] = pwd
            cfg["broker"]["use_tls"] = tls

            stop_event.clear()
            lbl_status.config(text="● CONNECTING...", fg="orange")
            btn_connect.config(text="Disconnect")

            def worker():
                nonlocal is_connected
                is_connected = True
                root.after(0, lambda: lbl_status.config(text="● CONNECTED", fg="green"))
                run_live_client(cfg, on_message_callback=on_gui_message, stop_event=stop_event, on_client_ready=on_ready)
                is_connected = False
                root.after(0, lambda: lbl_status.config(text="● DISCONNECTED", fg="red"))
                root.after(0, lambda: btn_connect.config(text="Connect"))

            client_thread = threading.Thread(target=worker, daemon=True)
            client_thread.start()
        else:
            stop_event.set()
            lbl_status.config(text="● DISCONNECTING...", fg="orange")

    btn_connect.config(command=toggle_connection)

    root.mainloop()


# ==============================================================================
#                  OPTION 5: CONFIG FILE LIST & MANAGER (CMD LINE)
# ==============================================================================

def open_config_files_cmd_list():
    """Option 5: Lists all configuration files in the command line for run/view/open."""
    while True:
        patterns = ["*.yaml", "*.yml", "*.xml", "*.json"]
        found_files = []
        for pat in patterns:
            for f in glob.glob(pat):
                if f not in found_files and not f.startswith("~"):
                    found_files.append(f)

        primary = ["config.yaml", "config.xml", "server_credentials.json", "connection_history.json"]
        found_files.sort(key=lambda x: (0 if x in primary else 1, x.lower()))

        print("\n" + "=" * 80)
        print("          CONFIGURATION FILES LIST & MANAGER (DEVICE CMD LINE)")
        print("=" * 80)
        print(f"\nFound {len(found_files)} configuration file(s) in workspace:\n")

        for idx, f in enumerate(found_files, 1):
            f_size = os.path.getsize(f)
            mtime = datetime.fromtimestamp(os.path.getmtime(f)).strftime("%Y-%m-%d %H:%M")
            desc = ""
            if f == "config.yaml":
                desc = "(Main RMS IoT SCADA YAML Config - Single IMEI)"
            elif f == "config.xml":
                desc = "(XML Configuration Mirror)"
            elif f == "server_credentials.json":
                desc = "(Auto-Saved Server Passwords & Credentials)"
            elif f == "connection_history.json":
                desc = "(Numbered Connection History Store)"
            elif f.startswith("config_") and f.endswith(".json"):
                desc = f"(Saved Device Config JSON)"
            elif f == "custom_device_example.json":
                desc = "(Sample Custom Device Config)"

            print(f"  [{idx:2d}] {f:30s} {f_size:7d} B  | {mtime}  {desc}")

        print("-" * 80)
        print("Actions:")
        print("  * Enter file number (e.g. '1', '2') to Run / Connect with that config")
        print("  * Type 'V <number>' to View contents in terminal (e.g. 'v 1')")
        print("  * Type 'O <number>' to Open file in system Notepad / Editor (e.g. 'o 1')")
        print("  * Enter '0' to return to Main Menu")
        print("-" * 80)

        cmd = input("Enter command: ").strip()
        if cmd == "0" or not cmd:
            break

        parts = cmd.split()
        if len(parts) == 1 and parts[0].isdigit():
            sel_num = int(parts[0]) - 1
            if 0 <= sel_num < len(found_files):
                target_f = found_files[sel_num]
                print(f"\n[+] Loading and running '{target_f}'...")
                cfg = load_config_file(target_f)
                run_live_client(cfg)
            else:
                print("[!] Invalid file number.")
        elif len(parts) == 2 and parts[0].upper() == "V" and parts[1].isdigit():
            sel_num = int(parts[1]) - 1
            if 0 <= sel_num < len(found_files):
                target_f = found_files[sel_num]
                print(f"\n=== CONTENTS OF {target_f} ===")
                with open(target_f, "r", encoding="utf-8", errors="ignore") as fp:
                    print(fp.read())
                print(f"=== END OF {target_f} ===\n")
            else:
                print("[!] Invalid file number.")
        elif len(parts) == 2 and parts[0].upper() == "O" and parts[1].isdigit():
            sel_num = int(parts[1]) - 1
            if 0 <= sel_num < len(found_files):
                target_f = found_files[sel_num]
                print(f"\n[+] Opening '{target_f}' in editor...")
                os.system(f'start "" "{target_f}"')
            else:
                print("[!] Invalid file number.")
        else:
            print("[!] Unrecognized input. Example: '1' to run, 'V 1' to view, 'O 1' to open.")


# ==============================================================================
#                  MAIN MENU & SELECTION ACTIONS
# ==============================================================================

def select_previous_connection_action():
    history = load_connection_history()
    print_previous_connections(history)

    choice = input(f"Select Connection Number (1-{len(history)}, or 0 to back): ").strip()
    if choice == "0" or not choice:
        return None

    try:
        sel_idx = int(choice) - 1
        if 0 <= sel_idx < len(history):
            selected = history[sel_idx]
            print(f"\n[+] Selected [Connection #{selected['connection_num']}]: {selected['name']}")
            run_live_client(selected["config"])
        else:
            print("[!] Invalid connection number.")
    except ValueError:
        print("[!] Please enter a valid number.")


def enter_new_imei_action():
    history = load_connection_history()
    print_previous_connections(history)

    print("\nSelect which base connection to use for the new IMEI:")
    base_choice = input(f"Enter Connection Number (1-{len(history)}, default: 1): ").strip()
    base_idx = 0
    if base_choice:
        try:
            val = int(base_choice) - 1
            if 0 <= val < len(history):
                base_idx = val
        except ValueError:
            pass

    base_entry = history[base_idx]
    base_cfg = base_entry["config"]
    broker_cfg = base_cfg.get("broker", {})

    new_imei = input("Enter New Target Device IMEI (e.g. 866738083619898): ").strip()
    if not new_imei:
        print("[!] IMEI cannot be empty.")
        return

    dev_name = input(f"Enter Device Name (default: Unit-{new_imei}): ").strip() or f"Unit-{new_imei}"

    new_cfg = json.loads(json.dumps(base_cfg))
    new_cfg["topics"] = generate_single_imei_topics(new_imei)
    new_cfg["registered_devices"] = [
        {
            "imei": new_imei,
            "name": dev_name,
            "device_type": "ONGRID_ROOFTOP_SOLAR",
            "location": "Site Custom",
            "enabled": True
        }
    ]

    conn_name = f"{broker_cfg.get('name', 'Server')} - IMEI {new_imei}"
    history, added = add_to_connection_history(
        conn_name,
        broker_cfg.get("host", "rms.iotscada-pmsg.com"),
        broker_cfg.get("port", 8883),
        broker_cfg.get("use_tls", True),
        broker_cfg.get("username", "test"),
        new_imei,
        new_cfg
    )

    out_file = f"config_{new_imei}.json"
    with open(out_file, "w", encoding="utf-8") as f:
        json.dump(new_cfg, f, indent=2)

    print(f"\n[+] Success: New connection registered as [Connection #{added['connection_num']}]!")
    cont = input("\nDo you want to connect now with this new IMEI? (y/n, default: y): ").strip().lower()
    if cont not in ["n", "no"]:
        run_live_client(new_cfg)


def enter_new_connection_action():
    history = load_connection_history()
    print_previous_connections(history)

    print("\n" + "=" * 80)
    print("                     ENTER NEW MQTT CONNECTION")
    print("=" * 80)

    conn_name = input("Enter Connection Name (default: 866738083619898): ").strip() or "866738083619898"
    host = input("Enter Broker Host (default: rms.iotscada-pmsg.com): ").strip() or "rms.iotscada-pmsg.com"
    port_in = input("Enter Broker Port (default: 8883): ").strip()
    port = int(port_in) if port_in else 8883

    tls_in = input("Enable TLS/SSL? (y/n, default: y): ").strip().lower()
    use_tls = tls_in != "n"

    username = input("Enter Username (default: test): ").strip() or "test"
    password = getpass.getpass("Enter Password: ")

    imei = input("Enter Target Device IMEI (default: 866738083619898): ").strip() or "866738083619898"
    client_id = input("Enter Client ID (default: 84e738ec-179a-4546-88af-cc3ba679d08d): ").strip() or "84e738ec-179a-4546-88af-cc3ba679d08d"

    if password:
        save_server_credential(host, username, password, port, client_id)

    topics_cfg = generate_single_imei_topics(imei)

    new_cfg = {
        "broker": {
            "name": conn_name,
            "host": host,
            "port": port,
            "protocol": "mqtts" if use_tls else "mqtt",
            "mqtt_version": "3.1.1",
            "client_id": client_id,
            "append_timestamp": False,
            "username": username,
            "password": password,
            "keepalive": 10,
            "clean_session": False,
            "use_tls": use_tls,
            "connect_timeout": 30
        },
        "topics": topics_cfg,
        "settings": {
            "auto_poll": False,
            "poll_interval_seconds": 15,
            "response_timeout_seconds": 30,
            "payload_to_send": "asas",
            "target_imei_only": True,
            "rtevent_display_mode": "compact"
        },
        "registered_devices": [
            {
                "imei": imei,
                "name": conn_name,
                "device_type": "ONGRID_ROOFTOP_SOLAR",
                "location": "Site Main",
                "enabled": True
            }
        ]
    }

    history, added = add_to_connection_history(conn_name, host, port, use_tls, username, imei, new_cfg)
    out_file = f"config_{imei}.json"
    with open(out_file, "w", encoding="utf-8") as f:
        json.dump(new_cfg, f, indent=2)

    print(f"\n[+] Success: Registered as [Connection #{added['connection_num']}]!")
    cont = input("Connect now? (y/n, default: y): ").strip().lower()
    if cont not in ["n", "no"]:
        run_live_client(new_cfg)


def run_simulator(config):
    print("\n" + "=" * 80)
    print("       OFFLINE SIMULATOR MODE (No Live Server Required)")
    print("=" * 80)
    devs = config.get("registered_devices", [])
    imei = devs[0].get("imei", "866738083619898") if devs else "866738083619898"
    pub_topic = f"rtsg-1/ongridrooftop/{imei}/ondemand/pub"

    print(f"Target Device IMEI : {imei}")
    print(f"Simulating ondemand request dispatch...")
    time.sleep(1)

    sim_payload = {
        "MSGID": 3307,
        "CMKEY": 353663,
        "IMEI": imei,
        "TIMESTAMP": datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M:%S"),
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
    print(f"[ONDEMAND DATA RECEIVED] Topic: {pub_topic}")
    print(f"Timestamp   : {sim_payload['TIMESTAMP']} UTC | RTT: 642.1 ms")
    print("-" * 80)
    print(f"Parsed Payload Breakdown (JSON):")
    for k, v in sim_payload.items():
        if k != "registers":
            print(f"  {k}: {v}")
    print("  Registers / Metrics:")
    for reg, val in sim_payload["registers"].items():
        print(f"    * Register [{reg}]: {val}")
    print("=" * 80)


def search_and_fetch_gprs_cli():
    """Searches Modbus registers or GPRS list and allows ondemand fetching in CLI."""
    while True:
        print("\n" + "=" * 80)
        print("      MODBUS & GPRS CONNECTION REGISTER EXPLORER (CLI ONDEMAND)")
        print("=" * 80)
        print("\nPlease select an action:\n")
        print("  [1] List All GPRS & Cellular Connection Registers (APN, IP, Port, RSSI, Status)")
        print("  [2] Search Registers by Name or Address Keyword (e.g. 'GPRS', 'PORT', 'VOLT')")
        print("  [3] Show All 300+ Modbus / SCADA Registers")
        print("  [4] Fetch Live Current Values from Device (Ondemand Query)")
        print("  [5] Back to Main Menu\n")
        print("-" * 80)

        sub_ch = input("Enter choice (1-5): ").strip()
        if sub_ch == "1":
            gprs_regs = [r for r in ALL_REGISTERS if r.get("category") in ["GPRS & Network", "IP & WiFi Config", "SSL & Security"]]
            print(f"\nFound {len(gprs_regs)} GPRS / Connection Register(s):")
            print("-" * 80)
            print(f" {'Addr':<6} {'Register Name':<24} {'Category':<16} {'Description'}")
            print("-" * 80)
            for r in gprs_regs:
                print(f" {r['address']:<6} {r['name']:<24} {r['category']:<16} {r.get('description', '')}")
            print("-" * 80)

            fetch_now = input("\nDispatch ondemand fetch to query these values from the device right now? (Y/n): ").strip().lower()
            if fetch_now in ["", "y", "yes"]:
                cfg = load_config_file("config.yaml") if os.path.exists("config.yaml") else DEFAULT_CONFIG
                run_live_client(cfg, once=True)

        elif sub_ch == "2":
            kw = input("Enter search keyword (e.g. 'GPRS', 'IP', 'SIM', '3354'): ").strip()
            results = search_registers(kw)
            print(f"\nFound {len(results)} matching register(s) for '{kw}':")
            print("-" * 80)
            print(f" {'Addr':<6} {'Register Name':<24} {'Category':<16} {'Description'}")
            print("-" * 80)
            for r in results:
                print(f" {r['address']:<6} {r['name']:<24} {r['category']:<16} {r.get('description', '')}")
            print("-" * 80)

            fetch_now = input("\nDispatch ondemand fetch to query values from device? (Y/n): ").strip().lower()
            if fetch_now in ["", "y", "yes"]:
                cfg = load_config_file("config.yaml") if os.path.exists("config.yaml") else DEFAULT_CONFIG
                run_live_client(cfg, once=True)

        elif sub_ch == "3":
            print(f"\nTotal Modbus Registers: {len(ALL_REGISTERS)}")
            print("-" * 80)
            print(f" {'Addr':<6} {'Register Name':<24} {'Category':<16} {'Description'}")
            print("-" * 80)
            for r in ALL_REGISTERS:
                print(f" {r['address']:<6} {r['name']:<24} {r['category']:<16} {r.get('description', '')}")
            print("-" * 80)

        elif sub_ch == "4":
            cfg = load_config_file("config.yaml") if os.path.exists("config.yaml") else DEFAULT_CONFIG
            r_name = input("Enter register name to query (default: GPRS_S): ").strip() or "GPRS_S"
            r_val = input("Enter register address / value (default: 3354): ").strip() or "3354"
            payload_dict = build_ondemand_payload(r_name, r_val, cmkey=LIVE_KEYS.get("CMKEY", "155521"), pmkey=LIVE_KEYS.get("PMKEY", "438266"))
            payload_str = json.dumps(payload_dict)
            print(f"\nDispatching live Ondemand Query: {payload_str}")
            cfg["settings"]["payload_to_send"] = payload_str
            run_live_client(cfg, once=True)

        elif sub_ch == "5":
            break


def main_menu():
    global DEFAULT_CONFIG
    while True:
        curr_mode = DEFAULT_CONFIG["settings"].get("rtevent_display_mode", "compact").upper()
        print("\n" + "=" * 80)
        print("              MQTT SCADA & RTEVENT CONTROLLER - MAIN MENU")
        print("=" * 80)
        print("\nPlease select an Option:\n")
        print("  [1] Launch Tkinter Graphical UI (Modbus & GPRS Register Explorer, Ondemand, Telemetry)")
        print("  [2] Select the previous connection")
        print("  [3] Search & Fetch Modbus / GPRS Registers (CLI Ondemand Query)")
        print("  [4] Enter new IEMI / IMEI (Single Device Mode)")
        print("  [5] Enter new connection")
        print("  [6] Configuration Files List (Open/View/Run config.yaml, config.xml, json...)")
        print(f"  [7] Toggle Telemetry Display Mode (Currently: {curr_mode})")
        print("  [8] Open Excel / CSV RTEvent Log File")
        print("  [9] Offline Simulator Mode       (Test without connecting to live broker)")
        print("  [10] Exit\n")
        print("-" * 80)

        choice = input("Enter your choice (1-10): ").strip()

        if choice == "1":
            launch_gui()

        elif choice == "2":
            select_previous_connection_action()

        elif choice == "3":
            search_and_fetch_gprs_cli()

        elif choice == "4":
            enter_new_imei_action()

        elif choice == "5":
            enter_new_connection_action()

        elif choice == "6":
            open_config_files_cmd_list()

        elif choice == "7":
            curr = DEFAULT_CONFIG["settings"].get("rtevent_display_mode", "compact")
            modes = ["compact", "full", "silent"]
            next_idx = (modes.index(curr) + 1) % len(modes)
            new_mode = modes[next_idx]
            DEFAULT_CONFIG["settings"]["rtevent_display_mode"] = new_mode
            print(f"\n[+] Telemetry display mode is now: {new_mode.upper()}")

        elif choice == "8":
            if os.path.exists(RTEVENT_CSV_LOG):
                print(f"Opening '{RTEVENT_CSV_LOG}'...")
                os.system(f'start "" "{RTEVENT_CSV_LOG}"')
            else:
                print(f"[!] Log file '{RTEVENT_CSV_LOG}' does not exist yet.")

        elif choice == "9":
            cfg = load_config_file("config.yaml") if os.path.exists("config.yaml") else DEFAULT_CONFIG
            run_simulator(cfg)

        elif choice in ["10", "q", "exit"]:
            print("\nExiting. Goodbye!")
            sys.exit(0)


def main():
    parser = argparse.ArgumentParser(description="MQTT SCADA & RTEvent Controller")
    parser.add_argument("--gui", action="store_true", help="Launch Graphical User Interface directly")
    parser.add_argument("-c", "--config", help="Path to config file (.yaml, .xml, .json)")
    parser.add_argument("--simulate", action="store_true", help="Run offline simulation mode")
    parser.add_argument("--once", action="store_true", help="Fetch once and exit")
    parser.add_argument("--password", help="Broker password")
    args = parser.parse_args()

    if args.gui:
        launch_gui(load_config_file(args.config) if args.config else None)
    elif args.simulate:
        cfg = load_config_file(args.config) if args.config else DEFAULT_CONFIG
        run_simulator(cfg)
    elif args.config:
        cfg = load_config_file(args.config)
        run_live_client(cfg, once=args.once, cli_password=args.password)
    else:
        main_menu()


if __name__ == "__main__":
    main()
