BALLEN
=======

An easy upgrading utility for the Ez-Flash Junior designed for a Raspberry Pi.

## Usage

This assumes a USB device containing your ROMs and ez-flash jr DAT file. It is assumed the device is mounted to /dev/sda1. If it connects to something different, change the `local_drive` variable in the *ballen.py* script

To use the script use the terminal to run the commands `python ballen.py 1` or `python ballen.py 2` to execute stage 1 and stage 2, respectively.