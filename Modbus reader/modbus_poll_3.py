"""
Modbus TCP & RTU Register Poller & Writer
------------------------------------------
Connects to a Modbus TCP device (or Modbus RTU-over-TCP gateway),
reads holding/input registers, writes single/multiple registers,
verifies write ACK confirmations, and saves results to JSON/CSV.

Works with pymodbus if installed, or falls back to pure Python standard library sockets
(zero extra pip packages required).
"""

import json
import time
import socket
import struct
import sys
import argparse
from datetime import datetime

# ======================= CONFIG =======================
IP_ADDRESS = "192.168.4.1"        # Device IP
PORT = 502                        # Modbus TCP port (default 502)
SLAVE_ID = 1                      # Unit / slave ID

START_REGISTER = 2000              # First register address (0-based offset)
END_REGISTER = 6000                # Last register address (inclusive)

REGISTER_TYPE = "holding"          # "holding" or "input"
CHUNK_SIZE = 100                   # Registers per request

TIMEOUT = 5                        # Seconds to wait for a response
RETRIES = 3                        # Retries per chunk before giving up
DELAY_BETWEEN_REQUESTS = 0.05      # Seconds to pause between requests
OUTPUT_FILE = "registers_2.json"   # Output JSON file
# ========================================================


def calc_modbus_crc16(data: bytes) -> int:
    """Calculates standard Modbus CRC-16 (poly 0xA001, init 0xFFFF)."""
    crc = 0xFFFF
    for byte in data:
        crc ^= byte
        for _ in range(8):
            if crc & 0x0001:
                crc = (crc >> 1) ^ 0xA001
            else:
                crc >>= 1
    return crc & 0xFFFF


