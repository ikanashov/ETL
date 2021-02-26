from etlconsumer import ETLConsumer
from etlproducer import ETLProducer


if __name__ == '__main__':
    ETLProducer().stop()
    ETLConsumer().stop()
