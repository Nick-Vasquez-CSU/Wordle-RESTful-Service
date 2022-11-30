import dataclasses
import sqlite3
import textwrap
import databases
import toml
from quart import Quart, abort, g, request
from quart_schema import QuartSchema, validate_request
import redis

app = Quart(__name__)
QuartSchema(app)

#app.config.from_file(f"./etc/{__name__}.toml", toml.load)

redisClient = redis.Redis(host='localhost', port=6379, db=0)

@dataclasses.dataclass
class GameInfo:
    username: str
    gameid: str
    guesses: int
"""
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
"""

@app.route("/result", methods=["POST"])
@validate_request(GameInfo)
async def postGameResult(data):
    auth = request.authorization
    if auth and auth.username and auth.password:
        leaderboardGroup = "Wordle Leaderboard"
        leaderboardData = dataclasses.asdict(data)


        result = redisClient.zadd(leaderboardGroup, {leaderboardData["username"]: leaderboardData["guesses"]})
        print("Result: ", result)
        echoResult = redisClient.zrange(leaderboardGroup, 0, -1, desc = True, withscores = True)
        print("Echoed Result: ", echoResult)

        return {"Uploading Game": str(echoResult)}, 200

    else:
        return (
            {"error": "User not verified"},
            401,
            {"WWW-Authenticate": 'Basic realm = "Login required"'},
        )

@app.route("/topten", methods=["GET"])
async def getTopTen():
    return (
        {"error": "User not verified"},
        401,
        {"WWW-Authenticate": 'Basic realm = "Login required"'},
    )
