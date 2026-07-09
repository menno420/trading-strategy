# Video source — salvaged lane input (2026-07-09)

> **Status:** `reference` — salvaged input for the video-strategy lane. The
> lane's session died at provision (2026-07-09T18:53:14Z, identical
> setup-script error, third kill; it never started). This doc preserves
> everything gen-2 needs to resume the lane without re-extracting.

## Source video

| Field | Value |
|---|---|
| URL | https://youtu.be/G6l6HfMbOLc |
| Title | I Built a FREE AI Trading Bot With Claude + TradingView (Step by Step) |
| Channel | Trading with DaviddTech — https://www.youtube.com/channel/UC7NJLsf6IonOy8QI8gt5BeA |
| Duration | 21:34 |
| Uploaded | 2026-07-09 |
| Views at capture | 4,749 (captured 2026-07-09T20:08Z) |

### Description (verbatim, trimmed of promo repetition)

> I Built a Profitable AI Trading Bot with Claude & TradingView (Step-by-Step)
>
> I built an AI trading bot with Claude and TradingView that delivers insane
> results. And today, I'm going to show you exactly how you can build your own
> for free. No coding required, no expensive servers, and I'll even show you
> the exact step most people get wrong that turns losing strategies into
> highly profitable systems. We are taking Claude, hooking it up to a free
> backtesting tool, finding the absolute best settings, and connecting it to a
> broker to trade 100% automatically.
>
> In this video you'll discover:
> - How to build and optimize a trading bot using Claude Code for free
> - How to use TradingKit (Trader Dev) to backtest strategies without burning tokens
> - How to add your Pine Script strategy to TradingView to run 24/7
> - How to connect TradingView directly to Bybit using Trigger.trade
> - The exact webhook alert setup that automates your execution
> - Crucial lessons on forward testing and portfolio diversification
>
> Video Chapters:
> 0:00 – I Built an AI Trading Bot with Claude ·
> 0:42 – The Setup: Tools You Need ·
> 2:31 – Step 1: Coding & Optimizing with Claude Code ·
> 8:30 – Setting up a 24-Hour Optimization Loop ·
> 10:43 – Step 2: Adding the Strategy to TradingView ·
> 12:24 – Step 3: Connecting to Bybit with Trigger.trade ·
> 16:24 – Wiring the Alert Message & Webhook ·
> 19:53 – Crucial Lessons: Forward Testing & Diversification
>
> Quick note: everything here is for education, not financial advice.

## How the transcript was obtained (methods log)

1. **`youtube-transcript-api` 1.2.4 — FAILED.** Exact error:
   `RequestBlocked: Could not retrieve a transcript for the video https://www.youtube.com/watch?v=G6l6HfMbOLc! This is most likely caused by: YouTube is blocking requests from your IP. … You are doing requests from an IP belonging to a cloud provider (like AWS, Google Cloud Platform, Azure, etc.). Unfortunately, most IPs from cloud providers are blocked by YouTube.`
2. **`yt-dlp --skip-download --write-auto-subs --write-subs --sub-langs en,nl` — PARTIAL.**
   Video metadata (title/channel/description/caption-track URLs) extracted
   successfully; the subtitle *download* step failed with exact error:
   `ERROR: [download] Got error: Failed to perform, curl: (35) Recv failure: Connection reset by peer. See https://curl.se/libcurl/c/libcurl-errors.html first for more details.. Giving up after 10 retries`
   (plus warnings: no JS runtime found; ffmpeg not found).
3. **Direct GET of the `timedtext` json3 caption URL** taken from the yt-dlp
   metadata (`automatic_captions.en`, ext `json3`), fetched with python
   `requests` through the agent proxy with
   `REQUESTS_CA_BUNDLE=SSL_CERT_FILE=/root/.ccr/ca-bundle.crt` — **SUCCESS**:
   HTTP 200, 449,534 bytes, 587 auto-caption segments (English, auto-generated).

