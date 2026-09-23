# JxJ DREAMSCAPE 親簽版補貨監控器

這是第一版（V1）的補貨監控程式，用來監控 SEVENTEEN US Official Store 首頁目前前兩個已售完的 JxJ `DREAMSCAPE` 親簽版本：

- Daydreamers Ver. (Signed ver.)
- Dreamchasers Ver. (Signed ver.)

## V1 架構

```text
SEVENTEEN 商品頁
      ↓
Python 檢查是否仍出現 "Sorry Sold out"
      ↓
GitHub Actions 每 5 分鐘執行
      ↓
與 state.json 的上一次狀態比較
      ↓
sold_out → available
      ↓
Discord Webhook 通知
```

這一版刻意保持簡單：

- 不模擬瀏覽器操作。
- 不測試 Add to Cart 是否真的可以點。
- 不自動購買。
- 只判斷商品頁是否仍顯示 `Sorry Sold out`。
- 只有從 `sold_out` 變成 `available` 時才通知一次，避免每 5 分鐘重複洗 Discord。

## 監控的商品

### Daydreamers Signed

https://seventeenshopus.com/products/jxj-1st-mini-album-dreamscape-daydreamers-ver-signed-ver

### Dreamchasers Signed

https://seventeenshopus.com/products/jxj-1st-mini-album-dreamscape-dreamchasers-ver-signed-ver

## GitHub Actions 注意事項

### 1. 最快每 5 分鐘

GitHub Actions 的排程（scheduled workflow）可以設定到每 5 分鐘執行一次。

本專案使用：

```yaml
cron: "*/5 * * * *"
```

但 GitHub 不保證準時執行。在平台負載較高時，排程可能延遲，甚至極少數情況可能被丟棄。

因此這是「接近即時」監控，不是真正的即時監控。

### 2. Private Repo 會消耗 Actions 分鐘

Private Repository 使用 GitHub-hosted runner 時，會消耗帳號方案內含的 GitHub Actions 分鐘。

若每 5 分鐘跑一次：

```text
12 次 / 小時
× 24 小時
× 30 天
≈ 8,640 次 / 月
```

而 Private Repo 的 job 計費時間會以分鐘計算並向上取整，因此這種高頻率監控不適合長期放在 Private Repo。

### 3. Public Repo 比較適合這個專案

Public Repository 使用標準 GitHub-hosted runner 基本上免費且不限一般 Actions 分鐘，因此目前最推薦的部署方式是：

```text
Public Repo
    +
GitHub Actions 每 5 分鐘
    +
Discord Webhook
```

程式本身可以公開，但 Discord Webhook 不應該寫進程式碼。

### 4. Discord Webhook 放 GitHub Secrets

到：

```text
Settings
→ Secrets and variables
→ Actions
→ Secrets
→ New repository secret
```

建立：

```text
Name:
DISCORD_WEBHOOK_URL

Value:
你的 Discord Webhook URL
```

程式執行時會透過：

```yaml
${{ secrets.DISCORD_WEBHOOK_URL }}
```

讀取，所以 Webhook URL 不會直接出現在公開程式碼中。

### 5. Public Repo 60 天無活動

GitHub 會自動停用連續 60 天沒有 Repository activity 的 Public Repository scheduled workflows。

如果這個 Repo 長時間完全沒有 commit、issue、PR 等活動，要記得確認 Actions 是否仍啟用。

## 啟用自動監控

目前 V1 已經包含每 5 分鐘的 schedule，但為了避免這個 Repo 在仍為 Private 時就開始大量消耗 Actions 分鐘，排程暫時有一個開關。

當你：

1. 已設定 `DISCORD_WEBHOOK_URL`
2. 已決定要開始正式監控
3. 建議已把 Repo 改成 Public

之後，到：

```text
Settings
→ Secrets and variables
→ Actions
→ Variables
→ New repository variable
```

建立：

```text
Name:
MONITORING_ENABLED

Value:
true
```

之後 scheduled workflow 就會開始工作。

## 手動執行

即使 `MONITORING_ENABLED` 尚未開啟，也可以：

```text
Actions
→ Monitor JxJ signed stock
→ Run workflow
```

手動跑一次。

這很適合第一次設定 Discord Webhook 後確認程式能正常抓到兩個商品。

## 目前狀態

V1 初始狀態：

```json
{
  "daydreamers_signed": "sold_out",
  "dreamchasers_signed": "sold_out"
}
```

如果其中一個變成有貨，例如：

```text
daydreamers_signed:
sold_out → available
```

Discord 就會收到類似：

```text
🚨 JxJ DREAMSCAPE 親簽版補貨！

JxJ DREAMSCAPE Daydreamers Ver. (Signed ver.)
https://seventeenshopus.com/...
```

## 如果未來真的太慢

GitHub Actions 適合這個 V1，因為：

- 不需要自己的電腦 24 小時開機。
- 設定簡單。
- Public Repo 幾乎沒有執行成本。
- 很適合拿來練 GitHub Actions。

但如果實際觀察後發現商品常在 1–2 分鐘內售罄，那 GitHub Actions 的 5 分鐘最低排程加上可能的執行延遲就不夠快。

到時再把相同的 Python 程式搬到更適合高頻率執行的環境即可，不需要現在就把架構做複雜。
