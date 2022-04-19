'''

Product, company and version information

'''

VERSION_MAJOR = 1

VERSION_MINOR = 1

VERSION_BUILD = 1


VERSION_INFO = (VERSION_MAJOR, VERSION_MINOR, VERSION_BUILD)

VERSION_STRING = '.'.join(map(str, VERSION_INFO))

# “%d.%d.%d” % VERSION_INFO

__version__ = VERSION_STRING

__company_name__ = 'Mikajaki SA'

__product_name__ = 'Station Automation'