The transcript below is the English auto-caption track, joined into readable
paragraphs with sparse `[m:ss]` timestamps (one per ~minute). Auto-caption
quirks preserved (e.g. "Two Bit"/"by bit" = Bybit, "Pinescript"/"kind script" =
Pine Script, "Trader Kit"/"trader dev" = TradingKit/Trader Dev,
"school.com" = skool.com, "takerit" = take-profit).

## Transcript (auto-captions, verbatim)

**[0:00]**
I built an AI trading bot with Claude and Trading View that delivers insane results. Today, I'm going to show you exactly how you can build your own for free. And guys, in case you don't know who I am, my name's David. I've been building trading bots here on YouTube for over 5 years. I was awarded top trader on Two Bit. So, I am a real trader trading real money. By the end of this video, you'll have a profitable strategy built by Claude for you. A real back test and full automation that takes trades on your broker. Zero code. And I'll even show you the step that most people get wrong. And that turns results from this into this. Right, the setup. This is going to be the boring part. So, I'm going to get through this as fast as we possibly can. You're going to need a couple of things to get started. First and foremost is going to be an account on claude.com. This is our AI which is going to be building and back testing our actual bots before we actually take them live. You are not locked to Claude. You can actually use Open AI or any

**[1:02]**
other model, but I prefer Claude myself. So, I'm going to click here, download the desktop version. Desktop version looks something like this. We just go over. I'm going to be using Claude code today. You can use chat once again, but code gives you loads more features and a lot more flexibility and you don't have to be worried about learning to code. Cloud will take care of everything from actually coding and actually setting everything up so you don't have to worry about anything. Next, we're going to be going over to Trading View. Trading View is our charting platform which allows us to go and see all of the entries on the chart. Not only that, we're going to be using Trading View's alert system for us to be able to connect over to our brokers. Next, we're going to be using tradingkit.com. Tradingkit.com is is a free product that I built myself which allows AI to have the tools it needs to be able to back test trading strategies. This is extremely powerful and something I'm very proud that we built as a community. Now, this is also free. I'll show you how to set it up and sign up in a couple of seconds. Next, another

**[2:02]**
product which is free trigger.trade. This is going to allow us to connect over to our broker. Now, this one is currently only crypto only, but if you prefer, you can actually use Alpeka or use a connector to your exchange. It's very similar as a setup, so don't worry about getting lost at that part there. And finally, you will need an account on a broker. I'm currently using Bybit today because it is the exchange that I use pretty much every day for trading. Right now, we got that bit out of the way. Let's start building this thing. Okay, so we're going to be doing this in three simple steps. First, we're going to be asking Claude code to create a simple bot on a proven strategy. Number two, we're going to be adding that strategy to Trading View so that it can run 247 without us having to buy expensive servers. And number three, we'll be adding that over to our exchange so that we actually trade this all automatically. So, let's get over to my computer and let's start building. Okay, so we're going to start off with

**[3:03]**
Claude. I hope you've already downloaded Claude from the official website Claude desktop and we're going to be using the code version over the side here. The first thing that we're going to need to do is install the tools so that Claude can actually back test our trading strategies. There's no point in setting up a bot and just asking Claude to trade it for you because it'll probably lose you money in the long run. We're going to be back testing. We're going to know our data. We want something that's profitable in the long term and not something that's going to wreck us on justopium. So, first things first, we're going to go over to tradingkit.com and we're going to sign up for an account. I've already got an account, so I'm just going to click on my accounts over here. And what this thing does is it allows Claude to have the tools so that it can actually back test trading strategies. Not only can it back test, it can optimize to find the best settings without burning tons of tokens because everything's done on their server. As you can see, the community from Trader Kit has made tons and tons of strategies, and they're all shared between the actual community. So, first

