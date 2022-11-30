#!/usr/bin/env python

import sys, subprocess


def main():

    j = subprocess.run(['az', 'account', 'get-access-token'], stdout=subprocess.PIPE).stdout.decode('utf-8')    # uncomment for resource manager APIs
    # j = subprocess.run(['az', 'account', 'get-access-token', '--resource', 'https://restlertest1.blob.core.windows.net'], stdout=subprocess.PIPE).stdout.decode('utf-8')  #uncomment for data-plane APIs
    j = j.split()[2].replace('"','').replace(',','')
    sys.stdout.write("{'appname':{}}" + '\n' + "Authorization: Bearer " + j)

if __name__ == "__main__":
    sys.exit(main())