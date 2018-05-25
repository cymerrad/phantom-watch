#!/bin/bash

echo "expected: 2 .png's in directory screenshot"
nodejs headless.js -d screenshots http://pepper.pl http://banggood.com --whole

echo "expected: 2 new directories in screenshots, in each directory multiple .png's"
nodejs headless.js -d screenshots http://pepper.pl http://banggood.com

echo "expected: 1 .jpg file named example.jpg in directory screenshots"
nodejs headless.js -d screenshots -o example.jpg http://pepper.pl --whole

echo "expected: 1 new directory in screenshots, multiple .jpg's inside"
nodejs headless.js -d screenshots -o example.jpg http://pepper.pl

echo "expected: error"
nodejs headless.js -d screenshots -o example.jpg http://pepper.pl http://alibaba.com --whole

echo "expected: .png in screenshots, path should be resolved"
nodejs headless.js -d ../$( echo $PWD | rev | cut -d'/' -f1 | rev )/screenshots http://google.com --whole

echo "expected: error"
nodejs headless.js -d screenshots -o /home/some_dir/filename.jpg http://google.com --whole

echo "expected: screenshots/home/some_dir/filename.jpg"
nodejs headless.js -d screenshots -o home/some_dir/filename.jpg http://google.com --whole

echo "expected: nothing exceptional; only some weird directory will be created with image inside"
nodejs headless.js -d '&\$!?#%^*(),.' http://google.com --whole

echo "expected: two files (image1.png & image2.png) in screenshots"
nodejs headless.js -d screenshots -o image1 http://google.com --whole
nodejs headless.js -o image2 http://google.com --whole
