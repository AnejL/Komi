# Komi

A simplistic python backup/restore tool for Linux

Backups are by default located and looked for in $HOME/Backups

## Usage
Komi has three modes:
- backup	(for copying files over from USBs to your PC)
- restore	(for copying files from your PC to USBs)
- makeboot	(for making simple bootable disks with GNU dd)


### Backup examples
komi backup
	komi prompts you which folder you want to choose as your destination and which device you want to backup

komi backup device=/dev/sda1
	komi prompts you which folder you want to backup /dev/sda1 to

komi backup device=/dev/sda1 folder=/home/anej/Backups/MyBkp
	komi mounts /dev/sda1 and copies it to /home/anej/Backups/MyBkp


### Restore examples
komi restore
	komi prompts you which folder you want to choose as your source and which device you want to copy it over to

komi restore device=/dev/sda1
	komi prompts you from which folder you want to restore files to /dev/sda1

komi restore device=/dev/sda1 folder=/home/anej/Backups/MyBkp
	komi copies the contents of /home/anej/Backups/MyBkp to /dev/sda1 

### Makeboot examples
*This mode is the strictest and most dangerous. That's why this is the only way to successfully make it work*

komi makeboot device=/dev/sda image=/home/anej/Downloads/arch.iso
	komi flashes /dev/sda disk with image /home/anej/Downloads/arch.iso 


*TODO*
- copy whole disks
- formatting
- zipping backups for improved space efficiency when storing
- possible performance improvements
- minor UI improvements

Made by AnejL
