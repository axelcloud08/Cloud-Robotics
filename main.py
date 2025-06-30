import logging
from RoboCup import run

logger = logging.getLogger(__name__)

def main():
    logging.basicConfig(level=logging.DEBUG, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    run()


if __name__ == '__main__':
    main()
