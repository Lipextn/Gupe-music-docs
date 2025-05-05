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
        with youtube_dl.YoutubeDL(ydl_opts) as ydl:
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

# ... (todo o seu código acima continua inalterado)
import random
import discord
from discord.ext import commands

bot = commands.Bot(command_prefix='!')

# ------------------ PIADAS ------------------
piadas_usadas = set()

introducoes = [  # 50 introduções
    "🤣 Essa aqui é pra fazer o abdômen doer de tanto rir!",
    "😆 Quem rir por último é mais lerdinho, hein?",
    "😂 Aguenta o fôlego, essa vem pesada!",
    "😜 Lá vem uma pérola do humor!",
    "😹 Essa até minha avó contou e ainda é boa!",
    "🎭 Prepare-se para o show de piadas!",
    "💣 Cuidado: essa vai explodir de tanto rir!",
    "🥴 Essa é nível tiozão no churrasco!",
    "🌪️ Vai te derrubar de tanto rir!",
    "🧠 Rir também é exercício mental!",
    "🎉 O circo chegou, e essa é a atração principal!",
    "😬 Tenta não engasgar de rir com essa!",
    "🔥 Piada quentinha saindo do forno!",
    "📢 Alerta de risada vindo aí!",
    "🙃 Essa é tão boa que parece ruim (ou o contrário!)",
    "🕺 Dá até vontade de dançar de tão boa!",
    "😮 Lá vem bomba de humor!",
    "💥 Prepare-se para um ataque de risos!",
    "🤡 Palhaço aqui é só o começo!",
    "🎙️ O stand-up começou, atenção!",
    "⛔ Proibido não rir dessa!",
    "🧻 Vai precisar de papel, porque essa faz chorar de rir!",
    "📺 Essa é digna de programa de comédia!",
    "🕹️ Aperte START nas risadas!",
    "🔊 Aumenta o volume e ouve essa!",
    "🥳 Humor 100% aprovado pela zoeira!",
    "🧂 Um salzinho a mais de humor nessa aqui!",
    "👴 Essa é estilo piada de pai... mas boa!",
    "🥵 Cuidado, essa é quente!",
    "📦 Humor embalado e pronto pra rir!",
    "🚨 Atenção: piada de impacto chegando!",
    "😅 Vamos ver se você consegue segurar essa!",
    "💃 Vem dançar no ritmo da risada!",
    "😏 Essa é tão ruim que dá a volta e fica boa!",
    "🍿 Prepara a pipoca e curte essa!",
    "📚 Essa piada já tá nos livros de história!",
    "😎 Nível mestre da comédia desbloqueado!",
    "🎩 Piada fina, com classe e zoeira!",
    "🐸 Ria ou será transformado em um sapo!",
    "🏆 Essa merece um Oscar do humor!",
    "🛑 Pausa o que estiver fazendo e presta atenção!",
    "🧨 Humor explosivo ativado!",
    "🐔 Nem a galinha botava um ovo tão bom!",
    "🎬 Piada digna de Hollywood (ou quase)!",
    "👻 Fantasmas riram dessa e sumiram!",
    "🪑 Senta aí, porque essa vai te derrubar!",
    "🧃 Beba água antes, vai que engasga!",
    "📸 Momento para registrar sua reação!",
    "🚀 Rumo à estratosfera do riso!",
    "🛸 Essa piada foi abduzida de tão boa!",
    "💡 Riso garantido ou sua sanidade de volta!",
]

