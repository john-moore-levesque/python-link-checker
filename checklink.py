import bs4
import httplib2
import json
import re
import urllib.parse
import argparse


class CheckLink():
    """
    CheckLink class
    address = address to check
    ssl = True (if SSL enabled; this is the default)
    prefix = False by default; pass if you are looking at a subpage (e.g., www.example.com/foo)
        This is necessary because www.example.com/foo will probably have top-level
        relative links (e.g., /bar)
    """
    def __init__(self, address, ssl=True, prefix=False):
        self.address = address.strip()
        if prefix:
            self.address = prefix + self.address
        if "http" not in self.address:
            if ssl:
                self.address = "https://%s" %(self.address)
            else:
                self.address = "http://%s" %(self.address)
        self.http = httplib2.Http()
        self.status, self.response = self.http.request(self.address)
        self.links = []
        for link in bs4.BeautifulSoup(self.response, parse_only=bs4.SoupStrainer('a'), features='html.parser'):
            if link.has_attr('href'):
                self.links.append(link)
        self.goodlinks = []
        self.badlinks = []
        self.other = []

    def check(self):
        """
        Check links on page
        """
        def _checkLink(link):
            """
            Check a given link; if the response is "good", then add it to self.goodlinks
            Otherwise add to self.badlinks
            If there's a ServerNotFound error, add to self.other (since this could be
                an issue with the computer checklink.py is being run from, not the
                remote server)
            """
            try:
                link = link.attrs['href']
            except KeyError:
                return -1
            if link[0] == '/':
                link = '://'.join(list(urllib.parse.urlparse(self.address)[0:2])) + link
            elif re.match(r'^mailto|^#', link):
                return None
            good = ['200', '206', '301', '302']
            try:
                status, response = self.http.request(link)
                if status['status'] not in good:
                    self.badlinks.append((status['status'], link))
                else:
                    self.goodlinks.append(link)
            except httplib2.ServerNotFoundError:
                self.other.append(("httplib2.ServerNotFoundError", link))
            except httplib2.ssl.SSLError:
                self.other.append(("httplib2.ssl.SSLError", link))
            except ConnectionResetError:
                self.other.append(("ConnectionResetError", link))
            except UnicodeError:
                self.other.append(("UnicodeError", link))

        for link in self.links:
            _checkLink(link)

    def log(self, logfilepath):
        """
        Write data to a logfile; if the logfile already exists it is read in and the
        relevant page in the dict is updated
        """
        logname = re.sub("https?://w{3}.?", '', self.address)
        logname = re.sub("/", '.', logname)
        logfile = "%s/%s" %(logfilepath, logname)
        if not len(self.goodlinks) and not len(self.badlinks):
            return False
        log = {}
        try:
            with open(logfile, 'r') as lfile:
                try:
                    log = json.load(log, encoding='utf-8')
                except json.decoder.JSONDecodeError:
                    pass
        except FileNotFoundError:
            pass
        if self.address not in log.keys():
            log[self.address] = {}
            log[self.address]['good'] = []
            log[self.address]['bad'] = []
            log[self.address]['other'] = []
        good = set(log[self.address]['good'])
        bad = set(log[self.address]['bad'])
        other = set(log[self.address]['other'])
        for glink in self.goodlinks:
            good.add(glink)
        for blink in self.badlinks:
            bad.add(blink)
        for olink in self.other:
            other.add(olink)
        log[self.address]['good'] = list(good)
        log[self.address]['bad'] = list(bad)
        log[self.address]['other'] = list(other)
        with open(logfile, 'w', encoding='utf-8') as lfile:
            json.dump(log, lfile)


def fromFile(linkfile, logfilepath=False, ssl=True, prefix=False):
    """
    Read a list of addresses from a linkfile and create CheckLink classes for each one
    Runs check() on each one, and log() on each if logfilepath is provided
    """
    links = []
    checkLinks = []
    with open(linkfile, 'r') as infile:
        links = infile.readlines()
    for link in links:
        checker = CheckLink(link, ssl, prefix)
        checker.check()
        checkLinks.append(checker)
        if logfilepath:
            checker.log(logfilepath)
    return checkLinks


def interface(**args):
    """
    Command-line interface
    """
    parser = argparse.ArgumentParser(description='Variables for checking links')
    parser.add_argument('--address', '-a', metavar='address', type=str,
                        help='address for doing a single link check run')
    parser.add_argument('--linkfile', '-l', metavar='linkfile', type=str,
                        help='file with list of links to read')
    parser.add_argument('--logfilepath', '-L', metavar='logfilepath', type=str,
                        help='path for writing log files')
    parser.add_argument('--ssl', '-s', metavar='ssl', type=bool, default=True,
                        help='is this site SSL-enabled? (default is True)')
    parser.add_argument('--prefix', '-p', metavar='prefix', type=str, default=False,
                        help='prefix to use for top-level ("/foo") links, if the address provided is an internal page')
    args = parser.parse_args()
    if args.address:
        _check = CheckLink(args.address, args.ssl, args.prefix)
        _check.check()
        if args.logfilepath:
            _check.log(args.logfilepath)
        else:
            print(_check.address)
            print(_check.goodlinks)
            print(_check.badlinks)
            print(_check.other)
    elif args.linkfile:
        return fromFile(args.linkfile, args.logfilepath, args.ssl, args.prefix)
    else:
        return False


if __name__ == "__main__":
    interface()
