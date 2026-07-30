# -*- coding: utf-8 -*-
"""Deploy EveryLane Macau to the Alibaba Cloud Singapore instance."""
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

# Competition Token Plan (Singapore region matches the server / organizer card)
API_KEY = os.environ.get("EL_QWEN_KEY", "")
BASE_URL = os.environ.get(
    "EL_QWEN_BASE",
    "https://token-plan.ap-southeast-1.maas.aliyuncs.com/compatible-mode/v1",
)
MODEL = os.environ.get("EL_QWEN_MODEL", "qwen3.7-plus")

INCLUDE_PREFIXES = (
    "backend/",
    "frontend/",
    "qwenpaw/",
    "requirements.txt",
    "README.md",
    "run.sh",
    "deploy/remote_setup.sh",
)
EXCLUDE_BITS = (
    "__pycache__",
    ".git",
    ".venv",
    "node_modules",
    ".env",
    "qa/_",
    ".pyc",
    "docs/",
    ".mp4",
)


def should_include(rel: str) -> bool:
    rel = rel.replace("\\", "/")
    if any(b in rel for b in EXCLUDE_BITS):
        return False
    if rel in ("requirements.txt", "README.md", "run.sh"):
        return True
    return any(rel.startswith(p) for p in INCLUDE_PREFIXES)


def make_tarball() -> bytes:
    buf = io.BytesIO()
    with tarfile.open(fileobj=buf, mode="w:gz") as tar:
        for dirpath, dirnames, filenames in os.walk(ROOT):
            dirnames[:] = [
                d
                for d in dirnames
                if d not in {".git", ".venv", "__pycache__", "node_modules", "docs", "qa"}
            ]
            for name in filenames:
                full = os.path.join(dirpath, name)
                rel = os.path.relpath(full, ROOT).replace("\\", "/")
                if should_include(rel):
                    tar.add(full, arcname=rel)
        setup = os.path.join(ROOT, "deploy", "remote_setup.sh")
        tar.add(setup, arcname="deploy/remote_setup.sh")
    return buf.getvalue()


def run(ssh: paramiko.SSHClient, cmd: str, timeout: int = 600) -> str:
    print(f"$ {cmd}")
    stdin, stdout, stderr = ssh.exec_command(cmd, timeout=timeout, get_pty=True)
    out = stdout.read().decode("utf-8", errors="replace")
    err = stderr.read().decode("utf-8", errors="replace")
    code = stdout.channel.recv_exit_status()
    if out.strip():
        print(out[-4000:])
    if err.strip():
        print(err[-2000:], file=sys.stderr)
    if code != 0:
        raise RuntimeError(f"command failed ({code}): {cmd}")
    return out


def main() -> None:
    if not PASSWORD:
        raise SystemExit("EL_PASS is required")
    if not API_KEY:
        raise SystemExit("EL_QWEN_KEY is required")

    print("packing…")
    blob = make_tarball()
    print(f"archive size: {len(blob) / 1024 / 1024:.1f} MB")

    ssh = paramiko.SSHClient()
    ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    print(f"connecting {HOST}…")
    for attempt in range(1, 8):
        try:
            ssh.connect(HOST, username=USER, password=PASSWORD, timeout=25, banner_timeout=40)
            break
        except Exception as e:
            print(f"connect attempt {attempt} failed: {e}")
            time.sleep(4)
    else:
        raise SystemExit("SSH connect failed")

    sftp = ssh.open_sftp()
    run(ssh, f"mkdir -p {REMOTE_DIR}")
    remote_tar = "/tmp/everylane.tgz"
    print("uploading…")
    with sftp.file(remote_tar, "wb") as f:
        f.write(blob)

    env_body = (
        f"QWEN_API_KEY={API_KEY}\n"
        f"QWEN_BASE_URL={BASE_URL}\n"
        f"QWEN_MODEL={MODEL}\n"
        "MAX_AGENT_STEPS=12\n"
    )
    with sftp.file(f"{REMOTE_DIR}/.env", "w") as f:
        f.write(env_body)
    run(ssh, f"chmod 600 {REMOTE_DIR}/.env")

    run(ssh, f"tar -xzf {remote_tar} -C {REMOTE_DIR}")
    run(ssh, f"chmod +x {REMOTE_DIR}/deploy/remote_setup.sh")
    run(ssh, f"bash {REMOTE_DIR}/deploy/remote_setup.sh", timeout=900)

    # quick public health (may fail if security group blocks 80)
    out = run(ssh, "curl -fsS http://127.0.0.1/api/health || curl -fsS http://127.0.0.1:8000/api/health")
    print("LOCAL_HEALTH:", out.strip())
    sftp.close()
    ssh.close()
    print("DEPLOY_DONE")


if __name__ == "__main__":
    main()
