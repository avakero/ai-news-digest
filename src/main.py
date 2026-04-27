"""
AI News Digest - メイン処理
毎朝、信頼できるAI関連RSSを取得・翻訳・要約してメール送信する

AI_PROVIDER 環境変数で使用するLLMを切り替え可能:
  anthropic（デフォルト）: Claude Opus 4.7
  gemini               : Gemini 2.5 Flash
  straico              : Straico経由で任意モデル（OpenAI互換 v2 API）
"""

import os
import json
import smtplib
import requests
from datetime import datetime, timezone, timedelta
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from dateutil import parser as dateparser

# ──────────────────────────────────────────
# 設定: RSSソース一覧（ホワイトリスト限定）
# ──────────────────────────────────────────
SOURCES = [
    {"name": "OpenAI",           "url": "https://openai.com/news/rss.xml"},
    {"name": "Google DeepMind",  "url": "https://deepmind.google/blog/rss.xml"},
    {"name": "Google Blog AI",   "url": "https://blog.google/technology/ai/rss/"},
    {"name": "Hugging Face",     "url": "https://huggingface.co/blog/feed.xml"},
    {"name": "Anthropic",        "url": "https://www.anthropic.com/news"},
    {"name": "TechCrunch AI",    "url": "https://techcrunch.com/category/artificial-intelligence/feed/"},
    {"name": "VentureBeat AI",   "url": "https://venturebeat.com/category/ai/feed/"},
    {"name": "MIT Tech Review",  "url": "https://www.technologyreview.com/feed/"},
    {"name": "arXiv cs.AI",      "url": "http://export.arxiv.org/rss/cs.AI"},
]

RSS2JSON_API  = "https://api.rss2json.com/v1/api.json"
HOURS_WINDOW  = 36  # 過去何時間以内の記事を対象にするか

# 使用するAIプロバイダー（環境変数で切り替え）
AI_PROVIDER     = os.environ.get("AI_PROVIDER", "anthropic").lower()
GEMINI_MODEL    = os.environ.get("GEMINI_MODEL",  "gemini-2.5-flash")
STRAICO_MODEL   = os.environ.get("STRAICO_MODEL", "openai/gpt-4o-mini")
STRAICO_API_URL = "https://api.straico.com/v2"


# ──────────────────────────────────────────
# RSS取得（rss2json.com プロキシ経由）
# ──────────────────────────────────────────
def fetch_rss(source: dict) -> list[dict]:
    try:
        resp = requests.get(
            RSS2JSON_API,
            params={"rss_url": source["url"]},
            timeout=20,
        )
        resp.raise_for_status()
        data = resp.json()
        if data.get("status") != "ok":
            print(f"[SKIP] {source['name']}: status={data.get('status')}")
            return []
        return [
            {
                "title":       item.get("title", ""),
                "link":        item.get("link", ""),
                "pubDate":     item.get("pubDate", ""),
                "description": item.get("description", "")[:800],
                "source":      source["name"],
            }
            for item in data.get("items", [])
        ]
    except Exception as e:
        print(f"[SKIP] {source['name']}: {e}")
        return []


def is_recent(pub_date_str: str, hours: int = HOURS_WINDOW) -> bool:
    try:
        pub = dateparser.parse(pub_date_str)
        if pub and pub.tzinfo is None:
            pub = pub.replace(tzinfo=timezone.utc)
        cutoff = datetime.now(timezone.utc) - timedelta(hours=hours)
        return pub >= cutoff if pub else True
    except Exception:
        return True  # パース失敗時は含める


# ──────────────────────────────────────────
# 共通プロンプト生成
# ──────────────────────────────────────────
def _build_prompt(articles: list[dict]) -> str:
    articles_text = "\n\n".join(
        f"[{i + 1}] SOURCE: {a['source']}\n"
        f"TITLE: {a['title']}\n"
        f"URL: {a['link']}\n"
        f"DATE: {a['pubDate']}\n"
        f"DESCRIPTION: {a['description']}"
        for i, a in enumerate(articles[:20])
    )
    return f"""あなたはAIニュースのキュレーターです。
以下の記事リストから最も重要な7〜8件を選び、日本語に翻訳・要約してください。

【選定優先度】
1. 主要ラボ（OpenAI・Anthropic・Google・Meta・Mistral等）の新モデル・新機能リリース
2. 大型製品ローンチ・開発者向けツール
3. 大型資金調達・買収・規制ニュース
4. 注目ベンチマーク・研究成果
5. 重要なパートナーシップ

【記事リスト】
{articles_text}

【出力形式】JSONのみを返してください（コードブロック不要）:
[
  {{
    "title_jp":   "自然な日本語タイトル",
    "title_en":   "元の英語タイトル",
    "summary_jp": "4〜6文の詳細な日本語要約（背景・意義・影響を含める）",
    "source":     "ソース名",
    "url":        "記事のURL",
    "pub_date":   "公開日（例: 2026年4月27日）"
  }}
]"""


