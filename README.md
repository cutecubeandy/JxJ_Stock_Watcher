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


## Discord 通知分級

正式監控現在分成兩種通知：

### 沒貨 / 心跳通知

如果建立 Repository variable：

`HEARTBEAT_ENABLED=true`

那麼在本輪沒有任何商品補貨時，監控會送出一般訊息：

```text
🟢 JxJ Stock Watcher 正常運作

Daydreamers Signed：sold_out
Dreamchasers Signed：sold_out

本訊息只是心跳確認，不會 @everyone。
```

這個功能主要用來確認 GitHub Actions、商品頁抓取和 Discord Webhook 都仍然正常。

如果不想收到這類訊息，在 Repository Variables 設定 `HEARTBEAT_ENABLED=false` 即可。

### 補貨通知

只要任一商品從 `sold_out` 變成 `available`，會送出高優先通知：

```text
@everyone
🚨 JxJ DREAMSCAPE 親簽版補貨！

商品名稱
商品網址
```

補貨通知會要求 Discord 解析 `@everyone` mention；實際是否通知所有成員仍受該 Discord 頻道 / Webhook 的 mention 權限控制。


## 目前正式設定

- 排程：每 5 分鐘一次，使用每小時 2、7、12、17、22、27、32、37、42、47、52、57 分，避開整點高負載。
- `MONITORING_ENABLED`：已不再需要。
- `HEARTBEAT_ENABLED`：預設開啟；只有明確設為 `false` 才關閉。
- `DISCORD_WEBHOOK_URL`：仍必須保存在 GitHub Secrets。
