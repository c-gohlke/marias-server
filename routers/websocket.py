from fastapi import (
    APIRouter,
    WebSocket,
    WebSocketDisconnect,
)
from connection_manager import ConnectionManager
from game.game_setup import Game
from logger import logger
from db.login import fake_decode_token
import json

MAX_GAMES = 100
TAG = "websocket"

manager = ConnectionManager()
router = APIRouter()


@router.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    await websocket.accept()
    try:
        while True:
            data = await websocket.receive_text()

            logger.info("data is " + data)

            data_obj = json.loads(data)
            msg_type = str(data_obj["type"])
            username = fake_decode_token(data_obj["access_token"])

            logger.info("data_obj send_type is " + msg_type)

            # username is not in database, continue as guest with
            # username = accesstoken
            if(not username):
                username = data_obj["access_token"]

            logger.info(
                TAG + f"\nreceived from: {username} \nreceived data: {data}")

            if(msg_type == "connect"):
                await manager.connect(websocket, username)
            elif(msg_type == "disconnect"):
                username = fake_decode_token(data_obj[
                    "disconnected_access_token"
                    ])
                if(username):
                    manager.disconnect(username)
                else:
                    logger.info(TAG + "user was never connected")
            elif(msg_type == "prompt_game_ids"):
                await manager.send_data("game_ids", None, username)
            elif(msg_type == "start_game"):
                await manager.games[
                    int(data_obj["game_id"])
                                    ].start_game()
            elif(msg_type == "add_bot"):
                logger.info(TAG + "adding a bot")
                await manager.games[int(data_obj["game_id"])].join(None)
            elif(msg_type == "send_play"):
                game_id = manager.user_game[username]
                if(manager.games[game_id] is not None and manager.games[
                        game_id].wait_for == username):
                    if manager.games[game_id].wait_reason == "trump_choice":
                        await manager.games[
                            game_id
                                            ].receive_trump_card_choice(
                            int(data_obj["play"])
                            )
                        await manager.games[game_id].show_hand(username)
                    elif manager.games[game_id].wait_reason == "talon_choice1":
                        await manager.games[game_id].receive_talon_choice1(
                            int(data_obj["play"])
                            )
                        await manager.games[game_id].show_hand(username)
                    elif manager.games[game_id].wait_reason == "talon_choice2":
                        await manager.games[game_id].receive_talon_choice2(
                            int(data_obj["play"])
                            )
                        await manager.games[game_id].show_hand(username)
                    elif manager.games[game_id].wait_reason == "receive_play1":
                        await manager.games[game_id].receive_play1(
                            int(data_obj["play"]))
                        await manager.games[game_id].show_hand(username)
                    elif manager.games[game_id].wait_reason == "receive_play2":
                        await manager.games[game_id].receive_play2(
                            int(data_obj["play"]))
                        await manager.games[game_id].show_hand(username)
                    elif manager.games[game_id].wait_reason == "receive_play3":
                        await manager.games[game_id].receive_play3(
                            int(data_obj["play"]))
                        await manager.games[game_id].show_hand(username)
                    elif manager.games[
                            game_id
                            ].wait_reason == "waiting to join":
                        break
                    else:
                        logger.error("reason not matched")
                else:
                    logger.info("game not expecting response from this player")
            elif msg_type == "create game":
                if username in manager.user_game.keys():
                    logger.error(
                        TAG + "mulitple games for same user not supported")
                else:
                    game = Game(manager)
                    for i in range(MAX_GAMES):
                        if i not in manager.games.keys():
                            game.game_id = i
                            break
                    manager.games[game.game_id] = game
                    await manager.join_game(username, game.game_id)
                    await manager.send_data("CreatedGameID",
                                            game.game_id,
                                            username)
                    logger.info(
                        TAG + f"Game created with id {game.game_id}")
            elif msg_type == "join":
                await manager.join_game(username, int(data_obj["game_id"]))
            elif msg_type == "reconnect":
                if username in manager.user_game.keys():
                    game_id = manager.user_game[username]
                    await manager.games[game_id].reconnect(username)
                else:
                    await manager.send_data(
                        "error",
                        {"error_message": "User never connected"},
                        username
                        )
            elif msg_type == "leave_game":
                game_id = manager.user_game[username]
                manager.games[game_id].leave_game(username)
                del manager.user_game[username]
            else:
                logger.info("received input type incorrect")

    except WebSocketDisconnect:
        logger.info(TAG + "websocket disconnected")
