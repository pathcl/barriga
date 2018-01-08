Barriga
=======

Find an apartment to rent for you. At this moment is only a toy :)

#### Requires:

Python 3

SQLite3

Tqdm (progressbar)

Beautifulsoup4

datasette (optional) (https://github.com/simonw/datasette)

#### Usage:

$ pip3 install requests bs4 tqdm datasette

$ cat flats.sql | sqlite3 flats.db

$ python3 main.py
$ python3 portal.py

$ pip3 install datasette && datasette serve flats.db

### Demo

[here](http://arm.unix.cl:8001/flats-398a1e4/flats)
