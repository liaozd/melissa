#!/usr/bin/env bash

/usr/bin/ruby -e "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/master/install)"
brew install git ffmpeg
sudo easy_install pip

cd $HOME
git clone https://github.com/liaozd/melissa
cd melissa/
sudo pip install -r requirements.txt  --trusted-host pypi.douban.com -i http://pypi.douban.com/simple
