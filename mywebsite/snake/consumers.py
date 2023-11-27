import json
import random
from channels.generic.websocket import AsyncWebsocketConsumer
from asgiref.sync import async_to_sync
import asyncio

ROOM = "perkenyi"
GRID_SIZE = 20
CANVAS_HEIGHT = 600
CANVAS_WIDTH = 1000
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
                'food': (random.randint(0, HEIGHT) * GRID_SIZE, random.randint(0, WIDTH) * GRID_SIZE),
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
        if data.get('type') == 'set_room_name':
            room_name = data.get('room_name')
            # Check if the provided room name is valid
            if room_name != ROOM:
                # Reject the connection for an invalid room name
                await self.close()
                return
            else:
                self.room_name = room_name
                # Prompt the user for a username
                await self.send(text_data=json.dumps({
                    'type': 'get_username',
                }))

        elif data.get('type') == 'set_username':
            self.username = data.get('username')
            await self.init()

        elif data.get('type') == 'key_press':
            # Handle key press from the client
            key = data.get('key')
            # Process the key press as needed
            if key:
                await self.handle_keypress(key)

    async def disconnect(self, close_code):
        # Remove the user from the room's group
        try:
            await self.channel_layer.group_discard(
                self.room_group_name,
                self.channel_name
            )
        except:
            pass

        # Remove the client from the game session
        del SnakeConsumer.games[self.room_name]['clients'][self.channel_name]

        # Cancel the game loop task when the client disconnects
        if not SnakeConsumer.games[self.room_name]['clients']:
            # If no clients left, remove the game session
            self.game_loop_task.cancel()
            del SnakeConsumer.games[self.room_name]
        else:
            # If clients remain, update their game state
            await self.send_game_state()

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

                    snake.insert(0, (head_x, head_y))

                    # Check for collisions
                    if (
                        head_x < 0
                        or head_x >= CANVAS_WIDTH
                        or head_y < 0
                        or head_y >= CANVAS_HEIGHT
                    ):
                        snake = [(GRID_SIZE,GRID_SIZE)]
                        snake.insert(0,(GRID_SIZE, random.randint(0, HEIGHT) * GRID_SIZE))

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