def _parse_json(raw: str) -> list[dict]:
    raw = raw.strip()
    if raw.startswith("```"):
        raw = raw.split("```")[1]
        if raw.startswith("json"):
            raw = raw[4:]
    return json.loads(raw.strip())


# ──────────────────────────────────────────
# Anthropic Claude で翻訳・要約・選定
# ──────────────────────────────────────────
def _summarize_anthropic(prompt: str) -> list[dict]:
    import anthropic as _anthropic
    client = _anthropic.Anthropic()
    message = client.messages.create(
        model="claude-opus-4-7",
        max_tokens=4096,
        messages=[{"role": "user", "content": prompt}],
    )
    return _parse_json(message.content[0].text)


# ──────────────────────────────────────────
# Google Gemini Flash で翻訳・要約・選定
# ──────────────────────────────────────────
def _summarize_gemini(prompt: str) -> list[dict]:
    import google.generativeai as genai
    genai.configure(api_key=os.environ["GEMINI_API_KEY"])
    model = genai.GenerativeModel(
        model_name=GEMINI_MODEL,
        generation_config={"response_mime_type": "application/json"},
    )
    response = model.generate_content(prompt)
    return _parse_json(response.text)


# ──────────────────────────────────────────
# Straico（OpenAI互換 v2）で翻訳・要約・選定
# ──────────────────────────────────────────
def _summarize_straico(prompt: str) -> list[dict]:
    from openai import OpenAI
    client = OpenAI(
        api_key=os.environ["STRAICO_API_KEY"],
        base_url=STRAICO_API_URL,
    )
    response = client.chat.completions.create(
        model=STRAICO_MODEL,
        messages=[{"role": "user", "content": prompt}],
        max_tokens=4096,
    )
    return _parse_json(response.choices[0].message.content)


# ──────────────────────────────────────────
# プロバイダーを自動選択して実行
# ──────────────────────────────────────────
def select_and_summarize(articles: list[dict]) -> list[dict]:
    prompt = _build_prompt(articles)
    if AI_PROVIDER == "gemini":
        print(f"[AI] Gemini ({GEMINI_MODEL}) で要約します")
        return _summarize_gemini(prompt)
    elif AI_PROVIDER == "straico":
        print(f"[AI] Straico ({STRAICO_MODEL}) で要約します")
        return _summarize_straico(prompt)
    else:
        print("[AI] Claude (claude-opus-4-7) で要約します")
        return _summarize_anthropic(prompt)


# ──────────────────────────────────────────
# HTMLメール組み立て
# ──────────────────────────────────────────
def build_html(articles: list[dict], date_str: str, sources_summary: str) -> str:
    articles_html = ""
    for a in articles:
        articles_html += f"""
    <div class="article">
      <div class="article-source">{a['source']}</div>
      <div class="article-title-jp">{a['title_jp']}</div>
      <div class="article-title-en">({a['title_en']})</div>
      <div class="divider"></div>
      <div class="article-body">{a['summary_jp']}</div>
      <a href="{a['url']}" class="article-link">記事を読む →</a>
      <div class="article-meta">🕐 {a['pub_date']}</div>
    </div>"""

    return f"""<!DOCTYPE html>
<html>
<head><meta charset="UTF-8">
<style>
  body {{ margin: 0; padding: 0; background-color: #f0f4f8; font-family: 'Helvetica Neue', Arial, sans-serif; }}
  .wrapper {{ max-width: 680px; margin: 0 auto; background: #ffffff; }}
  .header {{ background: linear-gradient(135deg, #1a1a2e 0%, #16213e 50%, #0f3460 100%); padding: 40px 32px; text-align: center; }}
  .header-icon {{ font-size: 48px; margin-bottom: 12px; }}
  .header-title {{ color: #fff; font-size: 26px; font-weight: 700; margin: 0 0 6px; }}
  .header-subtitle {{ color: #a0aec0; font-size: 14px; margin: 0; }}
  .header-date {{ display: inline-block; margin-top: 16px; background: rgba(255,255,255,0.1); color: #e2e8f0; font-size: 13px; padding: 6px 16px; border-radius: 20px; }}
  .content {{ padding: 32px; }}
  .section-label {{ font-size: 11px; font-weight: 700; letter-spacing: 2px; color: #718096; text-transform: uppercase; margin-bottom: 20px; }}
  .article {{ border: 1px solid #e2e8f0; border-radius: 12px; padding: 24px; margin-bottom: 20px; position: relative; overflow: hidden; }}
  .article::before {{ content: ''; position: absolute; top: 0; left: 0; width: 4px; height: 100%; background: linear-gradient(180deg, #667eea, #764ba2); }}
  .article-source {{ font-size: 11px; font-weight: 700; letter-spacing: 1px; text-transform: uppercase; color: #667eea; margin-bottom: 8px; }}
  .article-title-jp {{ font-size: 17px; font-weight: 700; color: #1a202c; line-height: 1.4; margin-bottom: 4px; }}
  .article-title-en {{ font-size: 12px; color: #718096; margin-bottom: 14px; font-style: italic; }}
  .article-body {{ font-size: 14px; color: #4a5568; line-height: 1.8; margin-bottom: 16px; }}
  .article-link {{ display: inline-block; background: linear-gradient(135deg, #667eea, #764ba2); color: white; text-decoration: none; padding: 8px 20px; border-radius: 6px; font-size: 13px; font-weight: 600; }}
  .article-meta {{ font-size: 12px; color: #a0aec0; margin-top: 12px; }}
  .footer {{ background: #1a1a2e; padding: 28px 32px; text-align: center; }}
  .footer-text {{ color: #718096; font-size: 13px; line-height: 1.6; }}
  .footer-count {{ color: #667eea; font-weight: 700; font-size: 20px; }}
  .divider {{ height: 1px; background: linear-gradient(90deg, transparent, #e2e8f0, transparent); margin: 4px 0 24px; }}
  .source-list {{ background: #f7fafc; border-radius: 8px; padding: 16px 20px; margin-top: 24px; font-size: 12px; color: #4a5568; line-height: 1.7; }}
  .source-list strong {{ color: #1a202c; }}
</style></head>
<body>
<div class="wrapper">
  <div class="header">
    <div class="header-icon">🤖</div>
    <h1 class="header-title">AI モーニングダイジェスト</h1>
    <p class="header-subtitle">本日の重要な AI 関連ニュースをまとめてお届けします</p>
    <span class="header-date">📅 {date_str}</span>
  </div>
  <div class="content">
    <div class="section-label">📰 本日のトップニュース</div>
    {articles_html}
    <div class="source-list">
      <strong>📡 参照ソース（公式RSS / 信頼メディア限定）</strong><br>
      {sources_summary}
    </div>
  </div>
  <div class="footer">
    <div class="footer-count">{len(articles)}件</div>
    <div class="footer-text">の AI 関連ニュースをお届けしました<br>各リンクをクリックして詳細をご確認ください</div>
  </div>
</div>
</body>
</html>"""