piadas = [
    "📖 Por que o livro foi ao médico? Porque ele tinha muitas páginas viradas!",
    "🦓 Qual é o animal mais antigo? A zebra, porque é em preto e branco!",
    "🐊 Por que o jacaré tirou o filho da escola? Porque ele réptil de ano!",
    "🔌 Como o eletricista chama o irmão dele? Manômetro!",
    "0️⃣ ➡️ 8️⃣ O que o zero disse para o oito? Que cinto legal!",
    "📖 Por que o livro foi ao médico? Porque ele tinha muitas páginas viradas!",
    "🦓 Qual é o animal mais antigo? A zebra, porque é em preto e branco!",
    "🐊 Por que o jacaré tirou o filho da escola? Porque ele réptil de ano!",
    "🔌 Como o eletricista chama o irmão dele? Manômetro!",
    "0️⃣ ➡️ 8️⃣ O que o zero disse para o oito? Que cinto legal!",
    "🚫⚡ Qual o contrário de volátil? Vem cá sobrinho!",
    "💻 Por que o computador foi ao médico? Porque estava com um vírus!",
    "🐂 Como se chama um boi que não vale nada? Boisofia!",
    "🍅 O que o tomate disse para o outro? Se não fosse por você, eu não passava de um extrato!",
    "🚀🐄 Por que a vaca foi para o espaço? Para visitar a Via Láctea!",
    "⛪🎤 O que o pagodeiro foi fazer na igreja? Cantar pá God!",
    "🐴📞 O que o cavalo foi fazer no orelhão? Passar um trote!",
    "🛞 Por que o pneu foi demitido? Porque estava sempre cansado!",
    "🌊📬 Como o mar se comunica? Ele manda alga-mail!",
    "🐟📚 Qual é o peixe mais inteligente? O atum, porque está sempre em grupo escolar!",
    "🎨🐱 Como se chama um gato pintor? Claude Miáu-net!",
    "🌳📱 Por que a árvore não usa Facebook? Porque ela já tem muitos galhos!",
    "🖨️📝 O que a impressora falou para o papel? Estou sentindo sua falta!",
    "🔨🐴 Como se chama o irmão mais novo do Thor? Thorzinho!",
    "🐰🚸 Por que o coelho atravessou a rua? Pra mostrar que ele também tem coragem!",
    "🎧🐮 Como se chama uma vaca com um fone de ouvido? Qualquer nome, ela não vai ouvir!",
    "🍌🩺 Por que a banana foi ao médico? Porque ela não estava se descascando bem!",
    "🧱🧼 O que o chão falou para o tapete? Coberto de razão!",
    "🏋️‍♂️ Qual é o cúmulo da força? Dobrar uma esquina!",
    "☕❤️ Como o café mostrou seu amor? Com uma declaração espresso!",
    "🐟🏢 Qual o nome do peixe que caiu do 10º andar? Aaaaaaaatum!",
    "👮‍♂️💻 Por que o notebook foi preso? Porque cometeu um cybercrime.",
    "🧼🧻 O que o sabonete disse para a toalha? Você me seca!",
    "🚪🗣️ Por que a parede não vai pra escola? Porque já tem muitos quadros.",
    "🧠🧵 O que o dente falou para o fio dental? Nossa relação é muito profunda!",
    "🐷🎮 Qual o jogo favorito do porquinho? O Bacon Royale!",
    "🐝🪲 Qual o inseto que vai pra academia? A abdomestra!",
    "🌵🫂 Por que o cacto não briga? Porque ele é espinhoso demais!",
    "🎷🐱 Como se chama um gato que toca jazz? Meownie Louis Armstrong!",
    "🍕💔 Por que a pizza terminou o namoro? Porque se sentia usada!",
    "🧀❤️ O que o queijo disse pro requeijão? Você me derrete!",
    "💡🧠 Qual a fórmula do humor? HAhAhA!",
    "📞🐠 Como o peixe atende o telefone? Diga, alô-lisco!",
    "📺😵‍💫 Por que a TV foi ao terapeuta? Muitos canais!",
    "🧻😢 Vai precisar de papel com essa de tanto rir!",
    "🎩😂 Piada de classe com zoeira de raiz!",
    "🐓💣 Galinha contou essa e explodiu de rir!",
    "🎤😜 O stand-up começou, senta que lá vem piada!",
    "👻🪞 O que o espelho falou pro fantasma? Te vejo por dentro!",
    "💃🤣 Dança da risada liberada com essa!",
    "🎮🐸 O que o sapo joga online? Croak of Duty!",
    "👽😄 Essa piada foi abduzida de tão boa!",
    "🏠🐘 Qual o animal que pula mais alto que uma casa? Todos, casas não pulam!",
    "🧃😄 Toma um gole e segura essa risada!",
    "🎢🤣 Essa piada é uma montanha-russa de humor!",
    "🚦😂 Parou tudo: hora da piada do dia!",
    "🎯🤣 Acertei bem no seu ponto fraco — o riso!",
    "📅🐝 Qual o inseto que organiza tudo? A planejamel!",
    "🎁😂 Presente do dia: uma piada épica!",
    "🗿😆 Piada milenar desbloqueada!",
    "🌈🎭 Essa é arte com tinta de zoeira!",
    "🎵😂 Essa é música pros seus ouvidos (se gostar de piada ruim kkk)",
]

