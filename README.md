# DIT Tools

To generate Apple FinalCut Pro XML for mutiple cameras.

Install:

curl -sL https://raw.githubusercontent.com/liaozd/melissa/master/install.sh | sh

### Dev Env

VIRTUALPATH=$HOME/.virtualenvs
test -d "$VIRTUALPATH" || mkdir -p "$VIRTUALPATH"
cd "$VIRTUALPATH"
virtualenv --python=`which python3` --no-site-packages melissa-python3

