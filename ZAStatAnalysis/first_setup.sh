#!/bin/bash

# configure the origin repository
GITHUBUSERNAME=`git config user.github`
GITHUBUSERREMOTE=`git remote -v | grep upstream | awk '{print $2}' | head -n 1 | cut -d / -f 2`
git remote add origin git@github.com:${GITHUBUSERNAME}/${GITHUBUSERREMOTE}

# Add the remaining forks
git remote add alesaggio https://github.com/alesaggio/ZAStatAnalysis.git
git remote add OlivierBondu https://github.com/OlivierBondu/ZAStatAnalysis.git
git remote add vidalm https://github.com/vidalm/ZAStatAnalysis.git
git remote add delaere https://github.com/delaere/ZAStatAnalysis.git
