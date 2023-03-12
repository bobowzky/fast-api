import orjson
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, Field


class AnimeRecord(BaseModel):
    rank: int
    title: str
    year: str
    runtime: str
    rating: float
    url: str
    genres: set[str]

    @staticmethod
    def from_dict(data: dict):
        genres = set(data.pop('genres', []))
        record = AnimeRecord(genres=genres, **data)
        return record


class Problem(BaseModel):
    detail: str


class Database:
    def __init__(self):
        self._data: list = []

    def load_from_filename(self, filename: str):
        with open(filename, "rb") as f:
            data = orjson.loads(f.read())
            for record in data:
                obj = AnimeRecord.from_dict(record)
                self._data.append(obj)

    def delete(self, id_anime: int):
        if 0 < id_anime >= len(self._data):
            return
        self._data.pop(id_anime)

    def add(self, anime: AnimeRecord):
        self._data.append(anime)

    def get(self, id_anime: int):
        if 0 < id_anime >= len(self._data):
            return
        return self._data[id_anime]

    def get_all(self) -> list[AnimeRecord]:
        return self._data

    def update(self, id_anime: int, anime: AnimeRecord):
        if 0 < id_anime >= len(self._data):
            return
        self._data[id_anime] = anime

    def count(self) -> int:
        return len(self._data)


db = Database()
db.load_from_filename('anime.json')

app = FastAPI(title="AnimeList API", version="0.1", docs_url="/docs")

app.is_shutdown = False


@app.get("/animes", response_model=list[AnimeRecord], description="Vrátí seznam anime")
async def get_animes():
    return db.get_all()


@app.get("/animes/{id_anime}", response_model=AnimeRecord)
async def get_anime(id_anime: int):
    return db.get(id_anime)


@app.post("/animes", response_model=AnimeRecord, description="Přidáme anime do DB")
async def post_anime(anime: AnimeRecord):
    db.add(anime)
    return anime


@app.delete("/animes/{id_anime}", description="Odstraníme anime", responses={
    404: {'model': Problem}
})
async def delete_anime(id_anime: int):
    anime = db.get(id_anime)
    if anime is None:
        raise HTTPException(404, "Anime neexistuje")
    db.delete(id_anime)
    return {'status': 'smazano'}


@app.patch("/animes/{id_anime}", description="Aktualizujeme anime do DB", responses={
    404: {'model': Problem}
})
async def update_anime(id_anime: int, updated_anime: AnimeRecord):
    anime = db.get(id_anime)
    if anime is None:
        raise HTTPException(404, "Anime neexistuje")
    db.update(id_anime, updated_anime)
    return {'old': anime, 'new': updated_anime}