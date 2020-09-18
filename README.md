# Corec-AutoSchedule-Avail
Web app that provides simpler ui for managing Purdue University corec appointments



## Usage:
### Sign up
<img src="https://i.imgur.com/2FY75m6.png" width="800">
You have to provide sensetive information so the server can log into your purdue account and get these reservations. There is an included disclaimer about this, but if you do not feel comfortable giving your server the capability to log into your purdue account, then don't use this project.

### Home
<img src="https://i.imgur.com/ltbprwA.png" width="800">
Each day with currently available appointments are displayed. Click on any of them to see the current options.

### Scheduling
<img src="https://i.imgur.com/CtvIHyz.png" width="800">
After clicking on a day, you can see all the currently available options scraped from the corec homepage.

<img src="https://i.imgur.com/3WVB9V1.png" width="800">
Select as many appointments as you like. You will be shown a day view with all selected appointments (as well as appointments you have already made for that day).

<img src="https://i.imgur.com/g2KcM6e.png" width="800">
Press Reserve to get the appointments.

<img src="https://i.imgur.com/KUdXjng.png" width="800">
Your appointment will be blue while the server is signing you up.

<img src="https://i.imgur.com/jZBdRPC.png" width="800">
Once it is reserved and confirmed, the appointment will be green. If there are any errors, the appointment will turn red.

### Canceling
<img src="https://i.imgur.com/dJbUIEM.png" width="800">
Click on any confirmed appointment to cancel it. You will be presented with a confirmation dialog before you cancel.

<img src="https://i.imgur.com/jZBdRPC.png" width="800">
Your appointment will remain while the server is canceling your reservation.

<img src="https://i.imgur.com/ltbprwA.png" width="800">
Once it is canceled, the appointment will be gone. If there are any errors, the appointment will turn red.


## To deploy your own version:
1. Generate a secret key for `project/config.py`
2. Follow tutorial for deploying to ubuntu vps: https://www.digitalocean.com/community/tutorials/how-to-serve-flask-applications-with-gunicorn-and-nginx-on-ubuntu-18-04 (Also install all python dependencies on this machine)
3. Generate invite keys by running `generateKeys.py`. Only users you give keys to will be able to sign up for your site.
