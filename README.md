Neatza App (Project is EOL-ed)
==========

This project is no longer maintained/worked upon or used.
Leaving the code here for reference.

Neatza == Morning (as the greeting 'Good Morning') in Romanian.

Description
-----------
This script is meant to be put in a cron-job on a machine and run periodically.

I run it every day at 9:31 AM Romanian Time.

What it will do, is:

1. Look for any conf files within the directory where the script is situated
2. It will read **Quotes of Days** from various sources
3. For each conf file
 1. Extract one line (which is supposed to be an URL of a pic) 
 2. Assign it a random quote from the list
 3. Send email

I did this script out of fun for my friends (with which I share an emailing list).

They wanted nude pics of girls, and one day I just created this small app because it was fun.

There's a script to populate the conf files, from sources.
I wrote some scrapers, and I'll have to write a few more in the future.

**Note**: some scrapers require PyQT installed on the system.
And if you're running it on the server you'll also need X virtual framebuffer installed.
For that, there's also a small **init.d** script.

