#!/usr/bin/env python3
"""
EE Flask Server Launcher
Start the EE web interface server
"""

import sys
from pathlib import Path

# Add EE src to path
ee_src = Path(__file__).parent / 'src'
sys.path.insert(0, str(ee_src))

from flask_server.run import main

if __name__ == '__main__':
    main()
