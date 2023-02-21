from dataclasses import dataclass, asdict
import json
from multiprocessing import Pool
import sqlite3
import string
import requests

API_ENDPOINT = string.Template("https://xkcd.com/${chunk}info.0.json")
NUM_WORKERS = 100


@dataclass
class ComicMetadata:
    num: int

    day: str
    month: str
    year: str

    title: str
    safe_title: str
    alt: str
    news: str
    transcript: str
    link: str
    img: str

    extra_parts: str = None


def fetch_metadata(url):
    response = requests.get(url)

    if response.status_code == 200:
        return ComicMetadata(**json.loads(response.text))
    else:
        raise RuntimeError(
            f"Error fetching/parsing data. Status code was: {response.status_code}"
        )


def fetch_all_metadata():
    latest_comic = fetch_metadata(API_ENDPOINT.substitute(chunk=""))
    latest_comic_index = latest_comic.num
    comics_to_fetch = range(1, latest_comic_index + 1)

    with Pool(NUM_WORKERS) as p:
        all_metadata = p.map(
            fetch_metadata,
            (
                API_ENDPOINT.substitute(chunk=f"{index}/")
                for index in comics_to_fetch
                if index != 404
            ),
        )

    return all_metadata


def init_db(db_name="xkcd_metadata.db"):
    db = sqlite3.connect(db_name)

    with db:
        db.execute(
            """CREATE TABLE IF NOT EXISTS xkcd (
                    num INTEGER PRIMARY KEY,
                    title TEXT,
                    alt TEXT,
                    transcript TEXT,
                    img TEXT
                );
            """
        )


def main():
    # all_metadata = fetch_all_metadata()
    init_db()


if __name__ == "__main__":
    main()
