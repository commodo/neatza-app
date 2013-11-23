Neatza App
==========

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

At the moment, it works only for sending to an emailing list.

I did this script out of fun for my friends (with which I share an emailing list).

They wanted nude pics of girls, and I just created this small app one day because it was fun.
Now I just have to fill the buckets of pics every once in a while, to keep them happy.

