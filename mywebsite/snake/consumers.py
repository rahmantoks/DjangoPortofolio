import json
import random
from channels.generic.websocket import AsyncWebsocketConsumer
from asgiref.sync import async_to_sync
import asyncio

class SnakeConsumer(AsyncWebsocketConsumer):
    games = {}
    async def connect(self):
        self.room_name = "snake_game"
        self.room_group_name = f"snake_game_{self.room_name}"       
        
        # Add the user to the room's group
        await self.channel_layer.group_add(
            self.room_group_name,
            self.channel_name
        )
        
        await self.accept()
        
        # Check if the game session already exists
        if self.room_name not in SnakeConsumer.games:
            SnakeConsumer.games[self.room_name] = {
                'clients': {},
                'food': (random.randint(0, 19) * 20, random.randint(0, 19) * 20),
            }

            # Start game loop
            self.game_loop_task = asyncio.create_task(self.move_snake())

        # Add the client to the game session with its own snake
        starting_x = 20
        starting_y = random.randint(0, 29) * 20

        # Add the client to the game session with its own snake
        SnakeConsumer.games[self.room_name]['clients'][self.channel_name] = {
            'snake': [(starting_x, starting_y)],
            'direction': "right",
        }

        # Send initial game state to the client
        await self.send_game_state()



    async def disconnect(self, close_code):
        # Remove the user from the room's group
        await self.channel_layer.group_discard(
            self.room_group_name,
            self.channel_name
        )

        # Remove the client from the game session
        del SnakeConsumer.games[self.room_name]['clients'][self.channel_name]

        # Cancel the game loop task when the client disconnects
        if not SnakeConsumer.games[self.room_name]['clients']:
            # If no clients left, remove the game session
            del SnakeConsumer.games[self.room_name]
        else:
            # If clients remain, update their game state
            await self.send_game_state()

        self.game_loop_task.cancel()

    async def receive(self, text_data):
        data = json.loads(text_data)
        key = data.get("key")

        if key:
            await self.handle_keypress(key)

    async def handle_keypress(self, key):
        if key == "w" and SnakeConsumer.games[self.room_name]['clients'][self.channel_name]['direction'] != "down":
            SnakeConsumer.games[self.room_name]['clients'][self.channel_name]['direction'] = "up"
        elif key == "s" and SnakeConsumer.games[self.room_name]['clients'][self.channel_name]['direction'] != "up":
            SnakeConsumer.games[self.room_name]['clients'][self.channel_name]['direction'] = "down"
        elif key == "a" and SnakeConsumer.games[self.room_name]['clients'][self.channel_name]['direction'] != "right":
            SnakeConsumer.games[self.room_name]['clients'][self.channel_name]['direction'] = "left"
        elif key == "d" and SnakeConsumer.games[self.room_name]['clients'][self.channel_name]['direction'] != "left":
            SnakeConsumer.games[self.room_name]['clients'][self.channel_name]['direction'] = "right"

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
            'clients': event['clients'],
            'food': event['food'],
        }))
        
    async def move_snake(self):
        try:
            while True:
                await asyncio.sleep(0.1)
                # Update the state for each client's snake
                for client_channel, client_data in SnakeConsumer.games[self.room_name]['clients'].items():
                    snake = client_data['snake']
                    direction = client_data['direction']
                    food = SnakeConsumer.games[self.room_name]['food']

                    head_x, head_y = snake[0]
                    if direction == "up":
                        head_y -= 20
                    elif direction == "down":
                        head_y += 20
                    elif direction == "left":
                        head_x -= 20
                    elif direction == "right":
                        head_x += 20

                    snake.insert(0, (head_x, head_y))

                    # Check for collisions
                    if (
                        head_x < 0
                        or head_x >= 600
                        or head_y < 0
                        or head_y >= 600
                    ):
                        snake = [(20,20)]
                        snake.insert(0,(20, random.randint(0, 29) * 20))

                    # Check if the snake eats the food
                    # Check for collisions with food
                    if head_x == food[0] and head_y == food[1]:
                        SnakeConsumer.games[self.room_name]['food'] = (random.randint(0, 29) * 20, random.randint(0, 29) * 20)
                    else:
                        snake.pop()

                    # Update the client's snake in the game state
                    SnakeConsumer.games[self.room_name]['clients'][client_channel]['snake'] = snake    

                await self.send_game_state()

        except asyncio.CancelledError:
            pass
