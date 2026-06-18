# ✦ Pokémon World — Bot Discord

Um RPG completo de Pokémon dentro do Discord, com progressão, coleção, batalhas, economia, itens, missões e interface visual premium.

---

## 🚀 Instalação no Railway

### 1. Criar projeto no Railway
- Acesse [railway.app](https://railway.app)
- Crie um novo projeto
- Escolha "Deploy from GitHub repo" ou faça upload manual

### 2. Variáveis de Ambiente
No painel do Railway, vá em **Variables** e adicione:

| Variável | Valor | Descrição |
|----------|-------|-----------|
| `DISCORD_TOKEN` | `seu-token-aqui` | Token do bot Discord |

> **NÃO crie arquivo `.env` ou `.env.example`**. O Railway gerencia as variáveis via painel.

### 3. Deploy
- O Railway detecta automaticamente o `requirements.txt` e instala as dependências
- O bot inicia automaticamente via `bot.py`

---

## 📁 Estrutura do Projeto

```
pokemon-discord-bot/
├── bot.py              # Arquivo principal (bot + comandos + batalhas)
├── config.py           # Configurações, cores, emojis, dados do jogo
├── database.py         # SQLite — treinadores, Pokémon, inventário, missões
├── pokeapi.py          # Integração com PokéAPI (imagens, dados, sprites)
├── utils.py            # Utilitários visuais (barras, cálculos, formatação)
├── requirements.txt    # Dependências Python
└── data/
    └── pokemon_bot.db  # Banco de dados SQLite (criado automaticamente)
```

---

## 🎮 Comandos

| Comando | Descrição |
|---------|-----------|
| `/start` | Inicia sua jornada como treinador |
| `/profile` | Seu perfil de treinador |
| `/catch` | Capturar Pokémon selvagem |
| `/pokedex` | Ver seus Pokémon capturados |
| `/team` | Gerenciar time de batalha |
| `/battle` | Batalhar contra NPC |
| `/pvp` | Desafiar outro jogador |
| `/shop` | Loja de itens |
| `/inventory` | Seu inventário |
| `/daily` | Recompensa diária + missões |
| `/leaderboard` | Ranking de treinadores |
| `/gift` | Presentear amigos com moedas |
| `/trade` | Trocar Pokémon com outros |
| `/help` | Ajuda completa |

---

## ✨ Recursos

- **Visual Premium**: Embeds elegantes, botões interativos, select menus, modais
- **PokéAPI**: Imagens oficiais, dados reais dos Pokémon
- **Sistema de Treinador**: Nível, XP, rank, títulos, especialização
- **Sistema de Pokémon**: Raridades, natures, potencial, shiny, stats
- **Batalhas PvE e PvP**: Turnos, vantagem de tipo, críticos, esquivas
- **Economia**: Moedas, loja, caixas misteriosas, presentes
- **Missões**: Diárias, semanais, eventos especiais
- **Inventário**: Poké Balls, poções, cartas de melhoria, itens especiais
- **Anti-spam**: Cooldowns em capturas, batalhas e XP por mensagem

---

## 🛠 Tecnologias

- `discord.py` 2.4+ (slash commands, botões, modais)
- `aiosqlite` (banco de dados SQLite async)
- `aiohttp` (requisições à PokéAPI)
- `Pillow` (processamento de imagens)

---

## 📝 Licença

Projeto para uso pessoal/educacional. Pokémon é propriedade da Nintendo/Game Freak.

---

**Boa jornada, treinador!** ⚔
