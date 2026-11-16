#!/usr/bin/env python3
"""
Mock Remote Device Simulator
Simulates a physical IoT node responding to request commands with ACKs and Telemetry payloads.
"""

import time
import json
import random
import argparse
from datetime import datetime, timezone

try:
    import paho.mqtt.client as mqtt
except ImportError:
    mqtt = None


def run_mock_device(host="localhost", port=1883, imei="866738083623411", name="Simulated Solar Node"):
    if not mqtt:
        print("[!] Error: paho-mqtt is required to run the mock device.")
        return

    sub_topic = f"rtsg-1/ongridrooftop/{imei}/ondemand/sub"
    pub_topic = f"rtsg-1/ongridrooftop/{imei}/ondemand/pub"

    print("=" * 70)
    print("                MOCK REMOTE IOT DEVICE SIMULATOR")
    print("=" * 70)
    print(f"Device Name  : {name}")
    print(f"Device IMEI  : {imei}")
    print(f"Broker       : {host}:{port}")
    print(f"Listening on : {sub_topic}")
    print(f"Publishing to: {pub_topic}")
    print("=" * 70)

    try:
        client = mqtt.Client(mqtt.CallbackAPIVersion.VERSION2, client_id=f"mock_dev_{imei}")
    except AttributeError:
        client = mqtt.Client(client_id=f"mock_dev_{imei}")

    def on_connect(cli, userdata, flags, rc, properties=None):
        rc_code = rc if isinstance(rc, int) else getattr(rc, "value", rc)
        if rc_code == 0:
            print(f"[+] Device connected to broker. Subscribed to '{sub_topic}'")
            cli.subscribe(sub_topic, qos=0)
        else:
            print(f"[!] Device failed to connect: {rc_code}")

    def on_message(cli, userdata, msg):
        payload_in = msg.payload.decode("utf-8", errors="ignore")
        print(f"\n[<-- REQUEST RECEIVED] Topic: {msg.topic}")
        print(f"    Payload: {payload_in}")

        time.sleep(0.3)
        # Generate realistic telemetry registers
        data = {
            "MSGID": random.randint(3000, 3999),
            "CMKEY": random.randint(300000, 399999),
            "timestamp": datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M:%S"),
            "CMD": "read",
            "type": "ondemand",
            "imei": imei,
            "registers": {
                "3345": 208,
                "3365": 1,
                "3747": random.randint(900000, 950000),
                "3799": 18,
                "4013": random.randint(14000000, 14500000),
                "4109": 18,
                "4113": random.randint(40, 60)
            }
        }
        resp_json = json.dumps(data)
        cli.publish(pub_topic, resp_json, qos=0)
        print(f"[--> TELEMETRY PUBLISHED] Topic: {pub_topic}")
        print(f"    Registers: {data['registers']}")

    client.on_connect = on_connect
    client.on_message = on_message

    try:
        client.connect(host, port, 60)
        client.loop_forever()
    except KeyboardInterrupt:
        print("\n[*] Stopping Mock Device...")
    finally:
        client.disconnect()


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Mock Remote Device Simulator")
    parser.add_argument("--host", default="localhost", help="Broker host")
    parser.add_argument("--port", type=int, default=1883, help="Broker port")
    parser.add_argument("--imei", default="866738083623411", help="Device IMEI")
    args = parser.parse_args()

    run_mock_device(host=args.host, port=args.port, imei=args.imei)