class SocketModbusClient:
    """
    Pure Python standard-library Modbus TCP and RTU-over-TCP Client.
    Requires no third-party libraries (no pip install required).
    """
    def __init__(self, host=IP_ADDRESS, port=PORT, timeout=TIMEOUT, is_rtu=False):
        self.host = host
        self.port = int(port)
        self.timeout = float(timeout)
        self.is_rtu = is_rtu
        self.sock = None
        self._tid = 1

    def connect(self):
        try:
            self.close()
            self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
            self.sock.settimeout(self.timeout)
            self.sock.connect((self.host, self.port))
            return True
        except Exception as e:
            self.sock = None
            return False

    def close(self):
        if self.sock:
            try:
                self.sock.close()
            except Exception:
                pass
            self.sock = None

    def _next_tid(self):
        tid = self._tid
        self._tid = (self._tid + 1) & 0xFFFF
        return tid or 1

    def read_holding_registers(self, address, count, slave=1, **kwargs):
        return self._read(address, count, func_code=3, slave_id=slave)

    def read_input_registers(self, address, count, slave=1, **kwargs):
        return self._read(address, count, func_code=4, slave_id=slave)

    def write_register(self, address, value, slave=1, **kwargs):
        return self._write_single(address, value, slave_id=slave)

    def write_registers(self, address, values, slave=1, **kwargs):
        return self._write_multiple(address, values, slave_id=slave)

    def _read(self, address, count, func_code=3, slave_id=1):
        class ModbusResult:
            def __init__(self, registers=None, error=None):
                self.registers = registers or []
                self.error = error
            def isError(self):
                return self.error is not None
            def __str__(self):
                return self.error or f"Registers({len(self.registers)})"

        if not self.sock:
            if not self.connect():
                return ModbusResult(error="Not connected to host")

        pdu = struct.pack(">BHH", func_code, address, count)
        if self.is_rtu:
            frame = struct.pack(">B", slave_id) + pdu
            crc = calc_modbus_crc16(frame)
            tx = frame + struct.pack("<H", crc)
        else:
            tid = self._next_tid()
            mbap = struct.pack(">HHHB", tid, 0, len(pdu) + 1, slave_id)
            tx = mbap + pdu

        try:
            self.sock.sendall(tx)
            rx = self.sock.recv(2048)
            if not rx:
                return ModbusResult(error="Empty response from device")

            if self.is_rtu:
                if len(rx) < 5:
                    return ModbusResult(error=f"RTU frame too short ({len(rx)} bytes)")
                fc = rx[1]
                if fc >= 0x80:
                    return ModbusResult(error=f"Modbus Exception 0x{fc:02X} code {rx[2]}")
                byte_cnt = rx[2]
                val_bytes = rx[3:3+byte_cnt]
            else:
                if len(rx) < 9:
                    return ModbusResult(error=f"TCP frame too short ({len(rx)} bytes)")
                fc = rx[7]
                if fc >= 0x80:
                    return ModbusResult(error=f"Modbus Exception 0x{fc:02X} code {rx[8]}")
                byte_cnt = rx[8]
                val_bytes = rx[9:9+byte_cnt]

            regs = []
            for i in range(0, len(val_bytes), 2):
                if i + 2 <= len(val_bytes):
                    regs.append(struct.unpack(">H", val_bytes[i:i+2])[0])
            return ModbusResult(registers=regs)
        except Exception as e:
            return ModbusResult(error=str(e))

    def _write_single(self, address, value, slave_id=1):
        """Dispatches Function 06 (Write Single Register) and verifies the device ACK."""
        class ModbusWriteResult:
            def __init__(self, address, value, ack_ok=False, error=None, raw_rx=b""):
                self.address = address
                self.value = value
                self.ack_ok = ack_ok
                self.error = error
                self.raw_rx = raw_rx
            def isError(self):
                return self.error is not None or not self.ack_ok
            def __str__(self):
                if self.ack_ok:
                    return f"ACK CONFIRMED: Register [{self.address}] = {self.value}"
                return self.error or "Write failed (No ACK)"

        if not self.sock:
            if not self.connect():
                return ModbusWriteResult(address, value, False, "Not connected")

        val_16 = value & 0xFFFF
        pdu = struct.pack(">BHH", 6, address, val_16)

        if self.is_rtu:
            frame = struct.pack(">B", slave_id) + pdu
            crc = calc_modbus_crc16(frame)
            tx = frame + struct.pack("<H", crc)
        else:
            tid = self._next_tid()
            mbap = struct.pack(">HHHB", tid, 0, len(pdu) + 1, slave_id)
            tx = mbap + pdu

        try:
            self.sock.sendall(tx)
            rx = self.sock.recv(1024)
            if not rx:
                return ModbusWriteResult(address, value, False, "No response from device")

            # Check Modbus Write ACK (Exact echo of function 06, address, and value)
            if self.is_rtu:
                if len(rx) >= 6:
                    rx_fc = rx[1]
                    if rx_fc >= 0x80:
                        return ModbusWriteResult(address, value, False, f"Modbus Exception 0x{rx_fc:02X} code {rx[2]}", rx)
                    rx_addr, rx_val = struct.unpack(">HH", rx[2:6])
                    if rx_fc == 6 and rx_addr == address and rx_val == val_16:
                        return ModbusWriteResult(address, value, True, raw_rx=rx)
            else:
                if len(rx) >= 12:
                    rx_fc = rx[7]
                    if rx_fc >= 0x80:
                        return ModbusWriteResult(address, value, False, f"Modbus Exception 0x{rx_fc:02X} code {rx[8]}", rx)
                    rx_addr, rx_val = struct.unpack(">HH", rx[8:12])
                    if rx_fc == 6 and rx_addr == address and rx_val == val_16:
                        return ModbusWriteResult(address, value, True, raw_rx=rx)

            return ModbusWriteResult(address, value, False, "Received response but ACK did not match", rx)
        except Exception as e:
            return ModbusWriteResult(address, value, False, str(e))

    def _write_multiple(self, address, values, slave_id=1):
        """Dispatches Function 16 (0x10 Write Multiple Registers) and verifies device ACK."""
        class ModbusWriteMultipleResult:
            def __init__(self, address, count, ack_ok=False, error=None):
                self.address = address
                self.count = count
                self.ack_ok = ack_ok
                self.error = error
            def isError(self):
                return self.error is not None or not self.ack_ok

        if not self.sock:
            if not self.connect():
                return ModbusWriteMultipleResult(address, len(values), False, "Not connected")

        count = len(values)
        byte_count = count * 2
        payload = struct.pack(">BHHB", 16, address, count, byte_count)
        for v in values:
            payload += struct.pack(">H", v & 0xFFFF)

        if self.is_rtu:
            frame = struct.pack(">B", slave_id) + payload
            crc = calc_modbus_crc16(frame)
            tx = frame + struct.pack("<H", crc)
        else:
            tid = self._next_tid()
            mbap = struct.pack(">HHHB", tid, 0, len(payload) + 1, slave_id)
            tx = mbap + payload

        try:
            self.sock.sendall(tx)
            rx = self.sock.recv(1024)
            if not rx:
                return ModbusWriteMultipleResult(address, count, False, "No response")
            # In Modbus, ACK for Func 16 echoes (Func 16, start_addr, count)
            if self.is_rtu and len(rx) >= 6:
                if rx[1] == 16:
                    return ModbusWriteMultipleResult(address, count, True)
            elif not self.is_rtu and len(rx) >= 12:
                if rx[7] == 16:
                    return ModbusWriteMultipleResult(address, count, True)
            return ModbusWriteMultipleResult(address, count, False, "Invalid ACK")
        except Exception as e:
            return ModbusWriteMultipleResult(address, count, False, str(e))


