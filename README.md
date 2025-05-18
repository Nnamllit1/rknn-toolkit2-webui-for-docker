# RKNN Toolkit2 Web UI for Luckfox Core3576

A modern, Dockerized Flask web interface to simplify and visualize the rknn-toolkit2 workflow for ONNX-to-RKNN model conversion, file management, and platform configuration. Optimized for Luckfox Core3576 and similar Rockchip platforms.

## Features
- **ONNX to RKNN conversion** (with live log streaming)
- **File management** (upload, download, delete for ONNX/RKNN)
- **Global config** (theme, server info, default platform)
- **Dark/Light mode** (persistent)
- **Server info display** (optional)
- **Dockerized deployment**
- **MySQL/MariaDB support via SQLAlchemy**
- **ARM/Embedded ready (host network support)**

## Quickstart

### 1. Clone & Build
```sh
git clone https://github.com/Nnamllit1/rknn-toolkit2-webui-for-docker.git
cd rknn-toolkit2-webui-for-docker
chmod +x ./install.sh && ./install.sh
```

## Alternative: One-Line Install (Linux, with wget)

For Linux users who want to install everything automatically:

```sh
wget -O - https://raw.githubusercontent.com/Nnamllit1/rknn-toolkit2-webui-for-docker/main/auto_install.sh | bash
```

- Downloads the repository, sets permissions, and runs the install script automatically.
- After completion, the Web UI is available as described below.

---

### 2. Access the Web UI
Open [http://localhost:5000](http://localhost:5000) or use your device's IP (e.g. http://192.168.x.x:5000).

### 3. Docker Compose Notes (ARM/Embedded)
- On embedded systems (e.g. Luckfox), `network_mode: host` is used so that port mapping and name resolution work reliably.
- In your `docker-compose.yml`, set for the web service: `network_mode: host` and `DB_HOST=127.0.0.1`.
- The database also runs in host network mode.

### 4. Configuration
- Edit `config.json` or use `./manage.sh config set <key> <value>`
- Example: `./manage.sh config set default_platform "rk3576"`

### 5. Usage
- Upload ONNX models and convert to RKNN via the web UI.
- Download or delete models on the Files page.
- View server info and settings on the Settings page.

## Database
- Metadata is stored in a MySQL/MariaDB database (via SQLAlchemy).
- The Python package `cryptography` is now required (see `requirements.txt`).

## Development
- Use `docker-compose.yml` for container management.
- Use `manage.sh` for config and container control.

## License
MIT License

---
**Note:** This project is not affiliated with Rockchip or Luckfox. For rknn-toolkit2, see [https://github.com/airockchip/rknn-toolkit2](https://github.com/airockchip/rknn-toolkit2)