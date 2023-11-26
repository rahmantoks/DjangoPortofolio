import json
import random
from channels.generic.websocket import AsyncWebsocketConsumer
from asgiref.sync import async_to_sync
import asyncio

class SnakeConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        await self.accept()
        
        self.snake =[(20,20)]
        self.direction = "right"
        self.food = (random.randint(0,19) * 20, random.randint(0,19) * 20)

        # Send initial game state to the client
        await self.send_game_state()

        # Start game loop
        self.game_loop_task = asyncio.create_task(self.move_snake())

    async def disconnect(self, close_code):
        # Cancel the game loop task when the client disconnects
        self.game_loop_task.cancel()

    async def receive(self, text_data):
        data = json.loads(text_data)
        key = data.get("key")

        if key:
            await self.handle_keypress(key)

    async def handle_keypress(self, key):
        if key == "ArrowUp" and self.direction != "down":
            self.direction = "up"
        elif key == "ArrowDown" and self.direction != "up":
            self.direction = "down"
        elif key == "ArrowLeft" and self.direction != "right":
            self.direction = "left"
        elif key == "ArrowRight" and self.direction != "left":
            self.direction = "right"

    async def send_game_state(self):
        await self.send(text_data=json.dumps({
            'snake': self.snake,
            'food': self.food,
            }))

    async def move_snake(self):
        try:
            while True:
                await asyncio.sleep(0.1)

                head_x, head_y = self.snake[0]
                if self.direction == "up":
                    head_y -= 20
                elif self.direction == "down":
                    head_y += 20
                elif self.direction == "left":
                    head_x -= 20
                elif self.direction == "right":
                    head_x += 20

                self.snake.insert(0, (head_x, head_y))

                # Check for collisions
                if (
                    head_x < 0
                    or head_x >= 400
                    or head_y < 0
                    or head_y >= 400
                    or (head_x, head_y) in self.snake[1:]
                ):
                    await self.reset_game()
                    self.snake.insert(0, (40, 20))

                # Check if the snake eats the food
                if head_x == self.food[0] and head_y == self.food[1]:
                    self.food = (random.randint(0, 19) * 20, random.randint(0, 19) * 20)
                else:
                    self.snake.pop()

                await self.send_game_state()

        except asyncio.CancelledError:
            pass
    
    async def reset_game(self):
        self.snake = [(20, 20)]
        self.direction = "right"
        self.food = (random.randint(0, 19) * 20, random.randint(0, 19) * 20)