def get_modbus_client(ip=IP_ADDRESS, port=PORT, timeout=TIMEOUT, is_rtu=False):
    """Instantiates a Modbus Client (supports pymodbus if installed, falls back to SocketModbusClient)."""
    try:
        from pymodbus.client import ModbusTcpClient
        return ModbusTcpClient(ip, port=int(port), timeout=timeout)
    except ImportError:
        return SocketModbusClient(host=ip, port=int(port), timeout=timeout, is_rtu=is_rtu)


def _read_block(client, reg_type, address, count, slave_id):
    """Calls the right read method adapting to the installed client."""
    method = client.read_holding_registers if reg_type == "holding" else client.read_input_registers
    for kwarg_name in ("slave", "unit", "device_id"):
        try:
            return method(address=address, count=count, **{kwarg_name: slave_id})
        except TypeError:
            continue
    return method(address=address, count=count)


def read_registers(client, start, end, reg_type="holding", slave_id=1, chunk_size=CHUNK_SIZE):
    """Reads registers from start to end (inclusive) in chunks with retries."""
    values = []
    address = start
    total = end - start + 1

    while address <= end:
        count = min(chunk_size, end - address + 1)
        result = None
        last_error = None
        for attempt in range(RETRIES):
            try:
                result = _read_block(client, reg_type, address, count, slave_id)
                if not result.isError():
                    break
                last_error = result
            except Exception as exc:
                last_error = exc
                try:
                    client.close()
                except Exception:
                    pass
                client.connect()
            time.sleep(DELAY_BETWEEN_REQUESTS)

        if result is None or result.isError():
            print(f"\nFailed to read registers {address}-{address + count - 1}: {last_error}")
            values.extend([None] * count)
        else:
            values.extend(result.registers)

        address += count
        print(f"Read {min(address - start, total)}/{total} registers...", end="\r")
        time.sleep(DELAY_BETWEEN_REQUESTS)

    print()
    return values


def write_single_register_with_ack(client, address, value, slave_id=1):
    """Writes a single register and verifies the device ACK confirmation."""
    for attempt in range(1, RETRIES + 1):
        try:
            res = client.write_register(address=address, value=value, slave=slave_id)
            if not res.isError():
                return True, f"[✓ ACK CONFIRMED] Written Register {address} = {value} successfully"
            last_err = str(res)
        except Exception as e:
            last_err = str(e)
            try:
                client.close()
            except Exception:
                pass
            client.connect()
        time.sleep(DELAY_BETWEEN_REQUESTS)
    return False, f"[✗ WRITE FAILED] Could not write Register {address} = {value}: {last_err}"


def main():
    parser = argparse.ArgumentParser(description="Modbus TCP/RTU Register Poller & Writer with ACK")
    parser.add_argument("--ip", default=IP_ADDRESS, help="Target device IP")
    parser.add_argument("--port", type=int, default=PORT, help="Target port")
    parser.add_argument("--slave", type=int, default=SLAVE_ID, help="Slave / Unit ID")
    parser.add_argument("--start", type=int, default=START_REGISTER, help="Start register")
    parser.add_argument("--end", type=int, default=END_REGISTER, help="End register")
    parser.add_argument("--write", action="store_true", help="Perform write operation")
    parser.add_argument("--reg", type=int, help="Register to write")
    parser.add_argument("--val", type=int, help="Value to write")
    parser.add_argument("--out", default=OUTPUT_FILE, help="Output JSON file")
    args = parser.parse_args()

    client = get_modbus_client(ip=args.ip, port=args.port, timeout=TIMEOUT)
    if not client.connect():
        print(f"Could not connect to {args.ip}:{args.port}")
        return

    print(f"Connected to {args.ip}:{args.port} (Unit ID: {args.slave})")

    if args.write:
        if args.reg is None or args.val is None:
            print("Error: --write requires --reg <address> and --val <value>")
            return
        print(f"Transmitting Write Request to Register [{args.reg}] = {args.val}...")
        ok, msg = write_single_register_with_ack(client, args.reg, args.val, slave_id=args.slave)
        print(msg)
    else:
        print(f"Reading registers {args.start} to {args.end}...")
        values = read_registers(client, args.start, args.end, REGISTER_TYPE, args.slave, CHUNK_SIZE)
        values_dict = {}
        for i in range(0, len(values), 2):
            reg_num = args.start + i
            v1 = values[i]
            v2 = values[i + 1] if i + 1 < len(values) else None
            if v1 is not None and v2 is not None:
                values_dict[str(reg_num)] = (v1 << 16) | v2
            else:
                values_dict[str(reg_num)] = v1

        data = {
            "ip": args.ip,
            "port": args.port,
            "slave_id": args.slave,
            "start_register": args.start,
            "end_register": args.end,
            "timestamp": datetime.now().isoformat(),
            "values": values_dict
        }
        with open(args.out, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=2)
        print(f"Saved {len(values_dict)} register values to {args.out}")

    client.close()


if __name__ == "__main__":
    main()
