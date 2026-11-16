#!/usr/bin/env python3
"""
Wrapper for backwards compatibility.
Invokes the master script: MQTT_SERVER_CONTROLLER.py
"""
import sys
from MQTT_SERVER_CONTROLLER import main, main_menu, run_live_client, run_simulator, load_config_file, DEFAULT_CONFIG

if __name__ == "__main__":
    main()
