#!/usr/bin/python
#coding: utf-8

import os
import commands

print(''' 
 ███████╗███╗   ███╗██████╗ 
 ██╔════╝████╗ ████║██╔══██╗
 ███████╗██╔████╔██║██████╔╝
 ╚════██║██║╚██╔╝██║██╔══██╗
 ███████║██║ ╚═╝ ██║██████╔╝
 ╚══════╝╚═╝     ╚═╝╚═════╝ 
 WEB ANGIL'S TEAM EXPLOIT 
''')

print "\n"
print "\nSMB >",
ip = raw_input()
print "\n"
print "\nUse proxychains? (Y/N):",
pchains = raw_input()

if pchains == 'Y' or pchains =='y' or pchains == '':
	print "\n"
	print "Listing folders..."
	print "\n"
	os.system("proxychains smbclient -L " + ip + " -N")
	print "\n "
elif pchains == 'N' or pchains == 'n':
	print "\n"
	print "Listing folders..."
	print "\n "
	os.system("smbclient -L " + ip + " -N")
	print "\n "



print "\nSharename:",
sn = raw_input()
print "\n "

if pchains == 'Y' or pchains =='y' or pchains == '':
	print "\n"	
	print "\nFolder " + sn
	os.system("proxychains smbclient //" + ip + "/" + sn +" -N")
	print "\n"
elif pchains == 'N' or pchains == 'n':
	print "\n "
	print "\nFolder >" + sn
	print "\n "
	os.system("smbclient //" + ip + "/" + sn +" -N")
	print "\n "
