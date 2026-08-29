# -*- coding: utf-8 -*-
"""Minimal-touch semifinal update for the EveryLane Macau server.

Unlike deploy_now.py (full bootstrap), this script ONLY:
  1. uploads the app tarball (backend / frontend / qwenpaw / run files),
  2. extracts it into /opt/everylane-macau,
  3. appends EL_LIVE_WEATHER=1 to the existing .env if missing (keys untouched),
  4. restarts the `everylane` systemd service.

It never reinstalls packages, never touches nginx or any other process on the
host, so everything else running on the server is left completely alone.
"""
from __future__ import annotations

import io
import os
import sys
import tarfile
import time

import paramiko

HOST = os.environ.get("EL_HOST", "47.79.228.128")
USER = os.environ.get("EL_USER", "root")
PASSWORD = os.environ.get("EL_PASS", "")
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
REMOTE_DIR = "/opt/everylane-macau"

INCLUDE_PREFIXES = ("backend/", "frontend/", "qwenpaw/",
                    "requirements.txt", "README.md", "run.sh")
EXCLUDE_BITS = ("__pycache__", ".git", ".venv", "node_modules", ".env",
                "qa/_", ".pyc", "docs/", ".mp4", "tts_cache")
# POI photos (~22 MB) are immutable and already on the server; skip them by
# default so a code update uploads in seconds. Set EL_INCLUDE_ASSETS=1 to
# force a full asset sync.
SKIP_ASSETS = os.environ.get("EL_INCLUDE_ASSETS", "") != "1"


def should_include(rel: str) -> bool:
    rel = rel.replace("\\", "/")
    if any(b in rel for b in EXCLUDE_BITS):
        return False
    if SKIP_ASSETS and rel.startswith("frontend/assets/"):
        return False
    if rel in ("requirements.txt", "README.md", "run.sh"):
        return True
    return any(rel.startswith(p) for p in INCLUDE_PREFIXES)


def make_tarball() -> bytes:
    buf = io.BytesIO()
    with tarfile.open(fileobj=buf, mode="w:gz") as tar:
        for dirpath, dirnames, filenames in os.walk(ROOT):
            dirnames[:] = [d for d in dirnames
                           if d not in {".git", ".venv", "__pycache__",
                                        "node_modules", "docs", "qa", "logs"}]
            for name in filenames:
                full = os.path.join(dirpath, name)
                rel = os.path.relpath(full, ROOT).replace("\\", "/")
                if should_include(rel):
                    tar.add(full, arcname=rel)
    return buf.getvalue()


def run(ssh: paramiko.SSHClient, cmd: str, timeout: int = 300) -> str:
    print(f"$ {cmd}")
    _, stdout, stderr = ssh.exec_command(cmd, timeout=timeout, get_pty=True)
    out = stdout.read().decode("utf-8", errors="replace")
    err = stderr.read().decode("utf-8", errors="replace")
    code = stdout.channel.recv_exit_status()
    if out.strip():
        print(out[-3000:])
    if err.strip():
        print(err[-1500:], file=sys.stderr)
    if code != 0:
        raise RuntimeError(f"command failed ({code}): {cmd}")
    return out


def main() -> None:
    if not PASSWORD:
        raise SystemExit("EL_PASS is required")
    print("packing…")
    blob = make_tarball()
    print(f"archive size: {len(blob) / 1024 / 1024:.1f} MB")

    ssh = paramiko.SSHClient()
    ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    print(f"connecting {HOST}…")
    for attempt in range(1, 8):
        try:
            ssh.connect(HOST, username=USER, password=PASSWORD,
                        timeout=25, banner_timeout=40)
            break
        except Exception as e:
            print(f"connect attempt {attempt} failed: {e}")
            time.sleep(4)
    else:
        raise SystemExit("SSH connect failed")

    remote_tar = "/tmp/everylane_update.tgz"
    run(ssh, f"rm -f {remote_tar}")  # clear any stale/partial upload
    sftp = ssh.open_sftp()
    print("uploading…")
    with sftp.file(remote_tar, "wb") as f:
        f.write(blob)
    sftp.close()

    run(ssh, f"tar -xzf {remote_tar} -C {REMOTE_DIR} && rm -f {remote_tar}")
    # enable live weather without rewriting existing credentials
    run(ssh, f"grep -q '^EL_LIVE_WEATHER=' {REMOTE_DIR}/.env "
             f"|| echo 'EL_LIVE_WEATHER=1' >> {REMOTE_DIR}/.env")
    run(ssh, "systemctl restart everylane")
    time.sleep(4)
    run(ssh, "systemctl is-active everylane")
    out = run(ssh, "curl -fsS http://127.0.0.1:8000/api/health")
    print("HEALTH:", out.strip()[-300:])
    out = run(ssh, "curl -fsS http://127.0.0.1:8000/api/impact/summary | head -c 200")
    print("IMPACT:", out.strip()[:200])
    ssh.close()
    print("UPDATE_DONE")


if __name__ == "__main__":
    main()
