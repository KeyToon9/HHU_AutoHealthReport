#!/bin/bash
date >> log.txt
python ./auto_report.py >> log.txt
echo "====================" >> log.txt