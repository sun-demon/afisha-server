import sys
from pathlib import Path
from typing import Union

import logging
from logging.handlers import RotatingFileHandler


_logging_configured = False
_Level = Union[int, str]


def setup_logging(logging_level: _Level = logging.DEBUG):
    global _logging_configured

    if _logging_configured:
        logging.getLogger(__name__).debug("Logging is already set up, skip it")
        return
    
    logs_dir = Path('logs')
    logs_dir.mkdir(exist_ok=True)

    formatter = logging.Formatter(
        '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )

    # root (console + file) logging
    console_handler = logging.StreamHandler(sys.stdout) # for root logging to console
    console_handler.setFormatter(formatter)

    root_file_handler = RotatingFileHandler( # for root loggin to file
        logs_dir / 'app.log',
        maxBytes=10*1024*1024,  # 10MB
        backupCount=10,
        encoding='utf-8'
    )
    root_file_handler.setFormatter(formatter)
    
    root_logger = logging.getLogger()
    root_logger.setLevel(logging_level)
    root_logger.addHandler(console_handler)
    root_logger.addHandler(root_file_handler)
    
    # logging for library (a little less noise)
    logging.getLogger('playwright').setLevel(logging.WARNING)
    logging.getLogger('sqlalchemy').setLevel(logging.WARNING)
    logging.getLogger('asyncio').setLevel(logging.WARNING)

    # logging.debug('Logging was succesfully configured')
    _logging_configured = True
