'''
Console script for spotidry
'''

import sys
from spotidry import Spotidry
# import spotidry

def main(args=None):
    """Console script for spotidry."""
    s = Spotidry()
    s.get_status()
    return 0

if __name__ == "__main__":
    sys.exit(main())