**[4:03]**
things first, we're going to go over to my account up here, and we're going to install this baby. We're going to click copy on the code, which is here, which is just the install instructions for Claude. I click on new session, and we're just going to go, "Hey there, buddy. Could you please install this for me globally so that it works on Claude code and Claude Co-work?" Boom. Going to hit enter. that's going to go away and install that globally so that we have access throughout all of our sessions. Okay, once that's installed, we're going to go over back to the website and we're going to have to get our API key from the trader dev website. Mine is already authorized as you can see just here. You will literally have to copy and paste that over to Claude. Hey there buddy, could you kindly authorize my trader dev install for me? And you hit enter and it will authorize it for you. I've already authorized. I don't know how to do it right now, so I'm just going to leave it as it is. Right. Once we're installed, the next thing we need to do is test the connection and make sure it's actually working. So, I'm going to ask Claude, "Hey there, buddy. Could you back test a

**[5:05]**
trading strategy on a 1 hour time frame? Just test it on BTCUSDT just to make sure it's working." Boom. So, what it's doing now is it's already authenticated. It's going to go away and do a back test. So, this is actually coding in Pinescript. kind script is the native language of trading view. So, it's actually going to go away and code this bot in a language that trading view will understand. Why is this important? Because if you're building a strategy on your computer and you turn your computer off, your strategy will stop running, which puts you in a position where either you have to put it up to a server, which costs money, or you'll have to have your computer turned on all day and risk losing those assets. So, what we've done is we've coded in Pine Script so that we can use Trading View. As you can see, it's gone away and made that back test result. If I click on full report, you can see this is the back test that it's done. Doesn't look amazing, but that is not a problem because we can also ask it to optimize our strategy. Hey there, buddy. The

**[6:05]**
strategy doesn't look great. Could you optimize it for me? Come up with an optimizing plan and optimize all of the settings until we find the best ones. Okay, so what it's done is it's come up with a plan. It's informed me that there is actually only two settings in this strategy, which is great. It means that we actually know what's going on. And it is actually intelligently optimizing instead of doing it randomly. It's gone away. It's going to be optimizing the strategy. It's going to try 80 different settings all in the background without burning too many tokens. The way this works is that the optimization actually happens on Trader Dev's servers. So, as you can see, we've only burnt 711 tokens so far. If this was optimizing manually and back testing every time, we'd be burning that at least every single optimization. Instead, Claude just pauses, waits for it to optimize, and then comes back with the results after optimization is done. Okay, so I actually asked Claude to give me the link so I can show you guys that it's actually optimized in the background. We can see the process currently is at 23%.

**[7:07]**
We have a heat map here that gives us the profit factor. We are looking for the best profit factor. Currently, we've gone through 29 of 500 and boom, we're done. So, as you can see, it has gone through and tested all of these different settings for the EMA, slow and fast settings. So, let me explain. In the background, what it's done is it's added a trading strategy that has two moving averages, but we don't know the best settings. So, we don't know the length of the best settings of the EMA. It's gone away and it has changed those lengths as you can see here on the screen from 110 all the way up to 400 and from 10 all the way up to 100 to try and find the best settings. And it is found that the most profitable trading strategy would be EMA slow at 400 and the fast moving average at 45. That gives us a profit factor of 1.86. If I click on it, you can see the back test has considerably improved and looks

**[8:10]**
a lot lot better. We are, as a matter of fact, in profit of 281%. Now, that took us literally seconds. I prompted Claude only a couple of prompts asking it to build a strategy. What I'm going to show you next is going to be its kind of super power. Okay, so it's given us back the code that we will use a little bit later inside of Trading View, which I'll show you. But here is the next step of the creation of a profitable bot. What we're going to do is we're going to ask Claude to go in a loop for 24 hours to try and find the best settings. We're going to give it a goal of finding the most profitable trading strategy using the optimizer so that we don't burn through too many credits. So to do that, what I've done is created this prompt here, which you will be able to find in the pinned comment. This is my expert systematic trader who's going to go away and look for a trading strategy on BTCUSDT on the 1 hour time frame. We are not locked in the slightest to crypto. We can use anything like gold or forex, but for

