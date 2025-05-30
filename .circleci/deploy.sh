#!/usr/bin/env bash

# エラー時、実行を止める
set -e

DEPLOY_DIR=deploy

echo j_kim buildstart

# gitの諸々の設定
git config --global push.default simple
git config --global user.email kimujinyogi_circle@gmail.com
git config --global user.name $CIRCLE_USERNAME

echo j_kim config end

# gh-pagesブランチをdeployディレクトリにクローン
git clone -q --branch=campcar $CIRCLE_REPOSITORY_URL $DEPLOY_DIR

echo j_kim clone end

# rsyncでhugoで生成したHTMLをコピー
cd $DEPLOY_DIR

git submodule update --init --recursive

cd campcar

HUGO_ENV=production hugo -v

rsync -arv --delete ./public/* ../

cd ../..

rm -rf deploy

git add -A
git commit -m "Deploy #$CIRCLE_BUILD_NUM from CircleCI [ci skip]" || true
git push -f
