# バージョン別サイトの更新

`_versions/kotori/versions.json` が版の一覧と既定版の真相源です。`latest` は通常の入口、`working` は編集中の版です。この main では両方が 1.1.2 です。

- `/kotori/` と `/kotori/main/` は `latest` の完全な9ページを表示します。
- `/kotori/v1.0.0/` などはその版の9ページと当時の画像・CSSを表示します。
- 編集先は `_versions/kotori/v<version>/`。`kotori/*.html`、`kotori/main/`、`kotori/v*/` は生成物です。
- 現在のナビゲーションとフッターは `_partials/kotori/`、過去の版は各版の `_partials/` から同期します。

```sh
python3 _partials/sync.py --write
python3 Tools/build_versions.py
python3 _partials/sync.py --check --all
python3 Tools/build_versions.py --check
```

`sync.py` の既定対象は `working` だけです。過去の版を確認するときは `--check --version 1.1.0` を指定します。生成器はローカル参照とアンカーを検査し、標準ライブラリだけで動作します。版・言語を切り替えても同じ内容のページへ移動し、存在するアンカーだけを引き継ぎます。JavaScriptがなくても全ページを閲覧できます。

1.0.0 はウェブサイト `d9fe639`、1.1.0 は正式公開タグ `4638bd3`、1.1.2 は `b97b94e` の内容を保存しています。1.1.1 は独立した旧サイトがないため1.1.0から再構成し、Appの正式タグにある4件の修正を明記しています。予定されていた1.0.1は1.1.0へ統合済みなので公開版として追加しません。Gitの日付からAppの公開日を推定しません。

1.1.3 の操作動画は `app-1.1.3` ブランチで作成・確認します。この main へは含めません。公開が決まった際に新しい版の全ページとアセットを追加し、`latest` を変更して再生成してください。変更、コミット、生成は遠隔サイトへの公開を行いません。
