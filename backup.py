#!/usr/bin/env python3
import os
import sys
import re
from datetime import datetime
import stat
import subprocess
import shutil

def quit(message):
    print("%s\n\nQuitting Komi!\n" % message)
    sys.exit()

def showhelp(mode):
    if mode == "none":
        print("\nKomi is a python based USB drive backup & restore utility. It also supports creating bootable usb drives.\nFor help and examples check \"komi backup help\" \"komi restore help\" and \"komi makeboot help\"")
        quit("")
    elif mode == "backup":
        backuphelp = "\nKomi's BACKUP  mode \
                \nUsage:\tkomi backup device=[disk] {t|c}folder=[path] \
                \n \
                \nExamples with explanation: \
                \n\tkomi backup device=/dev/sda1 bfolder=\"My usb bkp\" \
                \n\tCopy files from /dev/sda1 to default backups folder \"$HOME/Backups/My_usb_bkp\" \
                \n \
                \n\tkomi backup device=/dev/sda1 folder=\"/home/user/Documents/bkpfolder/today\" \
                \n\tCopy files from /dev/sda1 to custom dest. folder \"/home/user/Documents/bkpfolder/today\" \
                \n \
                \n\tkomi backup device=/dev/sda1 tfolder=\"My usb bkp\" \
                \n\tCopy files from /dev/sda1 to folder with timestamp \"$HOME/Backups/20190920170430_My_usb_bkp\" \
                \n \
                \n\tkomi backup \
                \n\tPrompt user for destination folder, device and name specifics. Proceeds as before. \
                \n"
        #subprocess.Popen("echo %s" % backuphelp, shell=True)
        print(backuphelp)
        quit("")
    elif mode == "restore":
        restorehelp = "\nkomi's RESTORE mode \
                \nUsage:\tkomi backup device=[disk] {t|c}folder=[path] \
                \n \
                \nExamples with explanation: \
                \n\tkomi restore device=/dev/sda1 folder=\"/home/user/Documents/bkp/\" \
                \n\tCopy files from folder \"/home/user/Documents/bkp/\" to /dev/sda1  \
                \n \
                \n\tkomi restore device=/dev/sda1 bfolder=\"My_usb_bkp\" \
                \n\tCopy files from folder with timestamp \"$HOME/Backups/My_usb_bkp\" to /dev/sda1 \
                \n \
                \n\tkomi restore \
                \n\tPrompt user for source folder, device and name specifics. Proceeds as before. \
                \n"
        print(restorehelp)
        quit("")
    else:
        makeboothelp = "\nkomi's MAKEBOOT mode \
                \nUsage:\tkomi makeboot device=[disk] image=[path] \
                \n \
                \nExamples with explanation: \
                \n\tkomi makeboot device=/dev/sda image=\"/home/user/arch.iso\" \
                \n\tFlash image \"/home/user/arch.iso\" to device=/dev/sda \
                \n"
        print(makeboothelp)
        quit("")

# check if partition kisslinuxis actually available
def diskexists(path):
    try:
        return stat.S_ISBLK(os.stat(path).st_mode)
    except:
        return False

# select the partition with fzf
def selectdisk():
    # get list of disks and their sizes
    disks = os.popen("lsblk -o name,size,model -n -l").read()

    # parse the output (remove device names and add exit string
    out = "Exit disk selection\n"
    for line in disks.splitlines():
        if re.match(r"^sd[a-z]$", line.split(" ")[0]):
            out += " - %s\n" % line.split(" ")[-1]
        else:
            out += "%s\n" % line

    # select one entry
    selected = subprocess.run(["fzf", "--layout=reverse"], input=out, encoding="ascii", stdout=subprocess.PIPE).stdout

    # if entry is exit string...
    if selected == "Exit disk selection\n":
        quit("Exiting disk selection!")      

    # if entry is a device (starting with " - ") recursively call itself
    elif selected[1] == "-":
        print("Select a valid partition!")
        selected = selectdisk()

    return selected.split(" ")[0]

# add /dev/ to selectdisk
def getdevname():
    return "/dev/{}".format(selectdisk())


