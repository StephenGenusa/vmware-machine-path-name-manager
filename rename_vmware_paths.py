#!/usr/bin/python
#
# Written for OS X but should be easy to modify for other operating systems
#
# By Stephen Genusa development.genusa.com
#

import sys, argparse, os, shutil, datetime, psutil, getpass

prog_ver = '.90'


def File_ReplaceStringValue (input_file, old_value, new_value):
    with open(input_file, 'r') as file:
        file_data = file.read().replace(old_value, new_value)
    with open(input_file, 'w') as file:
        file.write(file_data)
    
def List_CountExtensions (list, search_value):
    count = 0
    for list_item in list:
        filename_elements = list_item.split('.')
        if filename_elements.count > 1 and filename_elements[-1] and filename_elements[-1] == search_value:
            count += 1
    return count

def List_GetFileWithExtension (list, search_value):
    for list_item in list:
        filename_elements = list_item.split('.')
        if filename_elements.count > 1 and filename_elements[-1] and filename_elements[-1] == search_value:
            return list_item
    
def List_GetLineNumContainingConfigValue (list, search_value):
    #print list
    line_num = -1
    for list_item in list:                
        line_elements = list_item.split('=')
        #print line_elements[0]
        line_num += 1
        if line_elements[0].strip() == search_value:
            return line_num
    return -1

def TerminateIfVMwareIsRunning():
    # Make sure VMware is not running so the update doesn't conflict with in memory settings
    for proc in psutil.get_process_list():
        if proc.name()=='vmware-vmx' or proc.name()=='VMware Fusion':
            print "VMware is currently running.\nPlease exit before updating VMware paths and settings."
            print
            sys.exit()


def BackupVMInventoryFile():
    shutil.copy (vmInventoryFile, vmInventoryFile + '-' + datetime.datetime.today().strftime('%Y%m%d%H%M%S') + '.backup')



def UpdateVM(full_vm_path, bootdelay):
    print 'Processing ', full_vm_path
    
    # Get <vmname>.vmx or <vmname>.cfg
    # Check the directory and make sure only one vmx file exists
    #   Old VMs use .cfg but even my oldest VMs do no have a cfg so 
    #   I am not sure if the format is the same as vmx or not
    #   so cfg files will be ignored
    #vm_files = []
    vm_files = os.listdir(full_vm_path)
    if List_CountExtensions(vm_files, 'vmx') > 1:
        print 'More than one VMX file in directory. Processing terminated.'
        sys.exit()
       
    # Get the VMX filename    
    vmx_filename = List_GetFileWithExtension(vm_files, 'vmx') 
    print "VMX machine configuration file is", vmx_filename
    
    
    #with open(full_vm_path + '/' + vmx_filename, 'r') as file:
    #    vmx_data = file.readlines()
    #file.close()

    if bootdelay > -1:
        line_num = List_GetLineNumContainingConfigValue(vmx_data, 'bios.bootdelay')
        if line_num != -1:
            vmx_data[line_num] = 'bios.bootdelay = ' + 5*1000
        else:
            vmx_data.append('bios.bootdelay = ' + str(5*1000))
            
        #with open('/Users/' + getpass.getuser() + '/Desktop/test_data.txt', 'w') as file:
        #    file.writelines(vmx_data)
        
    
    

print 'VMware Virtual Machine Utility ' + prog_ver


# Set path to VM inventory file
vmInventoryFile = '/Users/' + getpass.getuser() + '/Library/Application Support/VMware Fusion/vmInventory'

if not os.path.isfile(vmInventoryFile):
    print 'The vmInventory file was not found. Processing terminated.'
    sys.exit()


# Set default path for directory where VMware stores VMs on OS X
if sys.platform == 'darwin':
    vmrootpath = '/Users/' + getpass.getuser() + '/Documents/Virtual Machines.localized'

