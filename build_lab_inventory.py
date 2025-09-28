#!/usr/bin/env python3
"""
Build Ansible inventory from virtual machines launch trace.

This script extracts router information from the launch trace file
and generates an Ansible inventory in YAML format.
"""

import logging
import os
import re
import sys
from pathlib import Path

import yaml


def setup_logging():
    """Configure logging for the script."""
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s - %(levelname)s - %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S",
    )
    return logging.getLogger(__name__)


def clean_ansi_codes(input_file, output_file):
    """Remove ANSI color codes from the trace file."""
    logger.info(f"Cleaning ANSI codes from {input_file}")
    ansi_escape = re.compile(r"\x9B|\x1B\[[0-?]*[ -/]*[@-~]")

    try:
        with open(input_file, "r", encoding="utf-8") as src:
            with open(output_file, "w", encoding="utf-8") as dst:
                for line in src:
                    dst.write(ansi_escape.sub("", line))
        return True
    except (IOError, OSError) as error:
        logger.error(f"Error processing file: {error}")
        return False


def extract_router_info(trace_file):
    """Extract router names and IPv6 addresses from the trace file."""
    routers = {}
    VM_PATTERN = "Router name"
    ADDRESS_PATTERN = "mgmt G1 IPv6 LL address"

    try:
        with open(trace_file, "r", encoding="utf-8") as src:
            lines = src.readlines()

            vm_name = None
            for line in lines:
                line = line.strip()

                if re.search(VM_PATTERN, line) and not vm_name:
                    parts = line.split(":", 1)
                    if len(parts) > 1:
                        vm_name = parts[1].strip().split(".")[0]

                elif re.search(ADDRESS_PATTERN, line) and vm_name:
                    parts = line.split(" :", 1)
                    if len(parts) > 1:
                        address = parts[1].strip().split("%")[0]
                        vm_address = f"{address}%enp0s1"

                        routers[vm_name] = {
                            "ansible_host": vm_address,
                            "ansible_port": 2222,
                        }
                        vm_name = None

        return routers
    except (IOError, OSError) as error:
        logger.error(f"Error reading trace file: {error}")
        return {}


def generate_inventory(routers, output_file):
    """Generate the Ansible inventory file in YAML format."""
    if not routers:
        logger.error("No router information found. Cannot generate inventory.")
        return False

    inventory = {
        "routers": {
            "hosts": routers,
            "vars": {
                "ansible_ssh_user": "{{ vm_user }}",
                "ansible_ssh_pass": "{{ vm_pass }}",
                "ansible_connection": "network_cli",
                "ansible_network_os": "ios",
            },
        }
    }

    try:
        # Ensure the directory exists
        os.makedirs(os.path.dirname(output_file), exist_ok=True)

        with open(output_file, "w", encoding="utf-8") as dst:
            yaml.dump(inventory, dst, sort_keys=False)

        logger.info(f"Inventory successfully written to {output_file}")
        return True
    except (IOError, OSError) as error:
        logger.error(f"Error writing inventory file: {error}")
        return False


if __name__ == "__main__":
    logger = setup_logging()

    # Define file paths using pathlib for better path handling
    trace_dir = Path("trace")
    inventory_dir = Path("inventory")

    trace_file = trace_dir / "launch_output.log"
    clean_trace_file = trace_dir / "launch_output.save"
    inventory_file = inventory_dir / "lab.yml"

    # Check if trace file exists
    if not trace_file.exists():
        logger.error("Virtual machines launch trace file does not exist.")
        logger.error("Are the virtual machines running?")
        sys.exit(1)

    # Remove existing clean trace file if it exists
    if clean_trace_file.exists():
        clean_trace_file.unlink()

    # Clean ANSI codes from the trace file
    if not clean_ansi_codes(trace_file, clean_trace_file):
        sys.exit(1)

    # Extract router information
    routers = extract_router_info(clean_trace_file)

    # Generate inventory file
    if not generate_inventory(routers, inventory_file):
        sys.exit(1)

    logger.info("Inventory generation complete.")
    sys.exit(0)
