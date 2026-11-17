"""
Port Scanner — PCB Dashboard
-----------------------------
A PCB-themed GUI port scanner compatible with modbus_app.py.
Scans TCP (and optionally UDP) ports on a target host using only
Python stdlib (socket / threading) — no extra pip packages required.

Reuses the same PCB colour palette, LED, ICButton, PCBProgressBar,
LogConsole and PCBTable widgets as modbus_app.py for a consistent look.
"""

import socket
import subprocess
import threading
import time
import tkinter as tk
from tkinter import ttk, messagebox, filedialog
from datetime import datetime
import os
import re

# ─────────────────────────────────────────────
#  PCB Colour Palette  (same as modbus_app.py)
# ─────────────────────────────────────────────
PCB_BG        = "#0d1f0d"
PCB_BOARD     = "#133213"
PCB_TRACK     = "#1a4d1a"
PCB_TRACK_LT  = "#206620"
PCB_COPPER    = "#c87533"
PCB_COPPER_LT = "#e89a55"
PCB_IC_BODY   = "#1c1c1c"
PCB_IC_PIN    = "#aaaaaa"
PCB_LED_OFF   = "#1a2e1a"
PCB_LED_RED   = "#ff3030"
PCB_LED_GRN   = "#00ff55"
PCB_LED_YLW   = "#ffcc00"
PCB_LED_BLU   = "#00aaff"
PCB_TEXT      = "#b8ffb8"
PCB_TEXT_DIM  = "#4a7a4a"
PCB_WHITE     = "#e8ffe8"
PCB_SILK      = "#d4e8d4"
PCB_ERR       = "#ff4444"
PCB_WARN      = "#ffaa00"
PCB_OK        = "#00ff80"
PCB_GOLD      = "#ffd700"

# ─────────────────────────────────────────────
#  Well-known port → service name map
# ─────────────────────────────────────────────
COMMON_SERVICES = {
    21: "FTP", 22: "SSH", 23: "Telnet", 25: "SMTP",
    53: "DNS", 67: "DHCP", 68: "DHCP", 69: "TFTP",
    80: "HTTP", 110: "POP3", 119: "NNTP", 123: "NTP",
    135: "MS-RPC", 137: "NetBIOS-NS", 138: "NetBIOS-DGM",
    139: "NetBIOS-SSN", 143: "IMAP", 161: "SNMP",
    194: "IRC", 389: "LDAP", 443: "HTTPS", 445: "SMB",
    465: "SMTPS", 502: "Modbus", 514: "Syslog", 515: "LPD",
    587: "SMTP-SUB", 631: "IPP", 636: "LDAPS",
    993: "IMAPS", 995: "POP3S", 1080: "SOCKS",
    1194: "OpenVPN", 1433: "MSSQL", 1521: "Oracle",
    1883: "MQTT", 2181: "ZooKeeper", 3306: "MySQL",
    3389: "RDP", 4840: "OPC-UA", 5000: "Flask/Dev",
    5432: "PostgreSQL", 5672: "AMQP", 5900: "VNC",
    6379: "Redis", 6881: "BitTorrent", 7547: "CWMP",
    8080: "HTTP-Alt", 8443: "HTTPS-Alt", 8883: "MQTT-TLS",
    9200: "Elasticsearch", 9300: "Elasticsearch-Cluster",
    10502: "Modbus-Alt", 11211: "Memcached",
    27017: "MongoDB", 47808: "BACnet",
}

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
OUTPUT_DIR  = os.path.normpath(os.path.join(SCRIPT_DIR, ".."))


# ─────────────────────────────────────────────
#  Core scan function (runs in worker thread)
# ─────────────────────────────────────────────
def scan_port_tcp(host: str, port: int, timeout: float,
                  retries: int = 2, retry_delay: float = 0.15) -> tuple[bool, float]:
    """
    Return (is_open, latency_ms).

    Retries up to *retries* extra times on failure so that a single dropped
    SYN (common with embedded/Modbus devices that have tiny TCP backlogs)
    does not cause a false-negative result.

    Why retries matter
    ------------------
    Embedded PLCs / Modbus devices often accept only 4-8 simultaneous
    half-open TCP connections.  When many threads probe at once the device
    silently drops excess SYNs; with no reply the connect_ex() times out and
    the port is wrongly reported closed.  A short pause + retry catches these.
    """
    for attempt in range(retries + 1):
        t0 = time.perf_counter()
        try:
            with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
                s.settimeout(timeout)
                rc = s.connect_ex((host, port))
                latency = (time.perf_counter() - t0) * 1000
                if rc == 0:
                    return True, round(latency, 1)
        except OSError:
            latency = (time.perf_counter() - t0) * 1000
        # Port appears closed on this attempt — wait briefly before retrying
        # so we don't pile more SYNs onto an already-overloaded device
        if attempt < retries:
            time.sleep(retry_delay)
    return False, round(latency, 1)


def resolve_host(host: str) -> str | None:
    """Return the resolved IPv4 string, or None on failure."""
    try:
        return socket.gethostbyname(host)
    except socket.gaierror:
        return None


# ─────────────────────────────────────────────
#  Network info — local IP, gateway, subnet
# ─────────────────────────────────────────────
def get_local_ip() -> str:
    """Best-effort: local IP used to reach the internet."""
    try:
        with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as s:
            s.connect(("8.8.8.8", 80))
            return s.getsockname()[0]
    except OSError:
        return "unavailable"


