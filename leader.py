
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

redisClient.flushall()


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
        elif leaderboardData["result"] == "Loss":
            score = 0
        
        if redisClient.hget('leaderboard', 'username') == auth.username:
            score = int(redisClient.hget('leaderboard', 'score')) + score
            count = int(redisClient.hget('leaderboard', 'gamecount')) + count
            averageScore = score / count
        
            result = redisClient.hset('leaderboard', 'averageScore', averageScore)
            result = redisClient.hset('leaderboard', 'result',leaderboardData["result"])
            result = redisClient.hset('leaderboard', 'guesses',leaderboardData["guesses"])
            result = redisClient.hset('leaderboard', 'score', score)
            result = redisClient.hset('leaderboard', 'gamecount', count)

        else  :

            result = redisClient.hset('leaderboard', 'username' , auth.username)
            result = redisClient.hset('leaderboard', 'averageScore', score)
            result = redisClient.hset('leaderboard', 'result',leaderboardData["result"])
            result = redisClient.hset('leaderboard', 'guesses',leaderboardData["guesses"])
            result = redisClient.hset('leaderboard', 'score', score)
            result = redisClient.hset('leaderboard', 'gamecount', count)

        return redisClient.hgetall('leaderboard'), 200

    else:
        return (
            {"error": "User not verified"},
            401,
            {"WWW-Authenticate": 'Basic realm = "Login required"'},
        )


@app.route("/top-scores/", methods=["GET"])

async def topScores():


    leaderboardSet = "Leaderboard"


    topScores = redisClient.zrange(leaderboardSet, 0, 9, desc = True, withscores = True)


    if topScores != None:

        return ('\n'.join(map(str, topScores))), 200

    else:

        return {"Error": "Database empty."}, 404