@bot.command()
async def piada(ctx):
    global piadas_usadas

    if len(piadas_usadas) == len(piadas):
        piadas_usadas.clear()

    while True:
        index = random.randint(0, len(piadas) - 1)
        if index not in piadas_usadas:
            piadas_usadas.add(index)
            break

    piada = piadas[index]
    intro = random.choice(introducoes)

    await ctx.send(f"{intro}\n\n{piada}")

# ------------------ JOGAR ------------------

@bot.command()
async def jogar(ctx):
    opcoes = [
        f"🎲 Você tirou **{random.randint(1, 6)}** no dado!",
        f"🪙 Deu **{'cara' if random.choice([True, False]) else 'coroa'}**!",
        f"🎯 Seu número da sorte é: **{random.randint(1, 100)}**",
        f"🧠 Pensei em um número... adivinha? **{random.randint(1, 10)}**",
        f"🕹️ Você ganhou: **{random.choice(['um bônus imaginário', 'um abraço virtual', 'uma risada grátis', 'nada 😅'])}**",
    ]
    await ctx.send(random.choice(opcoes))

# ------------------ IMAGEM ------------------

@bot.command()
async def imagem(ctx):
    imagens = [
        "https://i.imgur.com/2YkF4jF.jpeg",  # cachorro engraçado
        "https://i.imgur.com/zvWTUVu.jpeg",  # gato assustado
        "https://i.imgur.com/Xu7Z5bL.jpeg",  # banana ninja
        "https://i.imgur.com/lKJiT77.jpeg",  # bebê rindo
        "https://i.imgur.com/4M34hi2.jpeg",  # meme random
    ]
    await ctx.send(f"🖼️ Aqui está uma imagem gerada especialmente para você!\n{random.choice(imagens)}")

# ------------------ ZOA ------------------

@bot.command()
async def zoa(ctx):
    zoeiras = [
        f"😆 {ctx.author.mention} tem Wi-Fi tão lento que até o Pombo Correio ganha!",
        f"😂 {ctx.author.mention} acha que 1GB de RAM é muito!",
        f"😜 {ctx.author.mention} clicou pra abrir o Google e abriu o Word!",
        f"🤪 {ctx.author.mention} é o tipo que procura 'como desligar o PC' no Google!",
        f"🤣 {ctx.author.mention} é tão atrasado que achou que o Windows XP é novidade!",
        f"😏 {ctx.author.mention} é tão gamer que joga Campo Minado em 4K!",
    ]
    await ctx.send(random.choice(zoeiras))

# --------- EVENTO DE INICIALIZAÇÃO OPCIONAL ---------

@bot.event
async def on_ready():
    print(f"🤖 Bot online como {bot.user}")


@bot.command()
async def ping(ctx):
    await ctx.send("🏓 Pong!")

@bot.command()
async def gpt(ctx, *, pergunta):
    ...

bot.run(os.getenv('DISCORD_TOKEN'))

# ADIÇÕES ABAIXO: ----------------------------

import openai  # biblioteca da OpenAI

# Carrega a chave da API do ChatGPT
openai.api_key = os.getenv("OPENAI_API_KEY")

# Comando !ping
@bot.command()
async def ping(ctx):
    latencia = round(bot.latency * 1000)
    await ctx.send(f"🏓 Pong! Latência: {latencia}ms")

# Comando !gpt
@bot.command()
async def gpt(ctx, *, pergunta):
    await ctx.send("🤖 Pensando...")
    try:
        resposta = openai.ChatCompletion.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "system", "content": "Você é um assistente útil no Discord."},
                {"role": "user", "content": pergunta}
            ],
            max_tokens=150,
            temperature=0.7
        )
        conteudo = resposta.choices[0].message.content.strip()
        await ctx.send(f"💬 {conteudo}")
    except Exception as e:
        await ctx.send("⚠️ Ocorreu um erro ao consultar o ChatGPT.")
        print(f"[GPT ERRO] {e}")

