#!/usr/bin/bash

if [ $# != 1 ] ; then 
				echo "USAGE: sudo bash $0 your_user_name" 
				echo " e.g.: sudo bash $0 deepin" 
				exit 1; 
fi

sh -c "echo '$1 ALL=(ALL) NOPASSWD:ALL' >> /etc/sudoers"
