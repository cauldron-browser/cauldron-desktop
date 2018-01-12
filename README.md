# Cauldron desktop

# Fetch code, and build source
 git clone https://github.com/cauldron-browser/cauldron-desktop.git
 cd cauldron-desktop/
 ls
 subl Makefile 
 subl Makefile 
 python3
 make build
 
# eg in directory /Users/USERNAME/Documents/cauldron-desktop/dist/cauldron 
 make clean
 mkdir ~/.cache
 mkdir ~/.cache/cauldron

CAULDRON_DIR=~/.cache/cauldron dist/cauldron
cp download_blacklist.txt ~/.cache/cauldron/