**[9:12]**
simplicity, I'm just going to be using BTC today. So, I'm going to go down to the bottom. I'm going to hit enter. It's giving me instructions and rules. It's telling me it's ready and I'm going to then set it a goal. Okay, so it has actually started. So, the thing that's very important in this prompt is that we've given it a goal and we've also asked it to set up a loop. That loop is going to go away every 15 minutes and try and find best settings for the trading strategy. If the trading strategy fails, it will move on to the next one and not spend hours trying to optimize something that maybe looks overfit. So, we're going to leave Claude for the next 24 hours to see whether it comes up with something profitable that we can actually trade. Okay. So as you can see the back testings have started. We already have tons of strategies that have been back tested. I'm obviously not going to sit waiting 24 hours. I've prepared this one in advance for you guys so that we can do this all together. Okay. So the strategy after 24 hours with the optimization for sharp

**[10:14]**
ratio has come back and looks a little bit like this. We have over 500% net profit and an 11% max draw down and 141 closed trades which looks absolutely amazing. And guys, this community is all linked to our school.com where you can come and learn everything that I've learned over the past 5 years and get access to all of my tools in one single place. The school is very new, but you are more than welcome. You'll be able to find links down in the description and also in the pinned comment. Okay, now that we've got the back test on the website, we're going to go over to task two where we're going to be adding this strategy to Trading View. Okay, so now if I take this strategy and put it onto Trading View and add the fees from my broker to make sure that it's all working. Let's see whether we get good results. So to do this, we need to scroll down to the bottom of the page where you will find the code for the super trend flip EMA MACD on the 4hour on BTCUSDT. We're going to copy that. Okay. So if I

**[11:15]**
go over to Trading View where I have a brand new chart, we are on BTCUSDT on the 4hour time frame. As you can see just here, I'm going to go over to the pine icon just over in the corner over here. We're going to go over and create a new strategy. We're then going to go Ctrl A CtrlV on our keyboard, Ctrl S, and that will save this strategy to Trading View. So, this is where Trading View is really important to us. We're going to be able to double check the back test. Click here and go over to the settings. We're going to be able to add the fees for commission, our initial capital, and our default order size. This will give us a second back test which looks like this. Very similar to what we got off of trade of dev. We have over 500% net profit, 15% max draw down and 141 closed trades. Most important, we have a profit factor of 2.295. And the equity curve looks absolutely amazing. So now we have all of this

**[12:17]**
data. We're going to pass over to number three where we're going to be connecting this strategy over to our exchange. Okay, now that we have our bot ready, it's on trading view. We're going to have to go over to the automation. We want this baby to actually trade for us directly on our exchanges whilst we're at the beach or even sleeping. So, we're going to have to use a middleman service. What a middleman service does is it sits between Trading View and your exchange and kind of works like a translator. It takes the trades from Trading View and translates that code over to a code that your exchange understands. Today, we're going to be using Trigger Trade. Number one, because it is free. Number two, because it is anonymous. Trigger Trade was built to be an anonymous link between Trading View and your exchange. They never save any of your API codes on their servers. And the reason I know that is because I actually made it. Okay, for this part to work, we're going to have to do a couple of steps as well. First of all, we need to go over to our exchange and get the

**[13:17]**
API keys and secrets. This allows trigger trade to take the signal from Trading View and send it to your exchange with a kind of a special password that only you and Trading View actually know. Number two, we're going to set up an alert on Trading View so that every time that there is a trade, it will ping Trigger Trade and tell them about the trade so that it can then eventually ping your exchange. And everything is encrypted and stored on your Trading View account. So you don't have to worry about leaving your computer on in the background. You can sleep at night, go out with your family and not have to worry. Okay, so here I am on Trigger Trade. I'm already logged in. I have an account as I said. Now you can do this two ways. You can either install it onto Claude and just ask Claude to do it for you or you can just go through this simple form and actually do it online. I'm going to do it online. It'll take a couple of seconds and it's easier for me to explain to you guys. You can simply install this skill and ask Claude to do all of this for you. Right, first things first, we're going to choose our exchange. I'm on buy bit, so I'm going to be using by bit. We're