def _parse_ipconfig() -> list[dict]:
    """
    Run `ipconfig /all` and parse all adapters into a list of dicts:
      {name, ip, subnet, gateway, mac, dns}
    Only adapters with both an IPv4 address and a gateway are returned.
    """
    adapters: list[dict] = []
    try:
        out = subprocess.check_output(
            ["ipconfig", "/all"],
            stderr=subprocess.DEVNULL,
            timeout=8,
            text=True,
            encoding="utf-8",
            errors="replace",
        )
    except Exception:
        return adapters

    current: dict = {}
    for line in out.splitlines():
        # New adapter block starts with a non-indented header line
        if line and not line.startswith(" ") and not line.startswith("\t"):
            if current.get("ip") and current.get("gateway"):
                adapters.append(current)
            current = {"name": line.strip().rstrip(":")}
            continue

        stripped = line.strip()

        m = re.search(r"IPv4 Address[^:]*:\s*([\d.]+)", stripped, re.IGNORECASE)
        if m:
            current["ip"] = m.group(1)

        m = re.search(r"Subnet Mask[^:]*:\s*([\d.]+)", stripped, re.IGNORECASE)
        if m:
            current["subnet"] = m.group(1)

        m = re.search(r"Default Gateway[^:]*:\s*([\d.]+)", stripped, re.IGNORECASE)
        if m and m.group(1) != "0.0.0.0":
            current.setdefault("gateway", m.group(1))

        m = re.search(r"Physical Address[^:]*:\s*([0-9A-F\-]{17})", stripped, re.IGNORECASE)
        if m:
            current["mac"] = m.group(1)

        m = re.search(r"DNS Servers[^:]*:\s*([\d.]+)", stripped, re.IGNORECASE)
        if m:
            current.setdefault("dns", m.group(1))

    if current.get("ip") and current.get("gateway"):
        adapters.append(current)

    return adapters


def get_network_info() -> dict:
    """
    Return network info for the *active* adapter (the one whose IP matches
    the socket-based local-IP probe, or the first one with a gateway).
    Keys: local_ip, gateway, subnet, mac, dns, adapter_name, all_adapters
    """
    local_ip = get_local_ip()
    adapters = _parse_ipconfig()

    # Prefer the adapter whose IP matches the socket probe
    best = next((a for a in adapters if a.get("ip") == local_ip), None)
    if best is None and adapters:
        best = adapters[0]

    if best:
        return {
            "local_ip":     best.get("ip",      local_ip),
            "gateway":      best.get("gateway",  "—"),
            "subnet":       best.get("subnet",   "—"),
            "mac":          best.get("mac",      "—"),
            "dns":          best.get("dns",      "—"),
            "adapter_name": best.get("name",     "—"),
            "all_adapters": adapters,
        }
    # Fallback — no ipconfig data
    return {
        "local_ip":     local_ip,
        "gateway":      "—",
        "subnet":       "—",
        "mac":          "—",
        "dns":          "—",
        "adapter_name": "—",
        "all_adapters": [],
    }


# ─────────────────────────────────────────────
#  LED Widget
# ─────────────────────────────────────────────
class LED(tk.Canvas):
    def __init__(self, parent, color=PCB_LED_GRN, size=14, **kwargs):
        super().__init__(parent, width=size + 6, height=size + 6,
                         bg=PCB_BOARD, highlightthickness=0, **kwargs)
        self.size  = size
        self.color = color
        self._on   = False
        self._blink_job = None
        self._draw()

    def _draw(self):
        s, p = self.size, 3
        self.delete("all")
        if self._on:
            self.create_oval(0, 0, s + 6, s + 6,
                             fill="", outline=self.color, width=1)
            self.create_oval(p, p, s + p, s + p,
                             fill=self.color, outline=PCB_COPPER_LT, width=1)
            self.create_oval(p + 2, p + 2, p + s // 3, p + s // 3,
                             fill="white", outline="")
        else:
            self.create_oval(p, p, s + p, s + p,
                             fill=PCB_LED_OFF, outline=PCB_COPPER, width=1)

    def turn_on(self):  self._on = True;  self._draw()
    def turn_off(self): self._on = False; self._draw()

    def set_color(self, color):
        self.color = color
        self._draw()

    def blink(self, interval=400):
        if self._blink_job:
            self.after_cancel(self._blink_job)
        self._on = not self._on
        self._draw()
        self._blink_job = self.after(interval, lambda: self.blink(interval))

    def stop_blink(self, final_state=True):
        if self._blink_job:
            self.after_cancel(self._blink_job)
            self._blink_job = None
        self._on = final_state
        self._draw()


# ─────────────────────────────────────────────
#  IC Button
# ─────────────────────────────────────────────
class ICButton(tk.Canvas):
    def __init__(self, parent, text="IC", subtext="", command=None,
                 width=220, height=78, pin_count=8, **kwargs):
        super().__init__(parent, width=width, height=height,
                         bg=PCB_BOARD, highlightthickness=0, **kwargs)
        self.text = text; self.subtext = subtext
        self.command = command
        self.w = width;  self.h = height
        self.pin_count = pin_count
        self._pressed = self._hover = False
        self._draw()
        self.bind("<ButtonPress-1>",   self._on_press)
        self.bind("<ButtonRelease-1>", self._on_release)
        self.bind("<Enter>",           self._on_enter)
        self.bind("<Leave>",           self._on_leave)

    def _draw(self):
        self.delete("all")
        w, h = self.w, self.h
        body_pad = 18
        bx1, by1 = body_pad, 5
        bx2, by2 = w - body_pad, h - 5
        pps = self.pin_count // 2
        ps  = (by2 - by1) / (pps + 1)
        for i in range(pps):
            py = by1 + ps * (i + 1)
            self.create_rectangle(0, py - 3, body_pad - 1, py + 3,
                                   fill=PCB_IC_PIN, outline="")
            self.create_rectangle(body_pad - 3, py - 5, body_pad + 3, py + 5,
                                   fill=PCB_COPPER, outline=PCB_COPPER_LT, width=1)
            self.create_rectangle(w - body_pad + 1, py - 3, w, py + 3,
                                   fill=PCB_IC_PIN, outline="")
            self.create_rectangle(w - body_pad - 3, py - 5, w - body_pad + 3, py + 5,
                                   fill=PCB_COPPER, outline=PCB_COPPER_LT, width=1)
        offset  = 0 if self._pressed else 3
        self.create_rectangle(bx1 + 2, by1 + offset + 1, bx2 + 2, by2 + offset + 1,
                               fill="#050a05", outline="")
        if self._pressed:
            body_c = "#111"; bx1 += 1; by1 += offset
        elif self._hover:
            body_c = "#2a3a22"
        else:
            body_c = "#1e2e1e"
        self.create_rectangle(bx1, by1, bx2, by2,
                               fill=body_c, outline=PCB_COPPER, width=2)
        cx = (bx1 + bx2) // 2
        self.create_arc(cx - 9, by1 - 6, cx + 9, by1 + 6,
                         start=0, extent=180,
                         fill=body_c, outline=PCB_COPPER, width=1)
        self.create_oval(bx1 + 7, by2 - 11, bx1 + 12, by2 - 6,
                          fill=PCB_COPPER_LT, outline="")
        ty = (by1 + by2) // 2 - (9 if self.subtext else 0)
        tc = PCB_OK if self._pressed else PCB_LED_GRN
        self.create_text(w // 2, ty, text=self.text,
                          fill=tc, font=("Consolas", 11, "bold"))
        if self.subtext:
            self.create_text(w // 2, ty + 17, text=self.subtext,
                              fill=PCB_TEXT_DIM, font=("Consolas", 8))

    def _on_press(self, e):   self._pressed = True;  self._draw()
    def _on_release(self, e):
        self._pressed = False; self._draw()
        if self.command: self.command()
    def _on_enter(self, e): self._hover = True;  self._draw()
    def _on_leave(self, e): self._hover = False; self._draw()
    def set_text(self, t, s=""):
        self.text = t; self.subtext = s; self._draw()


