# python-link-checker

Usage:
```
python checklink.py [ARGUMENTS]
usage: checklink.py [-h] [--address address] [--linkfile linkfile]
                    [--logfilepath logfilepath] [--ssl ssl] [--prefix prefix]

Variables for checking links

optional arguments:
  -h, --help            show this help message and exit
  --address address, -a address
                        address for doing a single link check run
  --linkfile linkfile, -l linkfile
                        file with list of links to read
  --logfilepath logfilepath, -L logfilepath
                        path for writing log files
  --ssl ssl, -s ssl     is this site SSL-enabled? (default is True)
  --prefix prefix, -p prefix
                        prefix to use for top-level ("/foo") links, if the
                        address provided is an internal page
```

If no argument is provided, the script just exits.

If an address is provided, then a linkfile (file with list of links) is not read.

Originally based on https://gist.github.com/hackerdem/2872d7f994d192188970408980267e6e
