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

### STEP 2: AIプロバイダーのAPIキーを取得する

**AnthropicとGeminiのどちらか一方でOKです。両方取得しても使えます。**

#### Anthropic（Claude）を使う場合
1. [https://console.anthropic.com](https://console.anthropic.com) にアクセス
2. アカウントを作成 → 「API Keys」→「Create Key」
3. `sk-ant-...` から始まる文字列をコピーして保存

#### Google Gemini Flashを使う場合（無料枠が大きく安い）
1. [https://aistudio.google.com/apikey](https://aistudio.google.com/apikey) にアクセス
2. 「Create API key」→「Create API key in new project」
3. `AIza...` から始まる文字列をコピーして保存

#### Straicoを使う場合（多数のモデルを1つのAPIキーで使い回せる）
1. [https://platform.straico.com/settings-api](https://platform.straico.com/settings-api) にアクセス
2. APIキーをコピーして保存
3. 使いたいモデルを [https://straico.com/multimodel](https://straico.com/multimodel) で確認  
   例: `openai/gpt-4o-mini` / `anthropic/claude-3-5-sonnet` / `google/gemini-flash-1.5`

> 💡 **コスト比較**（1日1回実行・月額目安）  
> Anthropic Claude Opus 4.7: 約100〜200円  
> Gemini 2.5 Flash: 約10〜30円（無料枠内に収まることも多い）  
> Straico: モデルによる（GPT-4o-miniなら約20〜50円）

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

**Secrets（外部に見えない秘密の値）:**

| Name | 値 | 必須？ |
|------|----|-------|
| `ANTHROPIC_API_KEY` | `sk-ant-...` | Claudeを使う場合 |
| `GEMINI_API_KEY` | `AIza...` | Geminiを使う場合 |
| `STRAICO_API_KEY` | Straicoのキー | Straicoを使う場合 |
| `GMAIL_USER` | `あなたのアドレス@gmail.com` | ✅ 必須 |
| `GMAIL_APP_PASSWORD` | 16文字のアプリパスワード | ✅ 必須 |
| `RECIPIENT_EMAIL` | 受け取りたいアドレス | ✅ 必須 |

**Variables（プロバイダー切り替え用の設定値）:**

左メニューの「Secrets and variables」→「Variables」→「New repository variable」で登録:

| Name | 値 | デフォルト |
|------|----|---------|
| `AI_PROVIDER` | `anthropic` / `gemini` / `straico` | `anthropic` |
| `GEMINI_MODEL` | 例: `gemini-2.5-flash` | `gemini-2.5-flash` |
| `STRAICO_MODEL` | 例: `openai/gpt-4o-mini` | `openai/gpt-4o-mini` |

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