**[14:17]**
going to click continue. And then we have to give it our API key and secrets. I'm going to go over to Bybit to create APIs and secrets. We need to go over to our avatar on the side here and click on this API button just here, which will allow us to create that password that you're going to give over to Trading Views so that it can take your trades. We're going to click create a new key system generated key and we're going to go up to the top here. Click third party. Type in David Tech read right unified trading. Now, one thing that is very important is that your funds are actually in the right account. Depends if you're going to be trading crypto, you might want to use this. Otherwise, you can use another service. There's absolutely tons of them out there. We're going to click unified trading. We do not need access to the wallet or the exchange here. Here, we're just going to click then submit. And that will ask us to add our 2FA. I'm not going to do this today cuz I have an API key already and secret set up. So, I'm just going to go over and type them in. Okay. Boom. Right

**[15:18]**
there. In. We're then going to press continue. Is actually encrypting those keys using AES 256 encrypted. So, they're never shown to Trading View and can only be decrypted if they had the password. Okay. So, this is where we set everything up. We're going to give our strategy a name. We have to say make a choice of whether we're going to be using this strategy on multiple charts or just BTCUSDT. So, I'm just going to leave it set by chart. What this means is if I move my chart over to Ethereum, I can use exactly the same alert without having to worry about how much margin. Then, we're going to set up our USDT margin and say that I'm going to be using $100 per trade and 7x leverage. Then, we have a couple of other advanced features. I'm not going to worry about that today. But then we're going to go over to next. We can then set our takerit and stop loss. So if your strategy has a takerit and stop loss, you can actually set that so it's already done in your exchange. I'm going to click no takeprofit and stop loss because this is a swing trading

**[16:19]**
strategy. So it'll be open and closed with these bots just here. Okay. Once that's done, that's going to give you this code here. But it may look a little bit scary, but you don't have to worry. We're just going to scroll down to the bottom and we're going to copy this code here. And then I'm going to go over to Claude. I've already pasted in the code that we got from Trading View earlier. And I'm going to ask it to add this code for me. Hey there, buddy. I'd love to autotrade this strategy down below. Could you add the alert wiring in for me so that I can auto trade it on my Bybit account? Now, I've got to be honest, guys. This would have been much easier if I would have used the trigger trade skill. The reason I did it all step by step was to show you exactly what happens in the background when Claude actually does it for you. Adding your API keys and secrets is always something a little bit scary. So I thought I'd go through every step with you. Now there's a couple of things that I would suggest always when using AI to trade. And number one being set up some sub

**[17:19]**
accounts. Sub accounts will help you to protect your capital whilst these bots are actually trading for you and limit your risk. Number two, I would either paper trade or use a small amount of capital when you are testing your bots at the beginning because live trading is a lot different from back testing. Talking of that, I will be giving you the number one big mistake in a couple of seconds after we've actually completed this step. And guys, before I leave you, I recently opened a school on school.com. You're more than welcome to come and join us. In the school, you'll be able to find everything that I've learned from AI trading and algo trading over the past 5 years. You get access to all of my strategies and the bots that I have built. You'll be able to find the link in the description or in the pinned comment. I really look forward to seeing you over there. Okay, amazing. So, now Claude has actually set up the alert so we can actually auto trade this thing, right? Okay, let's go back over to Trading View. Let's paste our script in here. And as you can see, there was no

