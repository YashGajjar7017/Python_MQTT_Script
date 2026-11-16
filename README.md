# MQTT SCADA & Ondemand Controller

A Python MQTT controller and telemetry processor featuring single-IMEI targeting, terminal noise silencing, Tkinter desktop GUI with dedicated Ondemand command dispatching, real-time response viewer, and command-line configuration file manager.

---

## Key Updates & Features

### 1. Single IMEI Subscription (No Server-Wide Wildcards)
- Removed all `+` wildcards (`rtsg-1/ongridrooftop/+/...`).
- Subscribes strictly to the **target IMEI** (e.g. `866738083619898`), preventing messages from other server devices from flooding your session.
- **Silence `rtevent` from console**: `skip_rtevent_console: true` silences high-frequency `rtevent` messages from spamming the terminal, while still logging them safely to `rtevent_logs.csv` in the background.

### 2. Tkinter GUI: "Send Ondemand Request" Button & Live Response Viewer
- **Tab 2 (Send Ondemand Command)** now features:
  - **`🚀 SEND ONDEMAND REQUEST` button**: One click immediately publishes the payload (`asas` or custom) to the target device request topic.
  - **Live Ondemand Response Viewer**: Automatically updates in real time when the remote device replies on `.../ondemand/pub`, breaking down registers (`3345`, `3747`, `4013`, etc.) with millisecond round-trip latency.

### 3. Option [5]: Configuration Files List in Command Line
- Entering **`5`** in the main menu displays an interactive file manager right in your terminal:
  - Lists `config.yaml`, `config.xml`, `server_credentials.json`, `connection_history.json`, etc.
  - **Enter number** (e.g. `1`): Immediately runs and connects with that config.
  - **`V <number>`** (e.g. `v 1`): Prints the file contents directly in the terminal.
  - **`O <number>`** (e.g. `o 1`): Opens the file in Windows Notepad / default editor.

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
