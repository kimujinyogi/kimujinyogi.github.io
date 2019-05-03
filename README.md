# campcar の記事の作成

## 新しい記事

```
cd campcar
fugo new posts/xxxx.md
vim posts/xxxx.md
```
titleを変更、draftをfalseにする（公開）、mdファイルの最後に本文を追記する

```
hudo server -D
```

記事を確認

```
hugo 
cd ..
cp -r campcar/public/ ./
```

あとはpush 


