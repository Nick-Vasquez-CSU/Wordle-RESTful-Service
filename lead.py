import dataclasses
import sqlite3
import textwrap
import databases
import toml
from quart import Quart, abort, g, request
from quart_schema import QuartSchema, validate_request


app = Quart(__name__)
QuartSchema(app)

app.config.from_file(f"./etc/{__name__}.toml", toml.load)

@dataclasses.dataclass
class Game:
    gameid: str

async def _connect_db():
    database = databases.Database(app.config["DATABASES"]["URL"])
    await database.connect()
    return database


def _get_db():
    if not hasattr(g, "sqlite_db"):
        g.sqlite_db = _connect_db()
    return g.sqlite_db


@app.teardown_appcontext
async def close_connection(exception):
    db = getattr(g, "_sqlite_db", None)
    if db is not None:
        await db.disconnect()

@app.route("/result", methods=["GET"])
@validate_request(Game)
async def getGameResult(data):
    auth = request.authorization
    if auth and auth.username and auth.password:
        db = await _get_db()
        currGame = dataclasses.asdict(data)
        games_val = await db.fetch_one("SELECT * FROM game WHERE gameid= :gameid", values={"gameid": gameid})
        if games_val is None or len(games_val) == 0:
            return {"Message": "Not a valid gameid"}, 406

        if games_val[2] == "In-progress":
            return {
                "Game Still in Progress": "true",
                "Guesses Made": games_val[1]
            }, 202
        else:
            if games_val[1] > 6:
                return {
                    "Game Status": "Lost",
                    "Guesses Made": games_val[1]
                }, 202
            else:
                return {
                    "Game Status": "Won",
                    "Guesses Made": games_val[1]
                }, 202
    else:
        return (
            {"error": "User not verified"},
            401,
            {"WWW-Authenticate": 'Basic realm = "Login required"'},
        )

@app.route("/topten", methods=["GET"])
async def getTopTen():
    return
