#!/usr/bin/env python3
# 
# # This is a helper program for working with EZ-Flash Jr.
# Developer: Steven Zilberberg
# Date: 1/24/2021

# Steps
#   1. backup the existing data
#   2. Reformat the disk
#   3. Load FW4 to disk and prompt user for instructions
#   4. Reload everything back and overwrite dat files
#   5. Run the fatsort program

import os
import sys
import time
import shutil
import configparser
import subprocess
from subprocess import CalledProcessError

file_config = "config.ini"
local_drive = "/dev/sda1"
local_mount_folder = "drive"
local_backup = "backups"

def log(msg, type='info'):
	type = type.upper()
	print(f'[{type}]: {msg}')

def copytree(src, dst, symlinks=False, ignore=None):
    for item in os.listdir(src):
        s = os.path.join(src, item)
        d = os.path.join(dst, item)
        if os.path.isdir(s):
            shutil.copytree(s, d, symlinks, ignore)
        else:
            shutil.copy2(s, d)

def backup():
	log('Backing up...')
	if os.path.exists(local_backup):
		shutil.rmtree(local_backup)
	shutil.copytree(local_mount_folder, local_backup)

def restore():
	log('Processing original data')
	format_disk(local_drive)
	log('Restoring your games')
	copytree(local_backup, local_mount_folder)

def overwrite_dat_file():
	log('Overwriting old dat file')
	shutil.copy('fw4/ezgb.dat', local_mount_folder + '/ezgb.dat')

def format_disk(drive):
	unmounted = unmount(drive)
	if not unmounted:
		raise Exception("Format disk failed to unmount drive")

	try:
		subprocess.check_call([f'sudo mkfs.vfat {drive}'], shell=True)
		time.sleep(1)
		mounted = mount(drive)
		if not mounted:
			raise Exception('format disk failed to remount drive')
	except CalledProcessError as e:
		log('Failed to make filesystem', 'error')
	except Exception as e:
		raise e

def load_fw_ver4():
	log('Loading FW4...')
	copytree('fw4', local_mount_folder)
	time.sleep(1)

def fatsort():
	log('Reorganizing files with fatsort')
	unmounted = unmount(local_drive)
	if not unmounted:
		raise Exception('Fatsort failed to unmount drive')

	subprocess.call([f'sudo ./fatsort {local_drive} 1> /dev/null'], shell=True)
	mounted = mount(local_drive)
	if not mounted:
		raise Exception('Fatsort failed to remount drive')

def remove_default_files():
	files = ['.gitkeep']
	for f in files:
		file = f'{local_mount_folder}/{f}'
		if os.path.exists(file):
			os.remove(file)

def mount(drive):
	try:
		log(f"Mounting {drive}")
		subprocess.check_call([f'sudo mount {local_drive} {local_mount_folder} -o uid=pi -o gid=pi'], shell=True)
		time.sleep(1)
		return True
	except CalledProcessError as e:
		log('Failed to mount drive', 'error')
		return False
	except Exception as e:
		raise e

def unmount(drive):
	try:
		log(f"Unmounting {drive}")
		subprocess.check_call([f'sudo umount {drive}'], shell=True)
		time.sleep(1)
		return True
	except CalledProcessError as e:
		log('Failed to unmount drive', 'error')
		return False
	except Exception as e:
		raise e

def stage_1():
	backup()
	format_disk(local_drive)
	load_fw_ver4()
	return True
	
def stage_2():
	restore()
	overwrite_dat_file()
	remove_default_files()
	fatsort()
	return True

def show_help():
	print('Usage: python ballen.py [stage-number] (Options: --fatsort-only)')
	print('No Args - show help')
	print('stage-number: Which stage to perform')
	print(' 1 - This is the first action to perform')
	print('          This will backup the existing data')
	print('          Reformat the disk')
	print('          Load the contents of the fw4 directory')
	print('          Prompt the user with instructions')
	print(' 2 - This is the second action to perform')
	print('          Clear the disk')
	print('          Load the contents of the backup dir')
	print('          Overwrite the DAT file from fw4 to drive')
	print('          Execute the fatsort program')

def check_args():
	argc = len(sys.argv) - 1
	if argc != 1:
		return -1
	arg = sys.argv[1]
	if arg in ['?', '/?', '-h', '--help']:
		show_help()
		return -1
	argv = int(sys.argv[1])
	return argv

def print_success(result):
	if result == 1:
		print('')
		log('**********************')
		log('***STAGE 1 Complete***')
		log('**********************')
		log('Please put the SD card')
		log('in the Ez-Flash Junior')
		log('and update the firmware!')
	elif result == 2:
		print('')
		log('**********************')
		log('***STAGE 2 Complete***')
		log('**********************')
		log('Everything has been reloaded')
		log('Replace your SD card and')
		log('     Enjoy playing!!    ')
	else:
		print('')
		log('**********************')
		log('********Unknown*******')
		log('**********************')
		log('    Unknown result    ')

def process_config():
	if not os.path.exists(file_config):
		log("Config INI does not exist", "Error")
	parser = configparser.ConfigParser()
	parser.read(file_config)
	config = parser['DEFAULT']

	global local_drive
	global local_mount_folder
	global local_backup
	local_drive = config['dev_drive']
	local_mount_folder = config['mount_folder']
	local_backup = config['backup_folder']

def check_for_admin():
	if os.getuid() == 0:
		return True
	else:
		return False

def main():
	is_admin = check_for_admin()
	if not is_admin:
		log('Need to be admin to run', 'error')
		return
	else:
		log('User is Admin')

	process_config()
	option = check_args()
	if option <= 0:
		log('Invalid option given')
		return

	success = False
	log(f"Option: {option}")
	try:
		mounted = mount(local_drive)
		if not mounted:
			raise Exception('Failed to mount drive')

		if option == 1:
			success = stage_1()
		elif option == 2:
			success = stage_2()
		else:
			log('Unknown option given')
	finally:
		if mounted:
			unmount(local_drive)

	if success:
		print_success(option)

if __name__ == "__main__":
	main()
