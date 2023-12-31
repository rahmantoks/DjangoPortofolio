import json
import random
from channels.generic.websocket import AsyncWebsocketConsumer
from asgiref.sync import async_to_sync
from snake.const import *

import asyncio

ROOM = {"perkenyi","public"}
GRID_SIZE = 20
CANVAS_HEIGHT = 600
CANVAS_WIDTH = 800
HEIGHT = CANVAS_HEIGHT/GRID_SIZE - 1
WIDTH = CANVAS_WIDTH/GRID_SIZE - 1

class SnakeConsumer(AsyncWebsocketConsumer):
    games = {}  # Dictionary to store game state
    game_loop_task = None  # Keep track of the game loop taskames = {}

    async def connect(self):
        await self.accept()

    async def init(self):
        self.room_group_name = f"snake_game_{self.room_name}"
        # Add the user to the room's group
        await self.channel_layer.group_add(
            self.room_group_name,
            self.channel_name
        )

        # Check if the game session already exists
        if self.room_name not in SnakeConsumer.games:
            SnakeConsumer.games[self.room_name] = {
                'clients': {},
                'food': (random.randint(0, WIDTH) * GRID_SIZE, random.randint(0, HEIGHT) * GRID_SIZE),
            }

            # Start the game loop only once when the first client connects
            if not SnakeConsumer.game_loop_task:
                SnakeConsumer.game_loop_task = asyncio.create_task(self.move_snake())

        # Add the client to the game session with its own snake
        starting_x = GRID_SIZE
        starting_y = random.randint(0, HEIGHT) * GRID_SIZE

        # Add the client to the game session with its own snake
        SnakeConsumer.games[self.room_name]['clients'][self.channel_name] = {
            'username': self.username,
            'snake': [(starting_x, starting_y)],
            'direction': "right",
        }

        # Send initial game state to the client
        await self.send_game_state()

    async def receive(self, text_data):
        data = json.loads(text_data)
        if data.get('type') == 'set_player_info':
            room_name = data.get('room_name')
            username = data.get('username')

            # Check if the provided room name is valid
            if not room_name in ROOM:
                # Reject the connection for an invalid room name
                await self.close()
                return

            self.room_name = data.get('room_name')
            self.username = data.get('username')

            # Game start
            await self.init()
            await self.send(text_data=json.dumps({
                'type': 'game_start',
            }))

        elif data.get('type') == 'key_press':
            # Handle key press from the client
            key = data.get('key')
            # Process the key press as needed
            if key:
                await self.handle_keypress(key)

    async def disconnect(self, close_code):
        # # Remove the user from the room's group
        # await self.channel_layer.group_discard(
        #     self.room_group_name,
        #     self.channel_name
        # )

        try:
            # Remove the client from the game session
            del SnakeConsumer.games[self.room_name]['clients'][self.channel_name]

            # Cancel the game loop task when the client disconnects
            if not SnakeConsumer.games[self.room_name]['clients']:
                if SnakeConsumer.game_loop_task:
                    SnakeConsumer.game_loop_task.cancel()
                    SnakeConsumer.game_loop_task = None
                # If no clients left, remove the game session
                del SnakeConsumer.games[self.room_name]
        except:
            pass


        # await self.send_game_state()

    async def handle_keypress(self, key):
        direction = SnakeConsumer.games[self.room_name]['clients'][self.channel_name]['direction']

        if key == "w" and direction != "down":
            direction = "up"
        elif key == "s" and direction != "up":
            direction = "down"
        elif key == "a" and direction != "right":
            direction = "left"
        elif key == "d" and direction != "left":
            direction = "right"

        SnakeConsumer.games[self.room_name]['clients'][self.channel_name]['direction'] = direction

    async def send_game_state(self):
        # Send game state to the group
        await self.channel_layer.group_send(
            self.room_group_name,
            {
                'type': 'game_state',
                'clients': SnakeConsumer.games[self.room_name]['clients'],
                'food': SnakeConsumer.games[self.room_name]['food'],
            }
        )

    async def game_state(self, event):
        # Send game state to WebSocket
        await self.send(text_data=json.dumps({
            'type': event['type'],
            'clients': event['clients'],
            'food': event['food'],
        }))

    async def send_game_over(self, username, message):
        # Send game state to the group
        await self.channel_layer.group_send(
            self.room_group_name,
            {
                'type': 'game_over',
                'username': username,
                'message': message
            }
        )

    async def game_over(self, event):
        # Send game state to WebSocket
        await self.send(text_data=json.dumps({
            'type': event['type'],
            'username': event['username'],
            'message': event['message'],
        }))

    async def move_snake(self):
        try:
            while True:
                await asyncio.sleep(0.1)
                # Update the state for each client's snake
                for client_channel, client_data in SnakeConsumer.games[self.room_name]['clients'].items():
                    snake = client_data['snake']
                    username = client_data['username']
                    direction = client_data['direction']
                    food = SnakeConsumer.games[self.room_name]['food']

                    head_x, head_y = snake[0]
                    if direction == "up":
                        head_y -= GRID_SIZE
                    elif direction == "down":
                        head_y += GRID_SIZE
                    elif direction == "left":
                        head_x -= GRID_SIZE
                    elif direction == "right":
                        head_x += GRID_SIZE

                    # Check for collisions
                    collision = self.check_collision(client_channel,head_x, head_y)
                    if collision != Collisions.NO_COLLISION:
                        message = ""
                        # Send game over message
                        if collision == Collisions.SELF_COLLISION:
                            message = "You collided with your self!"
                        elif collision == Collisions.OTHER_COLLISION:
                            message = "You collided with other snake!"
                        elif collision == Collisions.BOUNDARY_COLLISION:
                            message = "You collided with the wall!"

                        await self.send_game_over(username,message)

                    # Move snake
                    snake.insert(0, (head_x, head_y))

                    # Check if the snake eats the food
                    # Check for collisions with food
                    if head_x == food[0] and head_y == food[1]:
                        SnakeConsumer.games[self.room_name]['food'] = (random.randint(0, WIDTH) * GRID_SIZE, random.randint(0, HEIGHT) * GRID_SIZE)
                    else:
                        snake.pop()

                    # Update the client's snake in the game state
                    SnakeConsumer.games[self.room_name]['clients'][client_channel]['snake'] = snake

                await self.send_game_state()

        except asyncio.CancelledError:
            pass

    def check_collision(self, client_channel, head_x, head_y):
        # Check for collision with own body
        if (head_x, head_y) in SnakeConsumer.games[self.room_name]['clients'][client_channel]['snake']:
            return Collisions.SELF_COLLISION

        # Check for collision with other players' snakes
        for client_id, client_data in SnakeConsumer.games[self.room_name]['clients'].items():
            if client_id != self.channel_name:  # Skip checking collision with the snake itself
                if (head_x, head_y) in client_data['snake']:
                    return Collisions.OTHER_COLLISION

        # Check for collision with game boundaries
        if head_x < 0 or head_x >= CANVAS_WIDTH or head_y < 0 or head_y >= CANVAS_HEIGHT:
            return Collisions.BOUNDARY_COLLISION

        return Collisions.NO_COLLISION
