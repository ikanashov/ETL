#!/bin/sh

python etlproducer.py &
sleep 60
python etlconsumer.py &
