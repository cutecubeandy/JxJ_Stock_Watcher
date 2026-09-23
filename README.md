# JxJ DREAMSCAPE Signed Stock Watcher

A small GitHub Actions monitor for the two signed JxJ `DREAMSCAPE` albums on the SEVENTEEN US Official Store.

## Products

- Daydreamers Ver. (Signed ver.)
- Dreamchasers Ver. (Signed ver.)

## What it does

Every scheduled run:

1. Downloads each product page.
2. Looks for the store's current `Sorry Sold out` message.
3. Compares the result with `state.json`.
4. If a product changes from sold out to available, sends one Discord message with the product link.
5. Saves the new state so Discord is not spammed every five minutes.

It intentionally does **not** test whether the Add to Cart button can be clicked.

## Discord setup

Create a Discord webhook for the channel where you want alerts.

Then in this repository go to:

`Settings -> Secrets and variables -> Actions -> Secrets`

Create a repository secret named:

`DISCORD_WEBHOOK_URL`

Paste the Discord webhook URL as its value.

Do **not** put the webhook URL directly in the code.

## Enable automatic monitoring

The workflow contains a five-minute schedule, but scheduled jobs are disabled by default.

When you are ready, go to:

`Settings -> Secrets and variables -> Actions -> Variables`

Create a repository variable:

- Name: `MONITORING_ENABLED`
- Value: `true`

You can also run it manually from the **Actions** tab before enabling the schedule.

## GitHub Actions usage note

This repository is currently private. Private repositories consume GitHub Actions minutes. A five-minute schedule can use a lot of Actions minutes because each job is billed in whole-minute increments.

For this tiny monitor, a public repository is usually the simplest way to use frequent standard GitHub-hosted Actions without consuming private-repository minutes. The Discord webhook remains safe as long as it is stored in GitHub Secrets.
