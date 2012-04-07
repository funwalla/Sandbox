# -*- coding: utf-8 -*-
"""
Practice file for 
http://docs.python.org//howto/logging.html#logging-basic-tutorial
"""

import logging
import mylib

def main():
    logging.basicConfig(level=logging.INFO,
                        format='%(asctime)s:%(module)s:%(lineno)d:%(funcName)'\
                        's:%(levelname)s: %(message)s')
    logging.info('started')
    v = 5
    logging.info('v = %d', v)
    mylib.do_something()
    logging.info('finished')

if __name__ == '__main__':
    main()



