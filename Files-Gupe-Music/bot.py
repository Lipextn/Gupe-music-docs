import discord
from discord.ext import commands
import yt_dlp
import os
from dotenv import load_dotenv

load_dotenv()

intents = discord.Intents.all()
bot = commands.Bot(command_prefix='!', intents=intents)

fila = []
musica_atual = None
pausado = False

@bot.event
async def on_ready():
    print(f'✅ Bot conectado como {bot.user.name}')

async def tocar_musica(ctx):
    global fila, musica_atual, pausado
    
    if not fila or pausado:
        return
    
    voice_client = ctx.voice_client
    url = fila.pop(0)

    ydl_opts = {
        'format': 'bestaudio/best',
        'noplaylist': True,
        'quiet': True,
        'default_search': 'ytsearch',
        'extract_flat': False,
    }

    try:
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(url, download=False)
            if 'entries' in info:
                info = info['entries'][0]
            musica_url = info['url']
            musica_atual = info.get('title', 'Música desconhecida')

        source = discord.FFmpegPCMAudio(musica_url, before_options='-reconnect 1 -reconnect_streamed 1 -reconnect_delay_max 5')
        voice_client.play(source, after=lambda e: bot.loop.create_task(tocar_musica(ctx)))
        await ctx.send(f"🎵 Tocando agora: **{musica_atual}**")

    except Exception as e:
        print("Erro ao tocar música:", e)
        await ctx.send("❌ Erro ao tentar tocar a música. Verifique o link ou tente novamente.")

@bot.command()
async def play(ctx, *, url):
    global fila
    if not ctx.author.voice:
        return await ctx.send("🚫 Você precisa estar em um canal de voz primeiro!")
    
    voice_client = ctx.voice_client or await ctx.author.voice.channel.connect()
    fila.append(url)

    if not voice_client.is_playing() and not voice_client.is_paused():
        await tocar_musica(ctx)

@bot.command()
async def pause(ctx):
    global pausado
    if ctx.voice_client and ctx.voice_client.is_playing():
        ctx.voice_client.pause()
        pausado = True
        await ctx.send("⏸ Música pausada")

@bot.command()
async def continue_(ctx):
    global pausado
    if ctx.voice_client and ctx.voice_client.is_paused():
        ctx.voice_client.resume()
        pausado = False
        await ctx.send("▶ Continuando música")

@bot.command()
async def stop(ctx):
    global fila, musica_atual
    if ctx.voice_client:
        fila.clear()
        ctx.voice_client.stop()
        musica_atual = None
        await ctx.send("⏹ Música parada e fila limpa")

@bot.command()
async def skip(ctx):
    if ctx.voice_client and ctx.voice_client.is_playing():
        ctx.voice_client.stop()
        await ctx.send("⏭ Música pulada")

@bot.command()
async def back(ctx):
    global fila
    if musica_atual:
        fila.insert(0, musica_atual)
        if ctx.voice_client:
            ctx.voice_client.stop()
            await ctx.send("⏮ Voltando para a música anterior")

@bot.command()
async def repeat(ctx):
    global fila
    if musica_atual:
        fila.insert(0, musica_atual)
        await ctx.send("🔂 Música será repetida")

@bot.command()
async def list(ctx):
    if not fila:
        return await ctx.send("📭 A fila está vazia.")
    lista = "\n".join([f"{i+1}. {url}" for i, url in enumerate(fila[:10])])
    await ctx.send(f"🎶 **Fila de músicas:**\n{lista}")

@bot.command()
async def ajuda(ctx):
    embed = discord.Embed(title="🎧 Comandos do Bot de Música", color=0x7289da)
    embed.add_field(name="!play [link ou nome]", value="Toca uma música do YouTube", inline=False)
    embed.add_field(name="!pause", value="Pausa a música atual", inline=False)
    embed.add_field(name="!continue", value="Continua a música pausada", inline=False)
    embed.add_field(name="!stop", value="Para a música e limpa a fila", inline=False)
    embed.add_field(name="!skip", value="Pula para a próxima música", inline=False)
    embed.add_field(name="!back", value="Volta para a música anterior", inline=False)
    embed.add_field(name="!repeat", value="Repete a música atual", inline=False)
    embed.add_field(name="!list", value="Mostra as próximas músicas da fila", inline=False)
    await ctx.send(embed=embed)

bot.run(os.getenv('DISCORD_TOKEN'))
