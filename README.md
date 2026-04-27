# 🤖 AI モーニングダイジェスト

毎朝、OpenAI・Anthropic・Google DeepMindなどの公式RSSから  
AI関連ニュースを自動収集・日本語要約してメールで届けます。

**完全無料・サーバー不要・フォークするだけで使えます。**

---

## できること

- 9つの公式ソースから最新AIニュースを毎朝自動取得
- Claude AIが日本語に翻訳・要約（4〜6文の詳細サマリー）
- リッチなHTMLメールとしてGmailで送信
- 毎朝6時（日本時間）に自動実行

---

## セットアップ手順（10分でできます）

### STEP 1: このリポジトリをForkする

右上の **「Fork」ボタン** を押してください。  
あなたのGitHubアカウントにコピーされます。

---

### STEP 2: Anthropic APIキーを取得する

1. [https://console.anthropic.com](https://console.anthropic.com) にアクセス
2. アカウントを作成（無料）
3. 「API Keys」→「Create Key」でキーを発行
4. `sk-ant-...` から始まる文字列をコピーして保存

> 💡 APIの使用料金について：1日1回の実行で月額 **約50〜200円程度**（使用量による）

---

### STEP 3: Gmailのアプリパスワードを取得する

通常のGmailパスワードではなく、専用の「アプリパスワード」が必要です。

1. [Googleアカウント設定](https://myaccount.google.com/security) を開く
2. **「2段階認証プロセス」** を有効にする（まだの場合）
3. 検索欄で「アプリパスワード」と検索して開く
4. アプリ名に「AI Digest」と入力 → **「作成」**
5. 表示された **16文字のパスワード** をコピーして保存

---

### STEP 4: GitHubにシークレット（秘密の設定）を登録する

ForkしたリポジトリのページでSECRETS (Secrets = 外部に見えない設定値) を登録します。

1. リポジトリの **「Settings」** タブを開く
2. 左メニューの **「Secrets and variables」→「Actions」** をクリック
3. **「New repository secret」** ボタンを4回押して、以下を登録：

| Name（名前） | Secret（値） |
|-------------|------------|
| `ANTHROPIC_API_KEY` | `sk-ant-...`（STEP 2で取得） |
| `GMAIL_USER` | `あなたのメールアドレス@gmail.com` |
| `GMAIL_APP_PASSWORD` | `xxxx xxxx xxxx xxxx`（STEP 3で取得） |
| `RECIPIENT_EMAIL` | メールを受け取りたいアドレス（自分でもOK） |

---

### STEP 5: 動作確認（手動実行）

1. リポジトリの **「Actions」** タブを開く
2. 左メニューの **「🤖 AI News Digest」** をクリック
3. **「Run workflow」→「Run workflow」** ボタンを押す
4. 緑のチェックマーク ✅ が出れば成功！
5. 設定したメールアドレスにメールが届いているか確認

---

## 毎朝の自動実行タイミング

```
毎朝 6:00 AM（日本時間）に自動実行されます
```

特に設定は不要です。Forkして設定したら翌朝から自動でメールが届きます。

---

## ソース一覧

| メディア | 種別 |
|---------|------|
| OpenAI News | 公式ブログ |
| Google DeepMind Blog | 公式ブログ |
| Google Blog (AI) | 公式ブログ |
| Hugging Face Blog | 公式ブログ |
| Anthropic News | 公式ブログ |
| TechCrunch AI | テックメディア |
| VentureBeat AI | テックメディア |
| MIT Technology Review | テックメディア |
| arXiv cs.AI | 研究プレプリント |

---

## よくある質問

**Q. 本当に無料ですか？**  
A. GitHubの実行は無料（Publicリポジトリは無制限）。Claude APIのみ従量課金（月数百円程度）。

**Q. 複数人に送れますか？**  
A. `RECIPIENT_EMAIL` にカンマ区切りで複数アドレスを入れると送れます。  
例: `user1@gmail.com,user2@gmail.com`

**Q. 送信時間を変えたいです**  
A. `.github/workflows/daily-digest.yml` の `cron: '0 21 * * *'` を変更してください。  
[cron書き方ツール](https://crontab.guru) が便利です。（JST = UTC+9 なので注意）

**Q. エラーが出ました**  
A. 「Actions」タブでログを確認できます。Secretsの設定ミスが最多原因です。

---

## ライセンス

MIT License - 自由に改変・再配布できます。

---

*Powered by [Claude API](https://anthropic.com) / [rss2json](https://rss2json.com)*
