vmware-machine-path-name-manager
================================

This is a WIP and incomplete. Do NOT run this Python code on your machine without backing up the computer first, *particularly* your VMs and the VM configuration files. You will see which files may be modified by this script by looking at the code.

The problem: VMWare allows you to rename virtual machines and the path to the VM never changes. After adding enough VMs, and perhaps renaming some from the Virtual Machine Library interface, it can be confusing which VM is located where. Also, VMWare's popup on the OS X dock uses the original machine name and you cannot tell which machine is which.

This Python code is intended to solve both problems: 1) Make VM folder names match the VM names and 2) Make the VMWare popup names match the VM names as shown in the Machine Library. The script currently solves problem #1 and there is some code to solve #2 but it is incomplete.