# Parse commandline arguments
parser = argparse.ArgumentParser(description='\tRenames the directory and VM files based on the VM name set in the Virtual Machine Library.\n')
parser.add_argument('--version', action='version', version='%(prog)s v' + prog_ver)
parser.add_argument("-n", "--namedvms", action='append', help="rename VM's physical files based on VMware's display name")
parser.add_argument("-b", "--bootdelay", action='store', default=-1, help="change bios.bootdelay")
parser.add_argument("-r", "--recursive", action='store_true', help="change all VM's in root VMware directory")
parser.add_argument("-v", "--vmrootpath", action='store', default=vmrootpath, help="root path where VMware store's VMs")
args = parser.parse_args()

print 
#print args


#TerminateIfVMwareIsRunning()

# Verify that root path to VMware VMs exists
if vmrootpath == '' or not os.path.exists(vmrootpath):
    print 'Either the specified vmrootpath does not exist or it needs to be set using the -v argument'
    sys.exit()


if args.recursive:
    #vm_directories = os.listdir(vmrootpath)
    BackupVMInventoryFile()
    #for vm_directory in vm_directories:
    #    if os.path.isdir(vmrootpath + '/' + vm_directory):
    #        UpdateVM(vmrootpath + '/' + vm_directory, args.bootdelay)
    
    # Read the vm inventory file 
    with open(vmInventoryFile, 'r') as file:
        vm_inventory_data = file.readlines()    
    vm_counter = 1
    
    # Parse inventory file for valid machine names and config files
    while vm_counter < 100:
        vmConfig_linenum = List_GetLineNumContainingConfigValue (vm_inventory_data, 'vmlist' + str(vm_counter) + '.config')
        vmDisplay_linenum = List_GetLineNumContainingConfigValue (vm_inventory_data, 'vmlist' + str(vm_counter) + '.DisplayName')
        # If valid machine name and config file then process
        if vmConfig_linenum > -1 and vmDisplay_linenum > -1 and vm_inventory_data[vmConfig_linenum].find('/') > -1:
            #print vm_inventory_data[vmDisplay_linenum].strip()
            display_name = vm_inventory_data[vmDisplay_linenum].split('"')[-2]
            vm_machine_config_path = vm_inventory_data[vmConfig_linenum].split('/')[-2]
            if vm_machine_config_path.find('.vmwarevm') == -1 or vm_machine_config_path.replace('.vmwarevm', '') != display_name:
                print "VM Machine:", display_name
                vm_old_config_path = vm_inventory_data[vmConfig_linenum].split('=')[1].strip()
                print "Old Config Path:", vm_old_config_path
                config_elements = vm_inventory_data[vmConfig_linenum].split('/')
                config_elements[-2] = display_name.replace('/', '_') + '.vmwarevm'
                vm_inventory_data[vmConfig_linenum] = "/".join(config_elements)
                vm_new_config_path = vm_inventory_data[vmConfig_linenum].split('=')[1].strip()
                print "New Config Path:", vm_new_config_path
                print 
                old_dir, old_file = os.path.split(vm_old_config_path)
                new_dir, new_file = os.path.split(vm_new_config_path)
                if old_dir != new_dir:
                    os.rename(old_dir.replace('"', ''), new_dir.replace('"', ''))
            #print display_name
        vm_counter += 1
    #print vm_inventory_data
    with open(vmInventoryFile, 'w') as file:
        file.writelines(vm_inventory_data)
        
            
else:
    if args.namedvms != None:
        # Validate that each VMware machine directory exists
        for vm_path in args.namedvms:
            if not os.path.exists(vmrootpath + '/' + vm_path):
                print 'The virtual machine path \"' + vm_path + '\" was not found. No VMs were updated.'
                print
                sys.exit()
            else:
                print 'The path for', vm_path, 'has been validated.'
                
        BackupVMInventoryFile()
        for vm_path in args.namedvms:
            UpdateVM(vmrootpath + '/' + vm_path, args.bootdelay)
    else:
        print 'Recursive option not selected and no virtual machine paths specified.\nNo VMs were updated.'


