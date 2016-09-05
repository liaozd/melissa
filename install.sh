#!/usr/bin/env bash

/usr/bin/ruby -e "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/master/install)"
brew install -y git ffmpeg
sudo easy_install pip

cd $HOME
git clone https://github.com/liaozd/melissa
cd melissa/
pip install -r requirements.txt -i https://pypi.douban.com/simple/


