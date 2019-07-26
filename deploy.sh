#!/bin/sh

cp -r campcar/public/ ./

git add -A
git commit -m " deplay "
git push origin master
