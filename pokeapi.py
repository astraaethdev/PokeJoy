"""
Integração com PokéAPI para obter dados e imagens dos Pokémon
"""
import aiohttp
import random
import asyncio
from config import POKEAPI_BASE, POKEAPI_OFFICIAL, MOVES_BY_TYPE, NATURES

class PokeAPI:
    def __init__(self):
        self.session = None
        self._cache = {}
        self._pokemon_list = None

    async def _get_session(self):
        if self.session is None or self.session.closed:
            self.session = aiohttp.ClientSession()
        return self.session

    async def fetch(self, url):
        """Faz requisição com cache"""
        if url in self._cache:
            return self._cache[url]

        session = await self._get_session()
        try:
            async with session.get(url, timeout=aiohttp.ClientTimeout(total=10)) as response:
                if response.status == 200:
                    data = await response.json()
                    self._cache[url] = data
                    return data
                return None
        except Exception:
            return None

    async def get_pokemon_list(self, limit=151):
        """Obtém lista de Pokémon"""
        if self._pokemon_list is not None:
            return self._pokemon_list[:limit]

        data = await self.fetch(f"{POKEAPI_BASE}/pokemon?limit=1000")
        if data:
            self._pokemon_list = data["results"]
            return self._pokemon_list[:limit]
        return []

    async def get_pokemon_data(self, identifier):
        """Obtém dados completos de um Pokémon"""
        data = await self.fetch(f"{POKEAPI_BASE}/pokemon/{identifier}")
        if not data:
            return None

        species_data = await self.fetch(f"{POKEAPI_BASE}/pokemon-species/{identifier}")

        # Extrair tipos
        types = [t["type"]["name"] for t in data.get("types", [])]

        # Extrair stats
        stats = {s["stat"]["name"]: s["base_stat"] for s in data.get("stats", [])}

        # Extrair moves
        moves = []
        for move in data.get("moves", [])[:4]:
            moves.append(move["move"]["name"].replace("-", " ").title())

        # Se não tiver moves, usar defaults do tipo
        if not moves and types:
            moves = random.sample(MOVES_BY_TYPE.get(types[0], ["Tackle"]), min(4, len(MOVES_BY_TYPE.get(types[0], ["Tackle"]))))

        # Descrição em inglês
        description = "Um Pokémon misterioso."
        if species_data and "flavor_text_entries" in species_data:
            for entry in species_data["flavor_text_entries"]:
                if entry.get("language", {}).get("name") == "en":
                    description = entry["flavor_text"].replace("\n", " ").replace("\f", " ")
                    break

        return {
            "pokedex_number": data["id"],
            "name": data["name"].capitalize(),
            "types": types,
            "hp": stats.get("hp", 50),
            "attack": stats.get("attack", 50),
            "defense": stats.get("defense", 50),
            "speed": stats.get("speed", 50),
            "moves": moves,
            "height": data.get("height", 0) / 10,
            "weight": data.get("weight", 0) / 10,
            "description": description,
            "sprite_url": f"{POKEAPI_OFFICIAL}/{data['id']}.png",
            "shiny_sprite_url": f"{POKEAPI_OFFICIAL}/shiny/{data['id']}.png",
        }

    async def get_random_pokemon(self, max_id=151, rarity_weights=None):
        """Obtém um Pokémon aleatório com raridade"""
        if rarity_weights is None:
            rarity_weights = {
                "comum": 0.60,
                "raro": 0.25,
                "epico": 0.10,
                "lendario": 0.04,
                "mitico": 0.01,
            }

        # Lendários e míticos têm IDs específicos
        legendary_ids = [144, 145, 146, 150, 151, 243, 244, 245, 249, 250, 377, 378, 379, 380, 381, 382, 383, 384, 385, 386]
        mythical_ids = [151, 251, 385, 386, 494, 647, 648, 649, 719, 720, 721, 801, 802, 807, 808, 809]

        rarity = random.choices(
            list(rarity_weights.keys()),
            weights=list(rarity_weights.values())
        )[0]

        if rarity == "lendario":
            pokemon_id = random.choice(legendary_ids)
        elif rarity == "mitico":
            pokemon_id = random.choice(mythical_ids)
        else:
            pokemon_id = random.randint(1, max_id)

        data = await self.get_pokemon_data(pokemon_id)
        if data:
            data["rarity"] = rarity
            data["is_shiny"] = random.random() < 0.004096
        return data

    async def get_pokemon_by_name(self, name):
        """Obtém Pokémon pelo nome"""
        return await self.get_pokemon_data(name.lower())

    async def get_evolution_chain(self, pokemon_id):
        """Obtém cadeia de evolução"""
        species = await self.fetch(f"{POKEAPI_BASE}/pokemon-species/{pokemon_id}")
        if not species or not species.get("evolution_chain"):
            return None

        chain_url = species["evolution_chain"]["url"]
        chain_data = await self.fetch(chain_url)
        return chain_data

    async def get_type_data(self, type_name):
        """Obtém dados de um tipo"""
        return await self.fetch(f"{POKEAPI_BASE}/type/{type_name}")

    async def close(self):
        if self.session and not self.session.closed:
            await self.session.close()

# Instância global
pokeapi = PokeAPI()
