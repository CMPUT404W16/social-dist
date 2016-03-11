try:
    from fbook import create_app
except ImportError:
    import sys, os
    sys.path.insert(0, os.path.abspath(".."))

from fbook import create_app
from config import config as app_conf
testing_app = create_app(app_conf['testing'])
