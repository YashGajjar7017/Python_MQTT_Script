# MQTT SCADA & Ondemand Controller

A Python MQTT controller and telemetry processor featuring single-IMEI targeting, terminal noise silencing, Tkinter desktop GUI with dedicated Modbus & GPRS Connection Register Explorer, real-time response viewer, ondemand fetching, and command-line configuration file manager.

---

## Key Updates & Features

### 1. 🔌 Modbus & GPRS Register Explorer (GUI Tab 1)
- Built-in database of all 300+ Modbus / SCADA registers from the device firmware defines.
- **Instant Search & Filters**:
  - Live search as you type (e.g. `GPRS`, `IP`, `PORT`, `APN`, `SIM`, `RSSI`, or register addresses like `3354`).
  - Quick-preset buttons:
    - **`🌐 Show GPRS List`**: Instantly isolates all cellular, APN, IP, port, and network status registers.
    - **`🔌 IP & WiFi`**: Displays local IP, subnet mask, gateway, DNS, and WiFi configurations.
    - **`⚡ Solar & Power`**: Voltage, current, power thresholds, inverter metrics, and grid supply.
    - **`⚙️ System & CPU`**: Firmware version, RTC clock, watchdog, CPU status, and reset flags.
    - **`📋 Show All`**: View all 300+ Modbus registers with addresses and descriptions.
- **Ondemand Live Fetch Actions**:
  - **`🚀 FETCH CURRENT VALUES (ONDEMAND)`**: Publishes ondemand fetch (`asas`) to `rtsg-1/ongridrooftop/{imei}/ondemand/sub`.
  - **`🌐 FETCH GPRS LIST VALUES`**: Isolates GPRS registers and immediately queries the device.
  - **`⚡ Fetch Selected Register`**: Queries the device specifically for the highlighted register row.
- **Automatic Real-Time Value Updates**:
  - When the device responds on `.../ondemand/pub`, `.../data/pub`, or `.../rtevent/pub`, incoming values in `registers` or top-level keys are **automatically mapped** into the **"Current Value"** column and **highlighted in green** with live timestamp.

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