def selectdestination(currentpath):
    # change into working directory
    os.chdir(currentpath)

    # fill folders with control entries
    folders = " - Exit folder selection\n - Back\n - Confirm\n"

    # list current folder's contents
    folders += os.popen("find * -maxdepth 0 -type d").read()
    
    # input all of this into fzf
    selected = subprocess.run(["fzf", "--layout=reverse"], input=folders, stdout=subprocess.PIPE, encoding="utf-8").stdout
    
    selected = selected.replace("\n", "")

    # control entry handling with recursion
    if selected == " - Exit folder selection":
        quit("Exiting folder selection") 
    elif selected == " - Back":
        # new path is last path without what's behind last / 
        newpath = '/'.join(currentpath.split("/")[1:-1])
        return selectdestination("/%s" % newpath)
    elif selected == " - Confirm":
        return currentpath
    else:
        return selectdestination("%s/%s" % (currentpath, selected))

# parse dirname and add timestamp
def getdirname(mode):

    # call selectdestination
    dirname = selectdestination("%s/Backups" % os.getenv("HOME"))

    # if backup mode is active also set subfolder
    if mode == "backup":
        # enter custom folder name
        foldername = input("Enter folder name (e.g. My backup)\n$> ").replace(" ", "_")

        # timestamp prompt
        if input("Include timestamp? [y/n]\n$> ") == "y":
            now = datetime.now()
            foldername = "%s_%s" % (now.strftime("%Y%m%d%H%M%S"), foldername)

        return "%s/%s" % (dirname, foldername)
    # if restore mode is active only return selected dir path
    elif mode == "restore":
        return dirname

# selects proper mode (backup, restore, makeboot)
def getmode():
    mode = input("\nSelect mode [1|2|3]:\n - backup   [1]\n - restore  [2]\n - makeboot [3]\n - exit mode selection [4]\n$> ")
    if mode == '1':
        return "backup"
    elif mode == '2':
        return "restore"
    elif mode == '3':
        return "makeboot"
    elif mode == '4':
        quit("Exiting mode selection")
    else:
        return getmode()

# devname       sdb1
# dirname       2019...
# infile        arch.iso
# mode          backup

dirname=""
devname=""
infile=""

mode=""

# if restore wipe argument is set then this becomes true
restorewipe=False

# if mode is first argument then start iterating at next one
startarg = 1

# get mode
if len(sys.argv) == 1:
    showhelp("none")
elif sys.argv[1] == "--help" or sys.argv[1] == "help":
    showhelp("none")
elif sys.argv[1] == "backup":
    mode = "backup"
    startarg = 2
elif sys.argv[1] == "restore":
    mode = "restore"
    startarg = 2
elif sys.argv[1] == "makeboot":
    mode = "makeboot"
    startarg = 2

print("\n-------------\n")

# iterate through all arguments
for i in range(startarg, len(sys.argv)):
    # show help if second argument is help string
    if  sys.argv[i] == "help" or sys.argv[i] == "--help" or sys.argv[i] == "-h":
        showhelp(mode)
    elif sys.argv[i] == "--wipe":
        restorewipe = True
    else:
        # argument is split to identifier and property for simplicity
        ident=sys.argv[i].split("=")[0]
        prop=sys.argv[i].split("=")[1]
   
        # if any error is raised script is terminated
        if ident == "device":
            if not re.match(r"/dev/sd[a-z][1-9]{1,2}", prop) and mode != "makeboot":
                quit(prop + " is not a valid disk partition name! Exiting...") 
            else:
                if not diskexists(prop):
                    quit("Device %s does not exist! Exiting..." % prop)

                devname = prop
                print("Selected device/partition\t\t: " + prop)
        #elif ident == "bfolder":
            #dirname = "%s/Backups/%s" % (os.getenv("HOME"), prop.replace(" ", "_"))
            #print("Selected folder\t\t: %s" % (dirname))
        elif ident == "folder":
            dirname = prop
            print("Custom folder\t\t: %s" % (dirname))
        elif ident == "tfolder":
            now = datetime.now()
            dirname = "%s/Backups/%s_%s" % (os.getenv("HOME"), now.strftime("%Y%m%d%H%M%S"), prop.replace(" ", "_"))
            print("Timestamped %s folder\t\t: %s" % ("destination" if ident == "tdest" else "source",  dirname))
            
        elif ident == "image":
            # if file exists and is an iso file
            if os.path.isfile(prop) and prop.split(".")[-1] == "iso":
                print("Bootable image file found!")
                infile = prop
            else:
                quit("Creating bootable disks is dangerous! Check your files beforehand!")
        else:
            quit("%s is not a valid argument! Exiting!" % ident)

# check if mode is set
if mode == "":
    mode = getmode()
    print("%s mode is selected" % mode)