**[18:20]**
changes to the back test. So, we are ready to roll. And our final step now is just to set up our web hook alert. So, we're going to click on the three dots beside our strategy just here. We are going to click on create an alert just like this. And as you can see, everything is pretty much already filled out. We are going to click on notifications and we're going to click on web hook URL. Then we're going to go back to trigger trade and we're going to copy this web hook URL just here. We're going to paste it in just there just like that. And that URL will connect trading view directly over to your exchange. We're going to press apply. We're going to make sure the expiration is openended because otherwise it will automatically turn itself off. Okay. And then we need to change the message. We will need to change the message to this little bit of code here which I'll also put in the pinned comment down below. It is strategy.order.alert message. What this simple message does

**[19:22]**
is connects trading view. Tells us exactly your stop losses and take profits and everything in one single message which is sent directly to exchange. We're going to give it a name. I'm going to call it test. And we're going to press apply and create. And boom. There you go. That is exactly how you set up your bot. Now, in the background, as soon as a new trade is popped off, it will automatically take a trade on your exchange. Now, guys, that was a stepbystep building profitable trading bots with Claude. And I'm just going to give you a couple of lessons that I've learned since the beginning of building strategies and building automated bots. Number one, always forward test your strategies. What this means is is when you back test a strategy, you are back testing it on historical data. 95% of strategies will fail once you put them into real markets. Best thing you can do is back test the strategy and then leave it for a couple of months. Come back to that strategy and see whether those results

**[20:23]**
look similar to what you're back testing results. If the case, then take it over to a paper trading or a small account to test on a live account. Number two would be diversification. Don't expect one bot to be the holy grail of all strategies. In my opinion, the best thing you can do is have multiple bots running on different coin pairs, different assets, different time frames using different strategies. This will diversify your portfolio a little bit better. But obviously guys, these are just things that I've learned as I've gone along. I am not a financial adviser and none of this is financial advice. So once again, thank you so much for joining me. I hope you managed to find some value from this video and now you'll be able to build your own bots, fish for yourself, not rely on somebody else building your strategies or even just giving you signals. Without further ado, guys, I'm going to wish you an absolutely wonderful day. Take care, keep safe, trade like boss, and I'll see you in the next one. Goodbye, guys. >> Come on, David. And once again, he's gone to a new strategy. He'll be back in

**[21:25]**
just 5 minutes. RSI and MACD. If it doesn't run into any bugs, there will be a new strategy.

## Similar videos (same channel / same strategy family) — candidates for cross-reference

Collected via web search 2026-07-09; the first block are Claude+TradingView
builds in the same series (channel attribution per search results, verify on
open); the second are same-author strategy references.

1. How To Build A Trading Strategy With Claude & Backtest On TradingView (DaviddTech, 2026-04-10) — https://www.youtube.com/watch?v=suaMYTxZIC4
2. I Let Claude Code 10,123 Profitable AI Trading Strategies – Results Are Insane (DaviddTech, 2026-05-18) — https://www.youtube.com/watch?v=3IgYhw5WqTY
3. I Gave Claude AI Full Access to 1500 TradingView Scalping Strategies… The Results Are Insane (DaviddTech, 2026-04-06) — https://www.youtube.com/watch?v=VD2TC8Ifl0w
4. I Gave Claude Full Access to TradingView – It Built a Profitable Strategy in Minutes — https://www.youtube.com/watch?v=h6qUy92Maco
5. I Built an AI Trading System With Claude + TradingView — https://www.youtube.com/watch?v=IqvnryFzZD4
6. Claude Code + TradingView = Advanced Trading Bot (Tutorial) — https://www.youtube.com/watch?v=8CHLrbTrnaw
7. Claude AI can NOW Automatically Build and Improve Your TradingView Strategies (while you sleep) — https://www.youtube.com/watch?v=77ikjQjdGFg
8. I Built A Trading Bot With Claude That Made $168,236 — https://www.youtube.com/watch?v=VDpTU5kdj8A
9. Triple Supertrend + Stoch RSI + 200 EMA by @DaviddTech (TradingView strategy script, same author, same indicator family) — https://in.tradingview.com/script/OI13Ltds-Triple-Supertrend-Stoch-RSI-200-EMA-by-DaviddTech/
10. 70% Win Rate MACD + Parabolic SAR + 200 EMA Trading Strategy (same author, Medium write-up) — https://daviddtech.medium.com/70-win-rate-highly-profitable-macd-parabolic-sar-200-ema-trading-strategy-8f49f8503aa

