import discord
from discord.ext import commands, tasks
from dotenv import load_dotenv
from datetime import date
import os

from config import EPIC_IDS, CHANNEL_ID, PREFIX
from fetch import fetch_events
from format import format_event_results

load_dotenv()

TOKEN = os.getenv("DISCORD_TOKEN")
if not TOKEN:
    raise RuntimeError("DISCORD_TOKEN が設定されていません。")

intents = discord.Intents.default()
intents.message_content = True

bot = commands.Bot(command_prefix=PREFIX, intents=intents)


def _collect_today(target_date: date | None = None) -> list[tuple[str, list[dict] | None]]:
    """今日（または指定日）の大会データを全プレイヤー分取得"""
    result = []
    for epic_id in EPIC_IDS:
        events = fetch_events(epic_id, target_date=target_date)
        result.append((epic_id, events))
    return result


@bot.event
async def on_ready():
    print(f"✅ ログイン成功: {bot.user} (ID: {bot.user.id})")
    print(f"   監視対象: {', '.join(EPIC_IDS)}")
    print(f"   通知チャンネルID: {CHANNEL_ID}")
    daily_update.start()


@tasks.loop(hours=24)
async def daily_update():
    """毎日1回、その日の大会成績を送信"""
    channel = bot.get_channel(CHANNEL_ID)
    if not channel:
        print(f"⚠️ チャンネルID {CHANNEL_ID} が見つかりません")
        return

    today = date.today()
    players_data = _collect_today(target_date=today)
    messages = format_event_results(players_data, report_date=today)

    if not messages:
        print(f"[{today}] 今日の大会データなし。送信スキップ。")
        return

    date_str = today.strftime("%Y/%m/%d")
    await channel.send(f"📊 **AMORIS 大会成績レポート** — {date_str}")
    for msg in messages:
        await channel.send(msg)


@bot.command(name="today")
async def today_cmd(ctx):
    """今日の大会成績を表示"""
    today = date.today()
    await ctx.send(f"🔍 {today.strftime('%Y/%m/%d')} の大会データ取得中...")
    players_data = _collect_today(target_date=today)
    messages = format_event_results(players_data, report_date=today)

    if not messages:
        await ctx.send("今日の大会データが見つかりませんでした。")
        return
    for msg in messages:
        await ctx.send(msg)


@bot.command(name="latest")
async def latest_cmd(ctx):
    """最新の大会成績（最も最近の日付）を表示"""
    await ctx.send("🔍 最新の大会データ取得中...")
    players_data = _collect_today(target_date=None)  # 最新日を自動選択
    messages = format_event_results(players_data)

    if not messages:
        await ctx.send("データが取得できませんでした。")
        return
    for msg in messages:
        await ctx.send(msg)


@bot.command(name="player")
async def player_cmd(ctx, *, epic_id: str):
    """特定のプレイヤーの最新大会成績を表示。例: !player Ninja"""
    await ctx.send(f"🔍 `{epic_id}` の最新データ取得中...")
    events = fetch_events(epic_id, target_date=None)
    if not events:
        await ctx.send(f"❌ `{epic_id}` のデータが見つかりませんでした。")
        return
    players_data = [(epic_id, events)]
    messages = format_event_results(players_data)
    for msg in messages:
        await ctx.send(msg)


@bot.command(name="help_ft")
async def help_ft(ctx):
    """コマンド一覧を表示"""
    embed = discord.Embed(title="🎮 AMORIS Fortnite Tracker", color=0x00d4ff)
    embed.add_field(name="!today", value="今日の大会成績を表示", inline=False)
    embed.add_field(name="!latest", value="最新の大会成績（最近の日付）を表示", inline=False)
    embed.add_field(name="!player <名前>", value="任意のプレイヤーの最新成績を検索", inline=False)
    embed.add_field(name="!help_ft", value="このヘルプを表示", inline=False)
    embed.set_footer(text="毎日0時に自動更新 ・ 当日の大会のみ表示")
    await ctx.send(embed=embed)


bot.run(TOKEN)
