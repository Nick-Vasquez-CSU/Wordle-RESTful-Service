
import dataclasses

import redis


# Necessary quart imports

from quart import Quart, request

from quart_schema import QuartSchema, validate_request


app = Quart(__name__)

QuartSchema(app)


# Initialize redis client

redisClient = redis.Redis(host='localhost', port=6379, db=0, charset='utf-8', decode_responses=True)


# delete data from redisclient for testing

#redisClient.flushall()


@dataclasses.dataclass

class LeaderInfo:

    result: str

    guesses: int

# Results endpoint

@app.route("/results/", methods=["POST"])

@validate_request(LeaderInfo)

async def Results(data: LeaderInfo):

    auth = request.authorization

    if auth and auth.username and auth.password:

        leaderboardSet = "Leaderboard"

        leaderboardData = dataclasses.asdict(data)

        score = 0
        count = 1
        if leaderboardData["result"] == "Win":

            if leaderboardData["guesses"] == 1:
                score = 6
            if leaderboardData["guesses"] == 2:
                score = 5
            if leaderboardData["guesses"] == 3:
                score = 4
            if leaderboardData["guesses"] == 4:
                score = 3
            if leaderboardData["guesses"] == 5:
                score = 2
            if leaderboardData["guesses"] == 6:
                score = 1
        else:
            score = 0

        resultOne = redisClient.zrange(leaderboardSet, 0, -1, desc = True, withscores = True, score_cast_func=int)
        print("AUTH USERMAME: " + auth.username)

        if False:
            score = redisClient.hget(auth.username, 'score') + score
            count = redisClient.hget(auth.username, 'gamecount') + count
            averageScore = score / count
            result = redisClient.hset(auth.username, 'averageScore', averageScore)
            result = redisClient.hset(auth.username, 'result',leaderboardData["result"])
            result = redisClient.hset(auth.username, 'guesses',leaderboardData["guesses"])
            result = redisClient.hset(auth.username, 'score', score)
            result = redisClient.hset(auth.username, 'gamecount', count)

        else:
            result = redisClient.hset(auth.username, 'averageScore', score)
            result = redisClient.hset(auth.username, 'result',leaderboardData["result"])
            result = redisClient.hset(auth.username, 'guesses',leaderboardData["guesses"])
            result = redisClient.hset(auth.username, 'score', score)
            result = redisClient.hset(auth.username, 'gamecount', count)

        return redisClient.hgetall(auth.username), 200
        #result = redisClient.zadd(leaderboardData, {id: [auth.username,leaderboardData["result"],leaderboardData["guesses"], score]})

        if result == 0:

            return "Username exist -- Updating Score.\nGame Status-Score\n" + ('\n'.join(map(str, resultOne))), 200

        elif result != int:

            return {"Error:" "Something went wrong."}, 404

        else:

            return "Adding new username and score.\nGame Status-Score\n" + ('\n'.join(map(str, resultOne))), 200

    else:
        return (
            {"error": "User not verified"},
            401,
            {"WWW-Authenticate": 'Basic realm = "Login required"'},
        )


# top 10 scores endpoint

@app.route("/top-scores/", methods=["GET"])

async def topScores():


    leaderboardSet = "Leaderboard"


    topScores = redisClient.zrange(leaderboardSet, 0, 9, desc = True, withscores = True)


    if topScores != None:

        return ('\n'.join(map(str, topScores))), 200

    else:

        return {"Error": "Database empty."}, 404
