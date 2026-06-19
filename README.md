# ✦ Pokémon World — Bot Discord — MUNDO VIVO RPG

Um RPG completo de Pokémon dentro do Discord, com mundo aberto, progressão, coleção, batalhas, economia, itens, missões, clima dinâmico, sistema de clãs, raids mundiais e interface visual premium.

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
├── bot.py              # Arquivo principal (bot + comandos + batalhas + mundo)
├── config.py           # Configurações, cores, emojis, dados do jogo, mundo de Elyndra
├── database.py         # SQLite — treinadores, Pokémon, inventário, missões, clãs, raids, ovos
├── pokeapi.py          # Integração com PokéAPI (imagens, dados, sprites)
├── utils.py            # Utilitários visuais (barras, cálculos, formatação, clima, amizade)
├── requirements.txt    # Dependências Python
└── data/
    └── pokemon_bot.db  # Banco de dados SQLite (criado automaticamente)
```

---

## 🗺️ Mundo de Elyndra

### Regiões
| Região | Emoji | Nível Mínimo | Clima |
|--------|-------|-------------|-------|
| **Verdália** | 🌿 | 1 | Temperado |
| **Frostvale** | ❄️ | 15 | Frio |
| **Maré Azul** | 🌊 | 25 | Tropical |
| **Vulkar** | 🔥 | 35 | Quente |
| **Drakoria** | 🐉 | 45 | Montanha |
| **Lumina** | 🏰 | 1 | Capital |

### Áreas por Região
- **Verdália**: Bosque Esmeralda, Árvore Ancestral, Caverna dos Cogumelos
- **Frostvale**: Lago Cristalino, Pico do Vento Branco, Ruínas Geladas
- **Maré Azul**: Ilha Coral, Gruta das Marés, Abismo Azul
- **Vulkar**: Vale das Cinzas, Cratera Escarlate, Mina de Obsidiana
- **Drakoria**: Ninho Celestial, Picos dos Anciões, Vale da Tempestade
- **Lumina**: Centro da Liga, Mercado Mundial, Arena dos Campeões, Biblioteca dos Lendários

---

## 🎮 Comandos

### Início e Perfil
| Comando | Descrição |
|---------|-----------|
| `/start` | Inicia sua jornada como treinador em Elyndra |
| `/profile` | Seu perfil de treinador com localização, insígnias, título |

### Mundo e Exploração
| Comando | Descrição |
|---------|-----------|
| `/world` | Visualiza o mapa de Elyndra |
| `/explore` | Explora a área atual com eventos dinâmicos |
| `/weather` | Ver clima atual e seus efeitos |

### Pokémon
| Comando | Descrição |
|---------|-----------|
| `/catch` | Capturar Pokémon selvagem na área atual |
| `/pokedex` | Ver seus Pokémon com amizade e personalidade |
| `/team` | Gerenciar time de batalha |
| `/friendship` | Interagir com Pokémon (alimentar, brincar, treinar) |
| `/evolve` | Evoluir Pokémon (em desenvolvimento) |

### Batalhas
| Comando | Descrição |
|---------|-----------|
| `/battle` | Batalhar contra NPC |
| `/battle_trainer` | Desafiar treinadores importantes de Elyndra |
| `/pvp` | Desafiar outro jogador |
| `/raid` | Participar de raid mundial |

### Economia
| Comando | Descrição |
|---------|-----------|
| `/shop` | Loja de itens com pedras evolutivas |
| `/inventory` | Seu inventário |
| `/daily` | Recompensa diária + missões |
| `/market` | Mercado de jogadores |

### Social
| Comando | Descrição |
|---------|-----------|
| `/leaderboard` | Ranking de treinadores |
| `/trade` | Trocar Pokémon com outros |
| `/gift` | Presentear amigos com moedas |
| `/clan` | Sistema de clãs |

### Sistema
| Comando | Descrição |
|---------|-----------|
| `/diary` | Diário de jornada |
| `/quests` | Missões ativas |
| `/help` | Ajuda completa |

### Admin
| Comando | Descrição |
|---------|-----------|
| `/admin_spawn_channel` | Define canal de spawns |
| `/admin_force_weather` | Força clima atual |
| `/admin_force_spawn` | Força spawn imediato |

---

## ✨ Recursos

- **🗺️ Mundo Vivo**: 6 regiões, 18 áreas exploráveis com eventos dinâmicos
- **🌦️ Clima Dinâmico**: Sol, chuva, tempestade, neve, névoa com efeitos em spawns
- **👤 Treinadores Importes**: Liora, Kael, Nerys, Volt, Ragnar, Aether com diálogos
- **🏅 Ginásios**: 6 ginásios com líderes e insígnias
- **📜 História**: 5 capítulos com requisitos e recompensas
- **💝 Amizade**: Sistema de amizade com níveis e bônus
- **🎭 Personalidade**: 8 personalidades diferentes para Pokémon
- **🥚 Ovos**: Sistema de incubação (4 tipos de ovos)
- **👥 Clãs**: Crie ou junte-se a clãs
- **🌋 Raids**: Bosses mundiais cooperativos
- **💹 Mercado**: Compre e venda itens entre jogadores
- **📓 Diário**: Registro automático de todas as aventuras
- **🌩 Spawns Automáticos**: Pokémon selvagens aparecem a cada 15 minutos
- **Visual Premium**: Embeds elegantes, botões interativos, select menus
- **PokéAPI**: Imagens oficiais, dados reais dos Pokémon
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
