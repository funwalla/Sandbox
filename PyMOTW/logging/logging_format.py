import logging

logging.basicConfig(format='%(module)s %(levelname)s:%(message)s',
                    level=logging.DEBUG)
logging.debug('This message should appear on the console')
logging.info('So should this')
logging.warning('And this, too')