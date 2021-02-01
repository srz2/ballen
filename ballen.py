# This is a helper program for working with EZ-Flash Jr.
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
import subprocess
from subprocess import CalledProcessError

local_drive = "/dev/sda1"
local_mount_folder = "drive"
local_backup = "backups"

sleep_time = 20

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

def format_disk(drive):
	unmount(drive)
	try:
		subprocess.check_call([f'sudo mkfs.vfat {drive}'], shell=True)
		time.sleep(1)
		mount(drive)
	except CalledProcessError as e:
		log('Failed to make filesystem', 'error')
	except Exception as e:
		raise e

def load_fw_ver4():
	log('Loading FW4...')
	copytree('fw4', local_mount_folder)

def fatsort():
	unmount(local_drive)
	subprocess.call([f'sudo ./fatsort {local_drive}'], shell=True)
	mount(local_drive)

def mount(drive):
	try:
		log(f"Mounting {drive}")
		subprocess.check_call([f'sudo mount {local_drive} {local_mount_folder} -o uid=pi -o gid=pi'], shell=True)
		time.sleep(1)
	except CalledProcessError as e:
		log('Failed to mount drive', 'error')
	except Exception as e:
		raise e

def unmount(drive):
	try:
		log(f"Unmounting {drive}")
		subprocess.check_call([f'sudo umount {drive}'], shell=True)
		time.sleep(1)
	except CalledProcessError as e:
		log('Failed to unmount drive', 'error')
	except Exception as e:
		raise e

def stage_1():
	backup()
	format_disk(local_drive)
	load_fw_ver4()
	return True
	
def stage_2():
	restore()
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
	print('Optionals')
	print('    --fatsort-only: The only action performed is')
	print('                    to execute this program on the drive.')

def check_args():
	argc = len(sys.argv) - 1
	if argc != 1:
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

def main():
	option = check_args()
	success = False
	log(f"Option: {option}")
	try:
		mount(local_drive)
		if option == 1:
			success = stage_1()
		elif option == 2:
			success = stage_2()
		else:
			pass	
	finally:
		unmount(local_drive)

	if success:
		print_success(option)

if __name__ == "__main__":
	main()
