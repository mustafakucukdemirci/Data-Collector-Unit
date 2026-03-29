@echo off
set ip=YOUR_DEVICE_IP
set user=YOUR_USERNAME
scp -r ../mirainano %user%@%ip%:Desktop/mirainano
pause
