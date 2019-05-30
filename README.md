# campcar の記事の作成

## 新しい記事

```
cd campcar
fugo new posts/xxxx.md
vim posts/xxxx.md
```
titleを変更、draftをfalseにする（公開）、mdファイルの最後に本文を追記する
coverは画像のパス

クリック出来る画像を貼る (サムネール用途大きい画像も別で用意するようにしよう）
```
{{< imagelink src="/buygopro/test_b.png" class="imagecenter" title="xxxx" >}}↲
```

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


