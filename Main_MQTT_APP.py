#!/usr/bin/env python3
"""
Main MQTT Application Entry Point
Direct wrapper and executor for MQTT_SERVER_CONTROLLER.py
Supports both CLI and Tkinter GUI modes with Modbus/GPRS Explorer, Topic Manager, and Telemetry.
"""
import sys
import os

from MQTT_SERVER_CONTROLLER import *

if __name__ == "__main__":
    main()
