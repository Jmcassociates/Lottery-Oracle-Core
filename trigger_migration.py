import os
import sys
sys.path.append('backend')
from migrate_v2 import migrate

if __name__ == "__main__":
    migrate()
