# Data Collection Unit

A Python desktop application for real-time monitoring and management of an industrial press machine. Runs on a dedicated on-site terminal.

## What it does

- Displays live machine data (temperatures, pressures, production count) read from a PLC
- Tracks work orders, production records, and machine downtime
- Streams telemetry to a ThingsBoard IoT server
- Stores production history in a local database
- Supports touch-screen use with an on-screen keyboard

## Stack

- **GUI** — Tkinter
- **PLC communication** — Modbus TCP
- **Database** — SQLite / SQLAlchemy
- **IoT** — ThingsBoard REST API

## Setup

**1. Install dependencies**
```bash
pip install -r requirements.txt
```

**2. Configure environment**
```bash
cp .env.example .env
```
Fill in `.env` with your network addresses and credentials.

**3. Configure personnel**
```bash
cp credentials.json.example credentials.json
```

**4. Run**
```bash
python main.py
```

## Requirements

Python 3.10+