# ──────────────────────────────────────────
# Gmail送信（SMTPアプリパスワード方式）
# ──────────────────────────────────────────
def send_email(html_body: str, subject: str, to_email: str, from_email: str, app_password: str) -> None:
    msg = MIMEMultipart("alternative")
    msg["Subject"] = subject
    msg["From"]    = from_email
    msg["To"]      = to_email
    msg.attach(MIMEText(html_body, "html", "utf-8"))

    with smtplib.SMTP_SSL("smtp.gmail.com", 465) as server:
        server.login(from_email, app_password)
        server.sendmail(from_email, to_email, msg.as_string())
        print(f"✅ メール送信完了 → {to_email}")


# ──────────────────────────────────────────
# メイン処理
# ──────────────────────────────────────────
def main():
    recipient    = os.environ["RECIPIENT_EMAIL"]
    sender       = os.environ["GMAIL_USER"]
    app_password = os.environ["GMAIL_APP_PASSWORD"]

    # 1. RSS全ソースを取得
    all_articles  = []
    source_counts = {}
    for source in SOURCES:
        articles = fetch_rss(source)
        recent   = [a for a in articles if is_recent(a["pubDate"])]
        source_counts[source["name"]] = len(recent)
        all_articles.extend(recent)
        print(f"[RSS] {source['name']}: {len(recent)}件（36h以内）")

    # 2. 記事が少ない場合は期間を緩和
    if len(all_articles) < 5:
        print("⚠️ 記事が5件未満のため、期間フィルタを72時間に緩和します")
        all_articles = []
        for source in SOURCES:
            articles = fetch_rss(source)
            recent   = [a for a in articles if is_recent(a["pubDate"], hours=72)]
            source_counts[source["name"]] = len(recent)
            all_articles.extend(recent)

    if not all_articles:
        print("❌ 記事を取得できませんでした。終了します。")
        return

    print(f"\n合計 {len(all_articles)} 件の記事を取得。Claudeで選定・要約中...\n")

    # 3. Claude APIで選定・翻訳・要約
    selected = select_and_summarize(all_articles)
    print(f"✅ {len(selected)} 件を選定しました")

    # 4. 日本語の日付文字列を生成
    jst        = timezone(timedelta(hours=9))
    now_jst    = datetime.now(jst)
    weekdays   = ["月", "火", "水", "木", "金", "土", "日"]
    date_str   = f"{now_jst.year}年{now_jst.month}月{now_jst.day}日（{weekdays[now_jst.weekday()]}）"

    sources_summary = " / ".join(f"{k}({v})" for k, v in source_counts.items())

    # 5. HTMLメールを組み立て・送信
    html    = build_html(selected, date_str, sources_summary)
    subject = f"🤖 AIモーニングダイジェスト — {date_str}"
    send_email(html, subject, recipient, sender, app_password)


if __name__ == "__main__":
    main()
