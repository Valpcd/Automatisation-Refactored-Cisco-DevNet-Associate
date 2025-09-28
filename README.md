# Lab03: IaC with Ansible for Cisco IOS XE Routers

## Overview

This project uses Infrastructure as Code (IaC) principles with Ansible to automate the deployment and configuration of Cisco IOS XE virtual routers. The automation workflow is managed using a GitLab CI/CD pipeline.

The lab book address is: [IaC Lab 3 – Using GitLab CI to run Ansible playbooks and build new IOS XE Virtual Routers](https://md.inetdoc.net/s/ltLcEoVDG)

## Lab Topology

<img src="https://md.inetdoc.net/uploads/eca5b443-07b3-40b3-9f6a-93e27846f722.png" width="60%" alt="IaC Lab 3 topology" />

## Workflow Description

The automation process follows these main steps:

1. **Environment Preparation** ([01_prepare.yml](./01_prepare.yml)):

   - Verifies accessibility of reference IOS XE qcow2 format virtual router images
   - Creates necessary directories and symbolic links
   - Configures virtual switches on the hypervisor
   - Sets up network infrastructure for the virtual environment

2. **VM Deployment** ([02_declare_run.yml](./02_declare_run.yml)):

   - Copies reference images for each virtual router
   - Generates YAML configuration for virtual machines
   - Assembles configurations into a lab declaration file
   - Launches virtual routers using the configuration
   - Updates the inventory with the newly created VMs

3. **Router Configuration** ([03_configure_routers.yml](./03_configure_routers.yml)):
   - Waits for routers to become accessible via SSH
   - Configures hostnames according to VM names
   - Sets up network interfaces with proper descriptions
   - Configures IPv4 and IPv6 addressing on interfaces
   - Establishes default routes for internet connectivity
   - Verifies connectivity through ping tests

## CI/CD Pipeline

The GitLab CI/CD pipeline is designed to run these playbooks sequentially to ensure a consistent and repeatable deployment process. The pipeline includes stages for:

- Establishing the Ansible environment
- Verifying connectivity to hypervisors
- Preparing the hypervisor environment
- Deploying and starting virtual routers
- Configuring the network on the routers
