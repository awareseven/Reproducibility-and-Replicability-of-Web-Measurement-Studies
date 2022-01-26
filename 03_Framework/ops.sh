#!/bin/bash

gsettings set org.gnome.desktop.lockdown disable-lock-screen 'true' &&
gsettings set org.gnome.desktop.screensaver lock-enabled false && 
gsettings set org.gnome.settings-daemon.plugins.power active false &&
git pull