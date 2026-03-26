# Optional — Add a Telegram Bot Client

## Background

The Flutter web client connects to the agent via WebSocket. A Telegram bot is another client that connects the same way — demonstrating that **the agent is the interface, not any particular frontend**.

Same agent, same tools, same answers — different client.

### Note on Telegram in Russia

The Telegram Bot API (`api.telegram.org`) is blocked from most Russian servers. Your university VM cannot reach it.

**Workaround:** The Telegram bot connects to nanobot via WebSocket (local Docker network — no internet needed). Telegram polling runs from a machine that *can* reach the Bot API — your local machine, or a non-Russian server. This is a real-world constraint — production systems often need to work around network restrictions.

## What to do

1. Get a Telegram bot token from [@BotFather](https://t.me/BotFather).

2. Either add an existing Telegram bot client as a submodule, or implement one yourself. The bot should:
   - Connect to nanobot via WebSocket (`ws://nanobot:8765`)
   - Relay user messages to the agent and forward responses back to Telegram
   - Handle `/start` and `/help` slash commands directly (without the agent)

3. Add a `client-telegram-bot` service to `docker-compose.yml`:
   - Environment: `BOT_TOKEN`, `NANOBOT_WS_URL`
   - Depends on: `nanobot`

4. Deploy and test. Open Telegram, find your bot, and ask it a question.

5. Ask the same question in the Flutter app and in Telegram. Compare the responses — they should be identical (same agent, same tools).

## Acceptance criteria

- The Telegram bot runs as a Docker Compose service (or locally if the VM can't reach Telegram API).
- Free-text messages are routed to the agent and responses appear in Telegram.
- The same queries work from both Telegram and the Flutter web app.
