lastfm_test
===========

This is a sample of usage of last_fm API

Requirements:
=============
The only requirement is the module requests. It can be installed using the next command:
pip install -r requirements.txt
The script generates a file called stored_tracks.dict where it is executed. Correct permissions
to write in the folder are needed.

...python
The script to be executed is in the folder:
lastfm_test/src
...

usage: myscript.py [-h] username

Retrieve user stats from Last.fm

positional arguments:
  username    The username you want to retrieve data for.

optional arguments:
  -h, --help  show this help message and exit