# ─────────────────────────────────────────────
#  PCB Progress Bar
# ─────────────────────────────────────────────
class PCBProgressBar(tk.Canvas):
    def __init__(self, parent, width=400, height=18, **kwargs):
        super().__init__(parent, width=width, height=height,
                         bg=PCB_BOARD, highlightthickness=0, **kwargs)
        self.w = width; self.h = height
        self._pct = 0.0
        self._draw()

    def set(self, pct):
        self._pct = max(0.0, min(1.0, pct))
        self._draw()

    def _draw(self):
        self.delete("all")
        w, h = self.w, self.h
        self.create_rectangle(0, 0, w, h, fill="#0a180a", outline=PCB_TRACK, width=1)
        fw  = int((w - 2) * self._pct)
        seg = 9
        for x in range(1, fw, seg + 2):
            sw = min(seg, fw - x)
            c  = PCB_LED_GRN if self._pct < 0.85 else PCB_LED_YLW
            self.create_rectangle(x, 2, x + sw, h - 2, fill=c, outline="")
        self.create_text(w // 2, h // 2,
                          text=f"{int(self._pct * 100)}%",
                          fill=PCB_WHITE, font=("Consolas", 8, "bold"))


# ─────────────────────────────────────────────
#  Log Console
# ─────────────────────────────────────────────
class LogConsole(tk.Text):
    def __init__(self, parent, **kwargs):
        super().__init__(parent,
                         bg="#080f08", fg=PCB_TEXT,
                         font=("Consolas", 9),
                         insertbackground=PCB_TEXT,
                         selectbackground=PCB_TRACK,
                         relief="flat", bd=0,
                         state="disabled", **kwargs)
        self.tag_configure("info",    foreground=PCB_TEXT)
        self.tag_configure("ok",      foreground=PCB_OK)
        self.tag_configure("warn",    foreground=PCB_WARN)
        self.tag_configure("error",   foreground=PCB_ERR)
        self.tag_configure("heading", foreground=PCB_COPPER_LT,
                           font=("Consolas", 9, "bold"))
        self.tag_configure("dim",     foreground=PCB_TEXT_DIM)

    def log(self, msg, level="info"):
        self.config(state="normal")
        ts = datetime.now().strftime("%H:%M:%S")
        self.insert("end", f"[{ts}] {msg}\n", level)
        self.see("end")
        self.config(state="disabled")

    def clear(self):
        self.config(state="normal")
        self.delete("1.0", "end")
        self.config(state="disabled")


# ─────────────────────────────────────────────
#  Scrollable PCB Table
# ─────────────────────────────────────────────
class PCBTable(tk.Frame):
    def __init__(self, parent, columns, **kwargs):
        super().__init__(parent, bg=PCB_BG, **kwargs)
        self.columns = list(columns)
        self._setup_style()
        vsb = ttk.Scrollbar(self, orient="vertical")
        hsb = ttk.Scrollbar(self, orient="horizontal")
        self.tree = ttk.Treeview(self, columns=self.columns, show="headings",
                                  style="PCB.Treeview",
                                  yscrollcommand=vsb.set,
                                  xscrollcommand=hsb.set)
        vsb.config(command=self.tree.yview)
        hsb.config(command=self.tree.xview)
        self._apply_columns()
        self.tree.grid(row=0, column=0, sticky="nsew")
        vsb.grid(row=0, column=1, sticky="ns")
        hsb.grid(row=1, column=0, sticky="ew")
        self.grid_rowconfigure(0, weight=1)
        self.grid_columnconfigure(0, weight=1)

    def _setup_style(self):
        style = ttk.Style()
        style.theme_use("clam")
        style.configure("PCB.Treeview",
                        background=PCB_BOARD, foreground=PCB_TEXT,
                        fieldbackground=PCB_BOARD, rowheight=22,
                        font=("Consolas", 9))
        style.configure("PCB.Treeview.Heading",
                        background=PCB_IC_BODY, foreground=PCB_COPPER_LT,
                        font=("Consolas", 9, "bold"), relief="flat")
        style.map("PCB.Treeview",
                  background=[("selected", PCB_TRACK_LT)],
                  foreground=[("selected", PCB_WHITE)])

    def _apply_columns(self):
        self.tree["columns"] = self.columns
        self.tree["show"]    = "headings"
        widths = {"Port": 70, "Status": 80, "Service": 120, "Banner": 220, "Latency": 90}
        for col in self.columns:
            self.tree.heading(col, text=col)
            w = widths.get(col, 100)
            self.tree.column(col, width=w, minwidth=60, anchor="center")

    def clear(self):
        for item in self.tree.get_children():
            self.tree.delete(item)

    def add_row(self, values, tag=""):
        self.tree.insert("", "end", values=values, tags=(tag,))
        self.tree.tag_configure("open",   background="#0f2b0f", foreground=PCB_LED_GRN)
        self.tree.tag_configure("closed", background=PCB_BOARD, foreground=PCB_TEXT_DIM)
        self.tree.tag_configure("modbus", background="#1a1400",  foreground=PCB_LED_YLW)


