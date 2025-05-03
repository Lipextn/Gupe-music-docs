import discord
from discord.ext import commands
import youtube_dl
import os
from dotenv import load_dotenv

# Carrega variáveis do .env
load_dotenv()

bot = commands.Bot(command_prefix='!', intents=discord.Intents.all())

# Variáveis de controle
fila = []
musica_atual = None
pausado = False

@bot.event
async def on_ready():
    print(f'Bot conectado como {bot.user.name}')

async def tocar_musica(ctx):
    global fila, musica_atual, pausado
    
    if not fila or pausado:
        return
        
    voice_client = ctx.voice_client
    url = fila.pop(0)
    
    ydl_opts = {'format': 'bestaudio'}
    with youtube_dl.YoutubeDL(ydl_opts) as ydl:
        info = ydl.extract_info(url, download=False)
        musica_atual = info['title']
        voice_client.play(discord.FFmpegPCMAudio(info['formats'][0]['url']),
                        after=lambda e: bot.loop.create_task(tocar_musica(ctx)))
    
    await ctx.send(f"🎵 Tocando agora: **{musica_atual}**")

@bot.command()
async def play(ctx, *, url):
    global fila
    if not ctx.author.voice:
        return await ctx.send("Entre em um canal de voz primeiro!")
    
    voice_client = ctx.voice_client or await ctx.author.voice.channel.connect()
    fila.append(url)
    
    if not ctx.voice_client.is_playing():
        await tocar_musica(ctx)

@bot.command()
async def pause(ctx):
    global pausado
    if ctx.voice_client.is_playing():
        ctx.voice_client.pause()
        pausado = True
        await ctx.send("⏸ Música pausada")

@bot.command()
async def continue(ctx):
    global pausado
    if ctx.voice_client.is_paused():
        ctx.voice_client.resume()
        pausado = False
        await ctx.send("▶ Continuando música")

@bot.command()
async def stop(ctx):
    global fila, musica_atual
    fila.clear()
    ctx.voice_client.stop()
    musica_atual = None
    await ctx.send("⏹ Música parada e fila limpa")

@bot.command()
async def skip(ctx):
    ctx.voice_client.stop()
    await ctx.send("⏭ Música pulada")
    await tocar_musica(ctx)

@bot.command()
async def back(ctx):
    global fila
    if musica_atual:
        fila.insert(0, musica_atual)
        ctx.voice_client.stop()
        await ctx.send("⏮ Voltando para a música anterior")
        await tocar_musica(ctx)

@bot.command()
async def repeat(ctx):
    global fila
    if musica_atual:
        fila.insert(0, musica_atual)
        await ctx.send("🔂 Música será repetida")

@bot.command()
async def list(ctx):
    if not fila:
        return await ctx.send("🎵 Fila vazia")
    lista = "\n".join([f"{i+1}. {url}" for i, url in enumerate(fila[:10])])
    await ctx.send(f"🎶 **Fila de músicas:**\n{lista}")

@bot.command()
async def ajuda(ctx):
    ajuda_msg = """
    **🎧 Comandos do Bot:**
    `!play [link]` - Toca uma música do YouTube
    `!pause` - Pausa a música atual
    `!continue` - Continua a música pausada
    `!stop` - Para a música e limpa a fila
    `!skip` - Pula para a próxima música
    `!back` - Volta para a música anterior
    `!repeat` - Repete a música atual
    `!list` - Mostra as próximas músicas
    """
    await ctx.send(ajuda_msg)

# Lê o token do arquivo .env automaticamente
bot.run(os.getenv('DISCORD_TOKEN'))
