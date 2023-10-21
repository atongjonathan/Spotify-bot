from logging import FileHandler, StreamHandler, INFO, basicConfig, getLogger

logger = getLogger(__name__)
basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - line %(lineno)d | %(message)s',
            handlers=[FileHandler('logs.txt'), StreamHandler()], level=INFO)
