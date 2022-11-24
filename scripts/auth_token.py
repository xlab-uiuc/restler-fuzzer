#!/usr/bin/env python

import sys, subprocess


def main():

    j = subprocess.run(['az', 'account', 'get-access-token'], stdout=subprocess.PIPE).stdout.decode('utf-8') # you must login first before running this script ('az login')
    j = j.split()[2].replace('"','').replace(',','')
    sys.stdout.write("{'appname':{}}" + '\n' + "Authorization: Bearer " + j)

if __name__ == "__main__":
    sys.exit(main())