## Rules extraction — first pass

The video is primarily a **workflow/tooling tutorial** (Claude Code →
TradingKit/Trader Dev backtester → TradingView → Trigger.trade → Bybit), not a
rules-first strategy exposition. Two concrete strategies appear on screen; the
transcript states the following.

### Strategy A — dual-EMA demo (the optimizer walkthrough, ~5:05–8:10)

- Instrument/timeframe: BTCUSDT, 1-hour.
- Structure: exactly **two parameters** — a slow EMA and a fast EMA ("a
  trading strategy that has two moving averages").
- Optimization sweep: slow EMA length 110→400, fast EMA length 10→100
  (~500 grid cells; heat map scored on **profit factor**).
- Stated best: **slow EMA = 400, fast EMA = 45** → profit factor 1.86,
  net profit +281% (backtest window not stated).
- Entry/exit logic not stated explicitly — implied EMA cross (fast vs slow),
  direction (long-only vs long/short) not stated.

### Strategy B — "SuperTrend Flip EMA MACD" (the headline result, ~10:14–12:17)

- Instrument/timeframe: **BTCUSDT, 4-hour** ("the super trend flip EMA MACD on
  the 4hour on BTCUSDT").
- Produced by a 24-hour optimization loop (iterating every 15 minutes across
  candidate strategies, discarding failures), objective = **Sharpe ratio**.
- Stated results: Trader Dev backtest ≈ 500%+ net profit, 11% max drawdown,
  141 closed trades; TradingView re-test with broker fees added ≈ 500%+ net
  profit, 15% max drawdown, 141 closed trades, **profit factor 2.295**.
- Trade management: swing strategy, **no take-profit / no stop-loss** —
  positions opened and closed by strategy signals only (stated at ~15:18–16:19).
- Execution config shown: Bybit unified trading, $100 USDT margin per trade,
  7x leverage, per-chart alert scope, webhook alert message
  `strategy.order.alert_message` (TradingView placeholder), open-ended alert
  expiration.

### Ambiguities (blocking a single faithful implementation)

1. Strategy B's actual **indicator parameters are never stated**: SuperTrend
   ATR period/multiplier, EMA length(s), MACD fast/slow/signal — all unknown.
   The Pine Script is only shown as "the code at the bottom of the page" on
   Trader Dev; it is not readable from captions.
2. **Entry/exit ("flip") logic unstated** — plausibly SuperTrend direction flip
   gated by EMA trend filter and/or MACD confirmation, but which component
   triggers vs filters is not specified.
3. Long/short vs long-only: not stated for either strategy.
4. Backtest window, initial capital, commission value, and order sizing used
   in the TradingView verification: not stated (only that fees were "added").
5. Strategy A's cross semantics (close-of-bar cross? both directions?) not
   stated.
6. The +500%/PF 2.295 headline is an **in-sample optimized** figure (the
   author himself flags that 95% of strategies fail forward tests, 19:53+).

**Gen-2 resume path (per QUEUE):** treat each plausible resolution of the
ambiguities as its own faithful interpretation — e.g. (i) SuperTrend flip
entry + EMA filter + MACD confirm, (ii) MACD cross entry + SuperTrend/EMA
filters, (iii) plain dual-EMA 400/45 as Strategy A control — and run them as
competing systems against each other and buy-and-hold under the lab's
holdout/fee discipline (founding-plan discipline; no headline-chasing).