# ─────────────────────────────────────────────
#  Main Application
# ─────────────────────────────────────────────
class PortScannerApp(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Port Scanner — PCB Dashboard  v1.0")
        self.configure(bg=PCB_BG)
        self.resizable(True, True)
        self.minsize(820, 600)

        self._scan_running = False
        self._stop_flag    = threading.Event()
        self._results: list[dict] = []

        self._build_header()
        self._build_main()
        self._build_footer()

        self.log("PCB Port Scanner ready.", "ok")
        self.log("Enter a host IP / hostname and port range, then press SCAN.", "dim")
        # Detect network info in background so UI shows instantly
        threading.Thread(target=self._refresh_net_info_bg, daemon=True).start()

    # ── helpers ──────────────────────────────
    def _ui(self, fn, *a, **kw):
        self.after(0, lambda: fn(*a, **kw))

    def log(self, msg, level="info"):
        self.console.log(msg, level)
        self.footer_var.set(msg[:120])

    # ── Header ───────────────────────────────
    def _build_header(self):
        hf = tk.Frame(self, bg=PCB_BOARD, height=72)
        hf.pack(fill="x", pady=(0, 2))
        hf.pack_propagate(False)

        lc = tk.Canvas(hf, width=68, height=72, bg=PCB_BOARD, highlightthickness=0)
        lc.pack(side="left", padx=8)
        self._draw_logo(lc)

        tf = tk.Frame(hf, bg=PCB_BOARD)
        tf.pack(side="left", fill="y", padx=4)
        tk.Label(tf, text="PORT  SCANNER  ·  PCB  DASHBOARD",
                 bg=PCB_BOARD, fg=PCB_LED_GRN,
                 font=("Consolas", 17, "bold")).pack(anchor="w", pady=(10, 0))
        tk.Label(tf, text="TCP Port Scanner  ·  Compatible with modbus_app.py",
                 bg=PCB_BOARD, fg=PCB_TEXT_DIM,
                 font=("Consolas", 8)).pack(anchor="w")

        lf = tk.Frame(hf, bg=PCB_BOARD)
        lf.pack(side="right", padx=18, pady=10)
        for col, (attr, lbl, color) in enumerate([
            ("led_scan", "SCAN", PCB_LED_GRN),
            ("led_busy", "BUSY", PCB_LED_YLW),
            ("led_open", "OPEN", PCB_LED_BLU),
            ("led_err",  "ERR",  PCB_LED_RED),
        ]):
            led = LED(lf, color=color)
            led.grid(row=0, column=col, padx=6)
            tk.Label(lf, text=lbl, bg=PCB_BOARD, fg=PCB_TEXT_DIM,
                     font=("Consolas", 7)).grid(row=1, column=col)
            setattr(self, attr, led)

    def _draw_logo(self, c):
        c.create_rectangle(20, 10, 48, 62, fill=PCB_IC_BODY,
                            outline=PCB_COPPER, width=2)
        for i in range(3):
            y = 18 + i * 13
            c.create_rectangle(8,  y, 20, y + 7, fill=PCB_IC_PIN, outline="")
            c.create_rectangle(48, y, 60, y + 7, fill=PCB_IC_PIN, outline="")
        c.create_arc(26, 7, 42, 17, start=0, extent=180,
                     fill=PCB_IC_BODY, outline=PCB_COPPER)
        c.create_text(34, 36, text="PS", fill=PCB_LED_GRN,
                      font=("Consolas", 12, "bold"))

    # ── Main area ────────────────────────────
    def _build_main(self):
        pw = tk.PanedWindow(self, orient="horizontal",
                            bg=PCB_BG, sashrelief="flat",
                            sashwidth=5, sashpad=1)
        pw.pack(fill="both", expand=True, padx=4, pady=4)

        left = tk.Frame(pw, bg=PCB_BOARD, width=270)
        pw.add(left, minsize=250)
        self._build_left(left)

        right = tk.Frame(pw, bg=PCB_BG)
        pw.add(right, minsize=420)
        self._build_right(right)

    # ── Left panel ───────────────────────────
    def _build_left(self, parent):
        self._build_net_info(parent)
        self._build_config(parent)
        self._build_buttons(parent)
        self._build_stats(parent)

    def _build_net_info(self, parent):
        """[ HOST NETWORK INFO ] panel — shows local IP, gateway, subnet, MAC."""
        nf = tk.LabelFrame(parent, text="[ HOST NETWORK INFO ]",
                           bg=PCB_BOARD, fg=PCB_COPPER_LT,
                           font=("Consolas", 8, "bold"),
                           labelanchor="n", bd=2, relief="groove")
        nf.pack(fill="x", padx=8, pady=(8, 2))

        # Label-value pairs
        self._net_vars: dict[str, tk.StringVar] = {}
        rows = [
            ("Adapter",    "adapter_name"),
            ("Local IP",   "local_ip"),
            ("Gateway",    "gateway"),
            ("Subnet",     "subnet"),
            ("MAC",        "mac"),
            ("DNS",        "dns"),
        ]
        for i, (label, key) in enumerate(rows):
            tk.Label(nf, text=label + ":", bg=PCB_BOARD, fg=PCB_TEXT_DIM,
                     font=("Consolas", 8), anchor="w").grid(
                row=i, column=0, padx=6, pady=1, sticky="w")
            var = tk.StringVar(value="detecting…")
            color = PCB_LED_YLW if key == "gateway" else PCB_LED_GRN
            tk.Label(nf, textvariable=var, bg=PCB_BOARD, fg=color,
                     font=("Consolas", 8, "bold"), anchor="w").grid(
                row=i, column=1, padx=4, pady=1, sticky="w")
            self._net_vars[key] = var

        # Adapter chooser (shown when multiple adapters exist)
        self._adapter_names: list[str] = []
        self._adapter_choice = tk.StringVar()
        self._adapter_cb = ttk.Combobox(nf, textvariable=self._adapter_choice,
                                         state="readonly", width=20,
                                         font=("Consolas", 8))
        # Only grid it when we have multiple adapters (done in _populate_net_info)

        # Action buttons row
        btn_row = len(rows)
        bf = tk.Frame(nf, bg=PCB_BOARD)
        bf.grid(row=btn_row, column=0, columnspan=2, padx=4, pady=(4, 6), sticky="ew")

        tk.Button(bf, text="⟳ Refresh",
                  command=lambda: threading.Thread(
                      target=self._refresh_net_info_bg, daemon=True).start(),
                  bg=PCB_IC_BODY, fg=PCB_TEXT, font=("Consolas", 7),
                  relief="flat", padx=4,
                  activebackground=PCB_TRACK,
                  activeforeground=PCB_WHITE).pack(side="left", padx=2)

        tk.Button(bf, text="→ Use Gateway",
                  command=self._use_gateway,
                  bg=PCB_IC_BODY, fg=PCB_LED_YLW, font=("Consolas", 7),
                  relief="flat", padx=4,
                  activebackground=PCB_TRACK,
                  activeforeground=PCB_WHITE).pack(side="left", padx=2)

        tk.Button(bf, text="→ Use Local IP",
                  command=self._use_local_ip,
                  bg=PCB_IC_BODY, fg=PCB_LED_GRN, font=("Consolas", 7),
                  relief="flat", padx=4,
                  activebackground=PCB_TRACK,
                  activeforeground=PCB_WHITE).pack(side="left", padx=2)

        nf.columnconfigure(1, weight=1)
        self._net_frame = nf
        self._net_btn_row = btn_row

    # ── Network info helpers ──────────────────
    def _refresh_net_info_bg(self):
        """Runs in a background thread — fetches network info then updates UI."""
        info = get_network_info()
        self._all_adapters = info.get("all_adapters", [])
        self._ui(self._populate_net_info, info)

    def _populate_net_info(self, info: dict):
        """Called on the UI thread to fill in all network labels."""
        self._net_vars["adapter_name"].set(info.get("adapter_name", "—")[:32])
        self._net_vars["local_ip"].set(info.get("local_ip",     "—"))
        self._net_vars["gateway"].set(info.get("gateway",      "—"))
        self._net_vars["subnet"].set(info.get("subnet",       "—"))
        self._net_vars["mac"].set(info.get("mac",          "—"))
        self._net_vars["dns"].set(info.get("dns",          "—"))

        gw = info.get("gateway", "—")
        lip = info.get("local_ip", "")

        # Log the detected info
        self.log(f"Network  local={lip}  gateway={gw}  subnet={info.get('subnet','—')}", "ok")

        # If multiple adapters found, show the combobox to switch
        adapters = info.get("all_adapters", [])
        if len(adapters) > 1:
            names = [f"{a.get('name','?')[:28]}  [{a.get('ip','?')}]" for a in adapters]
            self._adapter_cb["values"] = names
            self._adapter_choice.set(names[0])
            # Place combobox just below the DNS row if not already placed
            try:
                self._adapter_cb.grid(row=self._net_btn_row + 1, column=0,
                                      columnspan=2, padx=6, pady=(0, 4), sticky="ew")
                self._adapter_cb.bind("<<ComboboxSelected>>", self._on_adapter_change)
            except tk.TclError:
                pass

    def _on_adapter_change(self, _event=None):
        """User selected a different adapter from the combobox."""
        idx = self._adapter_cb.current()
        if 0 <= idx < len(self._all_adapters):
            a = self._all_adapters[idx]
            fake_info = {
                "adapter_name": a.get("name", "—"),
                "local_ip":     a.get("ip",      "—"),
                "gateway":      a.get("gateway",  "—"),
                "subnet":       a.get("subnet",   "—"),
                "mac":          a.get("mac",      "—"),
                "dns":          a.get("dns",      "—"),
                "all_adapters": self._all_adapters,
            }
            self._populate_net_info(fake_info)

    def _use_gateway(self):
        """Copy detected gateway IP into the Host/IP scan field."""
        gw = self._net_vars["gateway"].get()
        if gw and gw != "—":
            self._cfg["Host / IP"].set(gw)
            self.log(f"Host set to gateway: {gw}", "ok")
        else:
            messagebox.showwarning("Gateway Not Found",
                                   "Could not detect a default gateway.\n"
                                   "Check your network connection and press Refresh.")

    def _use_local_ip(self):
        """Copy detected local IP into the Host/IP scan field."""
        lip = self._net_vars["local_ip"].get()
        if lip and lip != "—" and lip != "unavailable":
            self._cfg["Host / IP"].set(lip)
            self.log(f"Host set to local IP: {lip}", "ok")
        else:
            messagebox.showwarning("Local IP Not Found",
                                   "Could not detect the local IP address.")

    def _build_config(self, parent):
        lf = tk.LabelFrame(parent, text="[ SCAN CONFIG ]",
                           bg=PCB_BOARD, fg=PCB_COPPER_LT,
                           font=("Consolas", 8, "bold"),
                           labelanchor="n", bd=2, relief="groove")
        lf.pack(fill="x", padx=8, pady=(8, 4))

        fields = [
            ("Host / IP",      "192.168.4.1"),
            ("Start Port",     "1"),
            ("End Port",       "1024"),
            ("Timeout (s)",    "1.0"),
            ("Threads",        "30"),
            ("Retries",        "2"),
            ("Retry delay(s)", "0.15"),
        ]
        self._cfg: dict[str, tk.StringVar] = {}
        for i, (lbl, dflt) in enumerate(fields):
            tk.Label(lf, text=lbl + ":", bg=PCB_BOARD, fg=PCB_TEXT_DIM,
                     font=("Consolas", 8), anchor="w").grid(
                row=i, column=0, padx=6, pady=2, sticky="w")
            var = tk.StringVar(value=dflt)
            tk.Entry(lf, textvariable=var, width=14,
                     bg="#080f08", fg=PCB_LED_GRN,
                     insertbackground=PCB_LED_GRN,
                     font=("Consolas", 9), relief="flat", bd=0,
                     highlightthickness=1,
                     highlightbackground=PCB_TRACK,
                     highlightcolor=PCB_COPPER).grid(
                row=i, column=1, padx=6, pady=2, sticky="ew")
            self._cfg[lbl] = var

        # Quick Preset selector
        n = len(fields)
        tk.Label(lf, text="Preset:", bg=PCB_BOARD, fg=PCB_TEXT_DIM,
                 font=("Consolas", 8)).grid(row=n, column=0, padx=6, pady=2, sticky="w")
        self._preset = tk.StringVar(value="Common (1-1024)")
        presets = ["Common (1-1024)", "Full (1-65535)", "Modbus (502)", "Web (80,443,8080)", "Custom"]
        cb = ttk.Combobox(lf, textvariable=self._preset, values=presets,
                          state="readonly", width=18)
        cb.grid(row=n, column=1, padx=6, pady=2, sticky="w")
        cb.bind("<<ComboboxSelected>>", self._apply_preset)

        # Show-closed toggle
        n += 1
        self._show_closed = tk.BooleanVar(value=False)
        tk.Checkbutton(lf, text="Show closed ports", variable=self._show_closed,
                       bg=PCB_BOARD, fg=PCB_TEXT, selectcolor=PCB_IC_BODY,
                       activebackground=PCB_BOARD, font=("Consolas", 8)).grid(
            row=n, column=0, columnspan=2, padx=6, pady=2, sticky="w")

        # Grab banner toggle
        n += 1
        self._grab_banner = tk.BooleanVar(value=True)
        tk.Checkbutton(lf, text="Grab service banner", variable=self._grab_banner,
                       bg=PCB_BOARD, fg=PCB_TEXT, selectcolor=PCB_IC_BODY,
                       activebackground=PCB_BOARD, font=("Consolas", 8)).grid(
            row=n, column=0, columnspan=2, padx=6, pady=2, sticky="w")

        lf.columnconfigure(1, weight=1)

    def _apply_preset(self, _event=None):
        p = self._preset.get()
        if p == "Common (1-1024)":
            self._cfg["Start Port"].set("1")
            self._cfg["End Port"].set("1024")
        elif p == "Full (1-65535)":
            self._cfg["Start Port"].set("1")
            self._cfg["End Port"].set("65535")
        elif p == "Modbus (502)":
            self._cfg["Start Port"].set("502")
            self._cfg["End Port"].set("502")
        elif p == "Web (80,443,8080)":
            # handled as start=80 end=8080 inclusive
            self._cfg["Start Port"].set("80")
            self._cfg["End Port"].set("8080")

    def _build_buttons(self, parent):
        bf = tk.Frame(parent, bg=PCB_BOARD)
        bf.pack(fill="x", padx=8, pady=4)

        tk.Label(bf, text="──── IC CONTROL CHIPS ────",
                 bg=PCB_BOARD, fg=PCB_TEXT_DIM, font=("Consolas", 7)).pack(pady=(0, 4))

        self.scan_btn = ICButton(
            bf, text="▶  SCAN PORTS",
            subtext="TCP connect scan",
            command=self._on_scan, width=246, height=78, pin_count=8)
        self.scan_btn.pack(pady=4)

        self.stop_btn = ICButton(
            bf, text="■  STOP SCAN",
            subtext="Abort current scan",
            command=self._on_stop, width=246, height=78, pin_count=8)
        self.stop_btn.pack(pady=4)

        pf = tk.Frame(bf, bg=PCB_BOARD)
        pf.pack(fill="x", pady=2)
        tk.Label(pf, text="SCAN PROGRESS", bg=PCB_BOARD, fg=PCB_TEXT_DIM,
                 font=("Consolas", 7)).pack(anchor="w")
        self.progress = PCBProgressBar(pf, width=246, height=18)
        self.progress.pack()

        self.status_var = tk.StringVar(value="IDLE")
        self.status_lbl = tk.Label(bf, textvariable=self.status_var,
                                   bg=PCB_BOARD, fg=PCB_LED_GRN,
                                   font=("Consolas", 9, "bold"))
        self.status_lbl.pack(pady=2)

    def _build_stats(self, parent):
        sf = tk.LabelFrame(parent, text="[ SCAN STATS ]",
                           bg=PCB_BOARD, fg=PCB_COPPER_LT,
                           font=("Consolas", 8, "bold"),
                           labelanchor="n", bd=2, relief="groove")
        sf.pack(fill="x", padx=8, pady=4)

        self._stat_vars: dict[str, tk.StringVar] = {}
        for lbl in ("Scanned", "Open", "Closed", "Elapsed"):
            tk.Label(sf, text=lbl + ":", bg=PCB_BOARD, fg=PCB_TEXT_DIM,
                     font=("Consolas", 8), anchor="w").pack(anchor="w", padx=8)
            var = tk.StringVar(value="—")
            tk.Label(sf, textvariable=var, bg=PCB_BOARD, fg=PCB_LED_GRN,
                     font=("Consolas", 9, "bold"), anchor="w").pack(
                anchor="w", padx=16, pady=(0, 2))
            self._stat_vars[lbl] = var

        # Export button
        tk.Button(sf, text="⬇ Export CSV", command=self._export_csv,
                  bg=PCB_IC_BODY, fg=PCB_TEXT, font=("Consolas", 8),
                  relief="flat", padx=4,
                  activebackground=PCB_TRACK,
                  activeforeground=PCB_WHITE).pack(padx=8, pady=(4, 6), fill="x")

    # ── Right panel ──────────────────────────
    def _build_right(self, parent):
        nb = ttk.Notebook(parent)
        nb.pack(fill="both", expand=True, padx=2, pady=2)

        style = ttk.Style()
        style.configure("TNotebook", background=PCB_BG, borderwidth=0)
        style.configure("TNotebook.Tab",
                        background=PCB_IC_BODY, foreground=PCB_TEXT_DIM,
                        font=("Consolas", 9), padding=[10, 4])
        style.map("TNotebook.Tab",
                  background=[("selected", PCB_BOARD)],
                  foreground=[("selected", PCB_COPPER_LT)])

        # Results tab
        res_tab = tk.Frame(nb, bg=PCB_BG)
        nb.add(res_tab, text="  🔌  SCAN RESULTS  ")
        self._build_results_tab(res_tab)

        # Log tab
        log_tab = tk.Frame(nb, bg=PCB_BG)
        nb.add(log_tab, text="  📟  LOG CONSOLE  ")
        self._build_log_tab(log_tab)

        self._nb = nb

    def _build_results_tab(self, tab):
        hdr = tk.Frame(tab, bg=PCB_BG)
        hdr.pack(fill="x", padx=6, pady=(4, 0))
        self.res_title = tk.Label(hdr,
                                   text="Press SCAN to start port discovery.",
                                   bg=PCB_BG, fg=PCB_TEXT_DIM,
                                   font=("Consolas", 9))
        self.res_title.pack(side="left")

        self.result_table = PCBTable(tab,
            columns=["Port", "Status", "Service", "Banner", "Latency (ms)"])
        self.result_table.pack(fill="both", expand=True, padx=6, pady=4)

    def _build_log_tab(self, tab):
        hdr = tk.Frame(tab, bg=PCB_BG)
        hdr.pack(fill="x", padx=6, pady=(4, 0))
        tk.Label(hdr, text="SCAN LOG  ·  SERIAL MONITOR",
                 bg=PCB_BG, fg=PCB_COPPER_LT, font=("Consolas", 9, "bold")).pack(side="left")
        tk.Button(hdr, text="CLR", command=lambda: self.console.clear(),
                  bg=PCB_IC_BODY, fg=PCB_TEXT_DIM, font=("Consolas", 7),
                  relief="flat").pack(side="right", padx=4)

        frame = tk.Frame(tab, bg=PCB_BG, relief="flat", bd=1,
                         highlightthickness=1, highlightbackground=PCB_TRACK)
        frame.pack(fill="both", expand=True, padx=6, pady=4)
        self.console = LogConsole(frame, wrap="word")
        vsb = ttk.Scrollbar(frame, command=self.console.yview)
        self.console.config(yscrollcommand=vsb.set)
        vsb.pack(side="right", fill="y")
        self.console.pack(fill="both", expand=True)

    # ── Footer ───────────────────────────────
    def _build_footer(self):
        ff = tk.Frame(self, bg=PCB_BOARD, height=26)
        ff.pack(fill="x", side="bottom")
        ff.pack_propagate(False)
        self.footer_var = tk.StringVar(value="Ready.")
        tk.Label(ff, textvariable=self.footer_var,
                 bg=PCB_BOARD, fg=PCB_TEXT_DIM, font=("Consolas", 8)).pack(
            side="left", padx=10, pady=4)
        tk.Label(ff, text="Port Scanner PCB  ·  stdlib socket",
                 bg=PCB_BOARD, fg=PCB_TEXT_DIM, font=("Consolas", 8)).pack(
            side="right", padx=10)

    # ── Config helper ────────────────────────
    def _get_config(self) -> dict | None:
        try:
            cfg = {
                "host":        self._cfg["Host / IP"].get().strip(),
                "start":       int(self._cfg["Start Port"].get()),
                "end":         int(self._cfg["End Port"].get()),
                "timeout":     float(self._cfg["Timeout (s)"].get()),
                "threads":     max(1, int(self._cfg["Threads"].get())),
                "retries":     max(0, int(self._cfg["Retries"].get())),
                "retry_delay": max(0.0, float(self._cfg["Retry delay(s)"].get())),
                "show_closed": self._show_closed.get(),
                "grab_banner": self._grab_banner.get(),
            }
        except ValueError as e:
            messagebox.showerror("Config Error", f"Invalid setting:\n{e}")
            return None
        if not cfg["host"]:
            messagebox.showerror("Config Error", "Please enter a Host / IP address.")
            return None
        if not (1 <= cfg["start"] <= 65535) or not (1 <= cfg["end"] <= 65535):
            messagebox.showerror("Config Error", "Ports must be in range 1–65535.")
            return None
        if cfg["start"] > cfg["end"]:
            cfg["start"], cfg["end"] = cfg["end"], cfg["start"]
        return cfg

    # ── Scan trigger ─────────────────────────
    def _on_scan(self):
        if self._scan_running:
            self.log("Scan already running!", "warn")
            return
        cfg = self._get_config()
        if cfg is None:
            return

        self._stop_flag.clear()
        self._results.clear()
        self.result_table.clear()
        self.res_title.config(text="Scanning…", fg=PCB_LED_YLW)

        self._scan_running = True
        self.led_err.turn_off()
        self.led_open.turn_off()
        self.led_scan.blink(350)
        self.led_busy.blink(600)
        self.status_var.set("SCANNING…")
        self.status_lbl.config(fg=PCB_LED_YLW)
        self.progress.set(0.0)
        for v in self._stat_vars.values():
            v.set("—")

        threading.Thread(target=self._scan_worker, args=(cfg,), daemon=True).start()

    def _on_stop(self):
        if self._scan_running:
            self._stop_flag.set()
            self.log("Stop requested — waiting for threads…", "warn")

    # ── Scan worker (background thread) ──────
    def _scan_worker(self, cfg: dict):
        host  = cfg["host"]
        t0    = time.time()
        total = cfg["end"] - cfg["start"] + 1

        # Resolve hostname → IP
        self._ui(self.log, f"Resolving host: {host}…", "info")
        ip = resolve_host(host)
        if ip is None:
            self._ui(self.log, f"Cannot resolve host: {host}", "error")
            self._ui(self.led_err.turn_on)
            self._ui(self._finish_scan, False, 0, 0, time.time() - t0)
            return

        retries     = cfg["retries"]
        retry_delay = cfg["retry_delay"]
        n_threads   = cfg["threads"]

        self._ui(self.log,
                 f"Resolved → {ip}  |  Scanning ports {cfg['start']}–{cfg['end']}  "
                 f"({total} ports, {n_threads} threads, "
                 f"timeout {cfg['timeout']}s, retries {retries}×{retry_delay}s)", "ok")
        if n_threads > 50:
            self._ui(self.log,
                     "⚠ High thread count — embedded devices may drop SYNs causing "
                     "false-negatives. Recommended ≤ 30 threads for PLCs/Modbus.", "warn")

        ports        = list(range(cfg["start"], cfg["end"] + 1))
        open_count   = 0
        done         = 0
        # Collect all results; sort & display after all threads finish
        all_results: list[dict] = []   # {port, is_open, service, banner, latency}

        # Semaphore limits how many threads run at once — this is the key
        # throttle that prevents SYN flooding an embedded device's TCP stack.
        sem  = threading.Semaphore(n_threads)
        lock = threading.Lock()

        def probe(port: int):
            nonlocal open_count, done
            if self._stop_flag.is_set():
                sem.release()
                return

            is_open, latency = scan_port_tcp(
                ip, port, cfg["timeout"],
                retries=retries, retry_delay=retry_delay,
            )

            banner = ""
            if is_open and cfg["grab_banner"]:
                banner = self._grab_banner_text(ip, port, cfg["timeout"])

            service = COMMON_SERVICES.get(
                port,
                socket.getservbyport(port, "tcp")
                if self._safe_getservbyport(port) else "unknown",
            )

            with lock:
                if is_open:
                    open_count += 1
                done += 1
                pct = done / total
                all_results.append({
                    "port": port, "is_open": is_open,
                    "service": service, "banner": banner, "latency": latency,
                })
                if is_open:
                    self._ui(self.log,
                             f"  OPEN  {port:>5}  {service:<18}  {banner[:40]}", "ok")
                self._ui(self._update_progress, pct, done, total, open_count)
            sem.release()

        for port in ports:
            if self._stop_flag.is_set():
                break
            sem.acquire()
            t = threading.Thread(target=probe, args=(port,), daemon=True)
            t.start()

        # Drain the semaphore: wait for every running thread to release
        for _ in range(n_threads):
            sem.acquire()

        # ── Sort by port number and populate the table in one shot ──
        all_results.sort(key=lambda r: r["port"])
        open_rows   = []
        for r in all_results:
            if not r["is_open"] and not cfg["show_closed"]:
                continue
            tag = ("modbus" if r["port"] == 502
                   else "open" if r["is_open"]
                   else "closed")
            row = (r["port"],
                   "OPEN" if r["is_open"] else "closed",
                   r["service"],
                   r["banner"][:60] if r["banner"] else "—",
                   f"{r['latency']} ms")
            self._ui(self.result_table.add_row, row, tag)
            if r["is_open"]:
                open_rows.append(r)

        self._results = [{"port": r["port"], "service": r["service"],
                          "banner": r["banner"], "latency_ms": r["latency"]}
                         for r in open_rows]

        elapsed = time.time() - t0
        if self._stop_flag.is_set():
            self._ui(self.log,
                     f"Scan aborted after {done}/{total} ports "
                     f"({open_count} open) in {elapsed:.1f}s", "warn")
        else:
            self._ui(self.log,
                     f"Scan complete — {open_count} open port(s) found "
                     f"in {elapsed:.1f}s  ({total} ports scanned)", "ok")
        self._ui(self._finish_scan, not self._stop_flag.is_set(),
                 open_count, done, elapsed)

    @staticmethod
    def _safe_getservbyport(port: int) -> bool:
        try:
            socket.getservbyport(port, "tcp")
            return True
        except OSError:
            return False

    @staticmethod
    def _grab_banner_text(host: str, port: int, timeout: float) -> str:
        """Try to grab a one-line banner from the open port."""
        try:
            with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
                s.settimeout(max(timeout, 1.0))
                s.connect((host, port))
                # Send a minimal HTTP probe for web ports; otherwise just listen
                if port in (80, 8080, 8443, 443, 8000, 8888):
                    s.sendall(b"HEAD / HTTP/1.0\r\n\r\n")
                raw = s.recv(256)
                return raw.decode("utf-8", errors="replace").split("\n")[0].strip()
        except Exception:
            return ""

    # ── UI updates ───────────────────────────
    def _update_progress(self, pct, done, total, open_cnt):
        self.progress.set(pct)
        self.status_var.set(f"SCANNED  {done} / {total}")
        self._stat_vars["Scanned"].set(f"{done} / {total}")
        self._stat_vars["Open"].set(str(open_cnt))
        self._stat_vars["Closed"].set(str(done - open_cnt))
        if open_cnt > 0:
            self.led_open.turn_on()

    def _finish_scan(self, success: bool, open_cnt: int, total_done: int, elapsed: float):
        self._scan_running = False
        self.led_scan.stop_blink(success)
        self.led_busy.stop_blink(False)
        self.progress.set(1.0 if success else self.progress._pct)
        self._stat_vars["Elapsed"].set(f"{elapsed:.1f} s")

        if success:
            self.status_var.set("DONE ✔")
            self.status_lbl.config(fg=PCB_OK)
            msg = (f"✔  {open_cnt} open port(s) found  ({total_done} scanned)"
                   if open_cnt else "✔  No open ports found.")
            self.res_title.config(text=msg, fg=PCB_OK if open_cnt else PCB_TEXT_DIM)
        else:
            self.status_var.set("ABORTED ■")
            self.status_lbl.config(fg=PCB_WARN)
            self.res_title.config(text="Scan aborted.", fg=PCB_WARN)

    # ── CSV export ───────────────────────────
    def _export_csv(self):
        if not self._results:
            messagebox.showinfo("No Data", "Run a scan first.")
            return
        fp = filedialog.asksaveasfilename(
            defaultextension=".csv",
            filetypes=[("CSV files", "*.csv")],
            initialdir=OUTPUT_DIR,
            initialfile="port_scan_results.csv",
        )
        if not fp:
            return
        try:
            with open(fp, "w") as f:
                f.write("Port,Service,Banner,Latency_ms\n")
                for r in self._results:
                    f.write(f"{r['port']},{r['service']},"
                            f"\"{r['banner'].replace(chr(34), '')}\","
                            f"{r['latency_ms']}\n")
            self.log(f"Exported {len(self._results)} rows → {os.path.basename(fp)}", "ok")
        except Exception as e:
            self.log(f"Export error: {e}", "error")


# ─────────────────────────────────────────────
if __name__ == "__main__":
    app = PortScannerApp()
    app.mainloop()

