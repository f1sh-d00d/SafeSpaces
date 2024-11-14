STEP 1: install all dependencies needed in the requirements.txt file
using the following command: 

pip install -r requirements.txt



STEP 2: After installing all the packages from requirements.txt, 
install "ffmpeg" based on your operating system as listed below:

# on Ubuntu or Debian
sudo apt update && sudo apt install ffmpeg

# on Arch Linux
sudo pacman -S ffmpeg

# on MacOS using Homebrew (https://brew.sh/)
brew install ffmpeg

# on Windows using Chocolatey (https://chocolatey.org/)
choco install ffmpeg

# on Windows using Scoop (https://scoop.sh/)
scoop install ffmpeg