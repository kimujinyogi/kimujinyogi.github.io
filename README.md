# campcar の記事の作成

## 新しい記事

```
cd campcar
hugo new posts/xxxx.md
vim posts/xxxx.md
```
titleを変更、draftをfalseにする（公開）、mdファイルの最後に本文を追記する
coverは画像のパス

クリック出来る画像を貼る (サムネール用途大きい画像も別で用意するようにしよう）
```
{{< imagelink src="/buygopro/test_b.png" class="imagecenter" title="xxxx" >}}↲

{{< thumblink src="/joycon/spray01.jpg" thumbnail="/joycon/spray01t.jpg" class="imagecenter" title="xxx" >}}
```

テーマのアップデート
```
git submodule update --remote --merge
```


```
hugo server -D
```

記事を確認

```
hugo
cd ..
git add -A
git commit -m " exec hugo "
cp -R campcar/public ./tmpPublic
git checkout master
cp -R ./tmpPublic/* ./
```

あとはpush 


theme update
```
git submodule update --remote --merge
```
