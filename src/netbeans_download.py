#!/usr/bin/python3

'''
This is a script that knows how to download netbeans.
'''

import download.generic # for get

'''
These are examples of urls to download
http://download.netbeans.org/netbeans/8.0.2/final/bundles/netbeans-8.0.2-linux.sh
http://download.netbeans.org/netbeans/8.0.2/final/bundles/netbeans-8.0.2-php-linux.sh
http://download.netbeans.org/netbeans/8.0.2/final/bundles/netbeans-8.0.2-cpp-linux.sh
http://download.netbeans.org/netbeans/8.0.2/final/bundles/netbeans-8.0.2-javaee-linux.sh
http://download.netbeans.org/netbeans/8.0.2/final/bundles/netbeans-8.0.2-javase-linux.sh
'''

products=[
    '',
    'php-',
    'cpp-',
    'javaee-',
    'javase-',
]
version='8.0.2'

for product in products:
    url='http://download.netbeans.org/netbeans/{version}/final/bundles/netbeans-{version}-{product}linux.sh'.format(**vars())
    filename='netbeans-{version}-{product}linux.sh'.format(**vars())
    download.generic.get(url, filename)
