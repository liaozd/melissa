#!/usr/bin/env bash

/usr/bin/ruby -e "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/master/install)"
brew install -y git ffmpeg pyqt
sudo easy_install pip

cd $HOME
git clone https://github.com/liaozd/melissa
cd melissa/
sudo pip3 install -r requirements.txt  --trusted-host pypi.douban.com -i http://pypi.douban.com/simple
