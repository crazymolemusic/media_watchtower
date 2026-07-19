#!/usr/bin/env python3
import os
import sys
import subprocess
import socket

def check_dependencies():
    try:
        import flask
        import requests
    except ImportError:
        print("[*] Base libraries missing. Initializing automated installation workflow...")
        subprocess.run([
            sys.executable, "-m", "pip", "install", 
            "flask", "requests", "--break-system-packages"
        ], check=True)
        os.execv(sys.executable, [sys.executable] + sys.argv)

check_dependencies()

def verify_target_port(host, port):
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        return s.connect_ex((host, port)) != 0

if __name__ == "__main__":
    project_dir = os.path.dirname(os.path.abspath(__file__))
    os.chdir(project_dir)

    if sys.argv[-1] == "--stop":
        print("[*] Halting operational active background Watchtower nodes...")
        if sys.platform == "win32":
            subprocess.run(["taskkill", "/IM", "python.exe", "/F"], capture_output=True)
        else:
            subprocess.run(["pkill", "-f", "app.routes"], capture_output=True)
        print("[+] Environment wiped clean.")
        sys.exit(0)

    if "--daemon" not in sys.argv:
        print("[*] Provisioning background memory spaces...")
        target_port = 8228
        if not verify_target_port("127.0.0.1", target_port):
            target_port = 9000
            if not verify_target_port("127.0.0.1", target_port):
                print(f"[!] Error: Default ports are locked. Clean instances using: python run.py --stop")
                sys.exit(1)

        log_file = open(os.path.join(project_dir, "watchtower_runtime.log"), "w")
        subprocess.Popen(
            [sys.executable, "run.py", "--daemon", str(target_port)],
            stdout=log_file,
            stderr=log_file,
            start_new_session=True if sys.platform != "win32" else None
        )
        
        print("================================================================================")
        print("🛡️ MEDIA WATCHTOWER ENGINE ACTIVE IN BACKGROUND")
        print("================================================================================")
        print(f"📡 Web Interface Access Target Link: http://127.0.0.1:{target_port}")
        print("💡 Success: You may now close this terminal interface pane window entirely!")
        print("================================================================================")
        sys.exit(0)

    assigned_port = int(sys.argv[-1])
    
    from app.engine import start_telemetry_loop
    import threading
    threading.Thread(target=start_telemetry_loop, daemon=True).start()

    from app.routes import web_app
    web_app.run(host="127.0.0.1", port=assigned_port, debug=False, use_reloader=False)
