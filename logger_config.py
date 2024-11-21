import logging
import colorlog
import os
from logging.handlers import RotatingFileHandler
from datetime import datetime

class LoggerSetup:
    @staticmethod
    def setup():
        # Create logs directory if it doesn't exist
        os.makedirs('logs', exist_ok=True)

        # Create formatters
        file_formatter = logging.Formatter(
            '%(asctime)s - %(name)s - %(levelname)s - %(user_id)s - %(message)s'
        )
        
        console_formatter = colorlog.ColoredFormatter(
            '%(log_color)s%(asctime)s - %(name)s - %(levelname)s - %(message)s',
            log_colors={
                'DEBUG': 'cyan',
                'INFO': 'green',
                'WARNING': 'yellow',
                'ERROR': 'red',
                'CRITICAL': 'red,bg_white',
            }
        )

        # Create handlers
        file_handler = RotatingFileHandler(
            'logs/bot.log',
            maxBytes=10*1024*1024,  # 10MB
            backupCount=5,
            encoding='utf-8'
        )
        file_handler.setFormatter(file_formatter)

        console_handler = logging.StreamHandler()
        console_handler.setFormatter(console_formatter)

        # Setup root logger
        root_logger = logging.getLogger()
        root_logger.setLevel(logging.INFO)
        root_logger.addHandler(file_handler)
        root_logger.addHandler(console_handler)
        
        return root_logger 
