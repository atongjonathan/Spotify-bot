import logging
from logging import FileHandler,StreamHandler,INFO, basicConfig, getLogger

basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - line %(lineno)d | %(message)s',
            handlers=[FileHandler('logs.txt'), StreamHandler()], level=INFO)
logger = getLogger(__name__)
