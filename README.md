# RKNN Toolkit2 Web UI for Luckfox Core3576

A modern, Dockerized Flask web interface to simplify and visualize the rknn-toolkit2 workflow for ONNX-to-RKNN model conversion, file management, and platform configuration. Optimized for Luckfox Core3576 and similar Rockchip platforms.

## Features
- **ONNX to RKNN conversion** (with live log streaming)
- **File management** (upload, download, delete for ONNX/RKNN)
- **Global config** (theme, server info, default platform)
- **Dark/Light mode** (persistent)
- **Server info display** (optional)
- **Dockerized deployment**

## Quickstart

### 1. Clone & Build
```sh
git clone <repo-url>
cd docker
./install.sh
```

### 2. Access the Web UI
Open [http://localhost:5000](http://localhost:5000) or use the IP shown after install.

### 3. Configuration
- Edit `config.json` or use `./manage.sh config set <key> <value>`
- Example: `./manage.sh config set default_platform "rk3576"`

### 4. Usage
- Upload ONNX models and convert to RKNN via the web UI.
- Download or delete models on the Files page.
- View server info and settings on the Settings page.

## Folder Structure
- `app.py` – Flask backend
- `convert.py` – ONNX to RKNN conversion script
- `templates/` – Jinja2 HTML templates
- `static/` – CSS/JS assets
- `uploads/` – Uploaded ONNX models (ignored by git)
- `converted/` – Converted RKNN models (ignored by git)
- `config.json` – Global config (ignored by git, see `config.example.json`)

## Development
- Use `docker-compose.yml` for container management
- Use `manage.sh` for config and container control

## License
MIT License

---
**Note:** This project is not affiliated with Rockchip or Luckfox. For rknn-toolkit2, see [https://github.com/airockchip/rknn-toolkit2](https://github.com/airockchip/rknn-toolkit2)
