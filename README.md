# MQTT SCADA & Ondemand Controller

A Python MQTT controller and telemetry processor featuring single-IMEI targeting, terminal noise silencing, Tkinter desktop GUI with dedicated Modbus & GPRS Connection Register Explorer, real-time response viewer, ondemand fetching, and command-line configuration file manager.

---

## Key Updates & Features

### 1. 🔌 Modbus & GPRS Register Explorer (GUI Tab 1)
- Built-in database of all 300+ Modbus / SCADA registers partitioned into direct sections:
  1. **`1. GPRS_Connection`**: All cellular, APN, server IP/port, signal RSSI, and modem communication registers.
  2. **`2. SPIFFS_Storage`**: SPIFFS flash memory, SD card, EEPROM, and storage error registers.
  3. **`3. Restart_Count`**: Watchdog reboots, modem resets, MCU resets, tripping counters, and retry registers.
  4. **`4. Solar_Power`**: Grid AC status, voltages, currents, power thresholds, inverter VD, and frequency.
  5. **`5. Meters_DLMS`**: Smart meters, DLMS billing counters, load surveys, and tamper event profiles.
  6. **`6. Control_Relays`**: Digital output commands, contactors, relays, and switches.
  7. **`7. System_RTC`**: Real-time clock (RTC), firmware version, CPU millis, GPS coordinates, and board temperature.
  8. **`8. All_Registers`**: Full searchable catalogue of all 300+ Modbus registers.

### 2. 📡 Dynamic Ondemand Device Command Dispatcher
- **Targeted Dynamic SCADA Payload**:
  Constructs and dispatches the exact required JSON structure:
  ```json
  {
    "msgid": "6374196",
    "CMKEY": "155521",
    "PMKEY": "438266",
    "timestamp": "2026-09-07 13:35:32",
    "type": "ondemand",
    "cmd": "read",
    "MODBUS_REG_NAME": VALUE_REG_GIVEN_BY_REG
  }
  ```
- **One-Click Table Selection**:
  Clicking any register row in the table automatically fills `MODBUS_REG_NAME` (e.g. `GPRS_S`) and `VALUE_REG` (e.g. `3354`), updates the live preview, and clicking **`🚀 IMMEDIATELY FETCH REMOTE DEVICE (ONDEMAND)`** publishes the request directly over MQTT!
- **Auto-Synced Handshake Keys**:
  `CMKEY` and `PMKEY` automatically synchronize with the active session keys whenever the device connects.

### 2. Single IMEI Subscription (No Server-Wide Wildcards)
- Subscribes strictly to the **target IMEI** (e.g. `rtsg-1/ongridrooftop/866738083619898/#`).
- Eliminates noise from other devices on the broker.
- Automatically handles `messagekey/sub` handshake and auto-dispatches ondemand requests.

### 3. Tkinter GUI: "Send Ondemand Request" Button & Live Response Viewer
- **Tab 2 (Send Ondemand Command)**:
  - **`🚀 SEND ONDEMAND REQUEST` button**: One click immediately publishes the payload (`asas` or custom) to the target device request topic.
  - **Live Ondemand Response Viewer**: Real-time parsed JSON breakdown of all registers and metrics.

### 4. Option [3]: Search & Fetch Modbus / GPRS Registers in CLI
- Allows terminal users to list all GPRS connection registers, search keywords, and trigger live ondemand queries without opening the GUI.

### 5. Option [6]: Configuration Files List in Command Line
- Manage all `.yaml`, `.xml`, and `.json` configs directly from the terminal.

---

## Main Menu

Launch the controller:
```powershell
python MQTT_SERVER_CONTROLLER.py
```

```text
================================================================================
              MQTT SCADA & RTEVENT CONTROLLER - MAIN MENU
================================================================================

Please select an Option:

  [1] Launch Tkinter Graphical UI (GUI with Send Ondemand Button & Viewer)
  [2] Select the previous connection
  [3] Enter new IEMI / IMEI (Single Device Mode)
  [4] Enter new connection
  [5] Configuration Files List (Open/View/Run config.yaml, config.xml, json...)
  [6] Toggle Silence 'rtevent' from Console (Currently: ENABLED)
  [7] Open Excel / CSV RTEvent Log File
  [8] Offline Simulator Mode       (Test without connecting to live broker)
  [9] Exit
```

---

## Tkinter Desktop GUI

To launch the graphical window directly:
```powershell
python MQTT_SERVER_CONTROLLER.py --gui
```
