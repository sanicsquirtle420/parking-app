# Intro to Git
## macOS / Linux instructions

macOS: Install with [brew](https://brew.sh)
```bash
brew install git
```
Linux: Install git with your package manager (Debian / Ubuntu) example
```bash
sudo apt install git
```

Generate an SSH key and follow the prompts
```bash
ssh-keygen -t ed25519 -C "email@example.com"
```

Find and copy your SSH public key
```bash
cat ~/.ssh/id_ed25519.pub
```

Example public SSH Key:
```
ssh-ed25519 AAcAC3NzaC1bZDI1NTE5AA4AIFk5mNd+BT2w4Sk9pXqAhiTxTsuyYCElmAsPiGN2l1rN druiz@go.olemiss.edu
```

Adding SSH Key to GitHub
Click on your profile picture > Settings > SSH and GPG keys > New SSH Key > Paste your public SSH key and give it a name

Clone this repository
```bash
git clone git@github.com:sanicsquirtle420/parking-app.git
```

To get the latest version from GitHub
```bash
git pull origin main
```
Before pulling make sure you are in the directory with the code. For example: `~/coding/parking-app` 

Uploading your changes to GitHub
```bash
git add .
git commit -m "Sample message"
git push origin main
```

If you want to you can add a [GPG key](https://docs.github.com/en/authentication/managing-commit-signature-verification/adding-a-gpg-key-to-your-github-account) to your GitHub account to have your commits be "verified" that they are from you.

If you are on Windows it would be easier for you to install Ubuntu with WSL and follow these instructions.