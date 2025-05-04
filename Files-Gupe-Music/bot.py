import discord
from discord.ext import commands
import yt_dlp as youtube_dl
import os
from dotenv import load_dotenv

# Carrega variáveis do .env
load_dotenv()
TOKEN = os.getenv('DISCORD_TOKEN')

# Inicializa o bot
intents = discord.Intents.all()
bot = commands.Bot(command_prefix='!', intents=intents)

# Variáveis globais
fila = []
musica_atual = None
pausado = False

# Configurações do yt_dlp
ydl_opts = {
    'format': 'bestaudio/best',
    'cookiefile': 'youtube.com_cookies.txt',
    'noplaylist': True,
    'quiet': True,
    'default_search': 'ytsearch',
    'extract_flat': False,
}

@bot.event
async def on_ready():
    print(f'✅ Bot conectado como {bot.user.name}')

async def tocar_musica(ctx):
    global fila, musica_atual, pausado

    if not fila or pausado:
        return

    voice_client = ctx.voice_client
    url = fila.pop(0)

    try:
        with youtube_dl.YoutubeDL(yt_opts) as ydl:
            info = ydl.extract_info(url, download=False)
            musica_url = info['url']
            musica_atual = info.get('title', 'Música desconhecida')

            # Corrige erro de conexão usando before_options
            source = discord.FFmpegPCMAudio(
                musica_url,
                before_options="-reconnect 1 -reconnect_streamed 1 -reconnect_delay_max 5",
                options="-vn"
            )
            voice_client.play(source, after=lambda e: bot.loop.create_task(tocar_musica(ctx)))

            await ctx.send(f"🎵 Tocando agora: **{musica_atual}**")
    except Exception as e:
        await ctx.send("❌ Erro ao tentar tocar a música.")
        print(f"[ERRO] Falha ao reproduzir: {e}")
        await tocar_musica(ctx)

@bot.command()
async def play(ctx, *, termo: str):
    global fila

    if not ctx.author.voice:
        return await ctx.send("⚠️ Você precisa estar em um canal de voz.")

    if not ctx.voice_client:
        await ctx.author.voice.channel.connect()

    # Verifica se é link direto do YouTube ou SoundCloud
    if "youtube.com" in termo or "youtu.be" in termo or "soundcloud.com" in termo:
        fila.append(termo)
    else:
        # Pesquisa no YouTube com ytsearch
        with youtube_dl.YoutubeDL(yt_opts) as ydl:
            try:
                info = ydl.extract_info(f"ytsearch:{termo}", download=False)['entries'][0]
                fila.append(info['webpage_url'])
            except Exception as e:
                print(f"[ERRO ao buscar no YouTube]: {e}")
                return await ctx.send("❌ Não consegui encontrar a música.")

    if not ctx.voice_client.is_playing() and not ctx.voice_client.is_paused():
        await tocar_musica(ctx)
    else:
        await ctx.send("🎶 Música adicionada à fila!")

@bot.command()
async def pause(ctx):
    global pausado
    if ctx.voice_client and ctx.voice_client.is_playing():
        ctx.voice_client.pause()
        pausado = True
        await ctx.send("⏸ Música pausada.")

@bot.command(name="continue")
async def continuar(ctx):
    global pausado
    if ctx.voice_client and ctx.voice_client.is_paused():
        ctx.voice_client.resume()
        pausado = False
        await ctx.send("▶ Música continuada.")

@bot.command()
async def stop(ctx):
    global fila, musica_atual
    if ctx.voice_client:
        fila.clear()
        ctx.voice_client.stop()
        musica_atual = None
        await ctx.send("⏹ Música parada e fila limpa.")

@bot.command()
async def skip(ctx):
    if ctx.voice_client:
        ctx.voice_client.stop()
        await ctx.send("⏭ Música pulada.")
        await tocar_musica(ctx)

@bot.command()
async def back(ctx):
    global fila
    if musica_atual:
        fila.insert(0, musica_atual)
        ctx.voice_client.stop()
        await ctx.send("⏮ Voltando para a música anterior.")
        await tocar_musica(ctx)

@bot.command()
async def repeat(ctx):
    global fila
    if musica_atual:
        fila.insert(0, musica_atual)
        await ctx.send("🔂 Música adicionada novamente para repetir.")

@bot.command()
async def list(ctx):
    if not fila:
        return await ctx.send("🎵 Fila de músicas vazia.")
    lista = "\n".join([f"{i+1}. {url}" for i, url in enumerate(fila[:10])])
    await ctx.send(f"🎶 **Fila atual:**\n{lista}")

@bot.command()
async def ajuda(ctx):
    ajuda_msg = """
    **🎧 Comandos do Bot de Música:**
    `!play [link ou nome]` - Toca uma música do YouTube ou SoundCloud
    `!pause` - Pausa a música
    `!continue` - Continua a música pausada
    `!stop` - Para tudo e limpa a fila
    `!skip` - Pula para a próxima música
    `!back` - Volta para a música anterior
    `!repeat` - Repete a música atual
    `!list` - Mostra as músicas da fila
    """
    await ctx.send(ajuda_msg)

bot.run(os.getenv('DISCORD_TOKEN'))
