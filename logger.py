import logging


fmt = '%(asctime)s - %(threadName)s - %(name)s - %(lineno)d - %(funcName)s - %(levelname)s - %(message)s'
formatter = logging.Formatter(fmt)
logger = logging.getLogger('impact3')

console = logging.StreamHandler()
console.setFormatter(formatter)

file = logging.FileHandler('log.txt')
file.setLevel(logging.WARNING)
file.setFormatter(formatter)

logger.addHandler(file)
logger.addHandler(console)
logger.setLevel(logging.DEBUG)

if __name__=='__main__':
    logger.info('123')
    logger.debug('123')
    logger.warning('123')
    logger.critical('123123')