if mode == "makeboot":
    if infile == "":
        quit("Select a proper image file and make sure you have backed up your files!")
    if not re.match(r"^\/dev\/sd[a-z]$", devname):
        quit("Select a proper disk and make sure you have backed up your files!\nExample: /dev/sda (NOT /dev/sda1)")

# check if dirname is set
if dirname == "" and mode != "makeboot":
    dirname = getdirname(mode)
    print("%s directory is set to %s" % (mode.capitalize(), dirname))

# check if devname and dirname are set
if devname == "":
    devname = getdevname() 
    print("Selected device is set to %s" % devname)


if mode == "backup":
    # error checking finished, proceed with risky stuff
    print("\n-------------\n\nAll set! Proceeding to copy contents of %s to folder %s" % (devname, dirname))
    
    # create a custom mountpoint
    mountpoint = "/mnt/backupper-%s" % devname.split("/")[2]

    # create directory (TODO check why it makes it owned by root by default)
    print("Creating destination directory %s\n!! Next steps will require superuser privileges !!" % dirname)
    os.system("sudo mkdir -p " + dirname)
    os.system("sudo chown -R %s %s" % (os.getlogin(), dirname))

    # mounting
    print("Unmounting /mnt for safety reasons")
    os.system("sudo umount %s" % mountpoint)
    os.system("sudo umount /mnt")


    print("Creating mountpoint %s" % mountpoint)
    os.system("sudo mkdir -p " + mountpoint)
    
    os.system("sudo mount %s %s" % (devname, mountpoint))

    # TODO check if sufficient space

    # copying
    print("Copying files... Wait!")
    copycommand = "cp -a %s/. %s/" % (mountpoint, dirname)
    copyprocess = subprocess.Popen(copycommand, shell=True)
    (output, err) = copyprocess.communicate() 
    status = copyprocess.wait()

    print("Copying done!")

    # clean up after everything
    print("Cleaning up like a good girl!\nUnmounting and removing mountpoint!")
    os.system("sudo umount %s" % mountpoint)
    os.system("sudo rm -rf %s" % mountpoint)

elif mode == "restore":
    # error checking finished, proceed with risky stuff
    print("\n-------------\n\nAll set! Proceeding to copy contents of folder %s to device %s" % (dirname, devname))
    
    # custom mountpoint name
    mountpoint = "/mnt/backupper-%s" % devname.split("/")[2]

    # unmounting and mounting
    print("Unmounting /mnt and %s for safety reasons \n!! Next steps will require superuser privileges !!" % mountpoint)
    os.system("sudo umount %s" % mountpoint)
    os.system("sudo umount /mnt")


    # create a custom mountpoint
    print("Creating mountpoint %s" % mountpoint)
    os.system("sudo mkdir -p " + mountpoint)

    os.system("sudo mount %s %s" % (devname, mountpoint))

    os.system("sudo chown -R %s %s" % (os.getlogin(), mountpoint))
    
    # if wipe flag is set to false prompt and set it accordingly
    if not restorewipe:
        if input("Wipe ALL data on partition %s before copying? [y/n]\n$> " % devname) == 'y':
            if input("Are you really sure? [y/n]\n$> ") == 'y':
                restorewipe = True

    # wipe only if 
    if restorewipe:
        print("\nRemoving all files from %s\n" % mountpoint)
        FNULL = open(os.devnull, 'w')
        wipe = subprocess.Popen("rm -r %s/{*,.*}" % mountpoint, shell=True, stdout=FNULL, stderr=subprocess.STDOUT)
        wipe.wait()

        print("Wiping finished! Proceeding to copy!")

    # TODO check if sufficient space

    # copying to selected device
    print("Copying files... Wait!")

    copycommand = "cp -a %s/. %s/" % (dirname, mountpoint)
    copyprocess = subprocess.Popen(copycommand, shell=True)

    (output, err) = copyprocess.communicate() 
    status = copyprocess.wait()

    print("Copying done!")

    # clean up after everything
    print("Cleaning up like a good girl!\nUnmounting and removing mountpoint!")
    os.system("sudo umount %s" % mountpoint)
    os.system("sudo rm -rf %s" % mountpoint)
else:
    
    if input("\nConfirm flashing of %s [y/n]\n$> " % devname) != "y":
        quit("\nQuitting bootable usb maker!")

    print("\nThis process can take some time... Be patient!")

    wipeprocess = subprocess.Popen(["sudo", "dd", "if=%s" % infile, "of=%s" % devname, "bs=4M", "status=progress"])
    (output, err) = wipeprocess.communicate() 
    status = wipeprocess.wait()


print("\n-------------\nAll finished!\n")
