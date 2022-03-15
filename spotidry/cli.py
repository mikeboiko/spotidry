'''
Console script for spotidry
'''

import sys
from spotidry.spotify import Spotidry

def main(args=None):
    """Console script for spotidry."""
    s = Spotidry()
    s.get_status()
    return 0

if __name__ == "__main__":
    sys.exit(main())
