from random import randint

from kivy.app import App
from kivy.uix.widget import Widget
from kivy.properties import NumericProperty, ReferenceListProperty, ObjectProperty
from kivy.clock import Clock
from kivy.vector import Vector

class PongPaddle(Widget):
    score = NumericProperty(0)

    def bounce_ball(self, ball):
        vx, vy = ball.velocity
        offset = (ball.center_y - self.center_y) / (self.height / 2)
        bounced = Vector(-1 * vx, vy)
        vel = bounced * 1.1
        ball.velocity = vel.x, vel.y + offset
        # if self.collide_widget(ball):
        #     vx, vy = ball.velocity
        #     offset = (ball.center_y - self.center_y) / (self.height / 2)
        #     bounced = Vector(-1 * vx, vy)
        #     vel = bounced * 1.1
        #     ball.velocity = vel.x, vel.y + offset

class PongBall(Widget):
    # velocity of the ball on x and y axis
    velocity_x = NumericProperty(0)
    velocity_y = NumericProperty(0)

    # referencelist property so we can use ball.velocity as
    # a shorthand, just like e.g. w.pos for w.x and w.y
    velocity = ReferenceListProperty(velocity_x, velocity_y)

    # ``move`` function will move the ball one step. This
    #  will be called in equal intervals to animate the ball
    def move(self):
        self.pos = Vector(*self.velocity) + self.pos

class PongGame(Widget):
    ball = ObjectProperty(None)
    player1 = ObjectProperty(None)
    player2 = ObjectProperty(None)

    # give a stationary ball initial velocity and direction
    def serve_ball(self,vel=(4,0)):
        self.ball.center = self.center
        self.ball.velocity = Vector(4, 0).rotate(randint(0, 360))

    def update(self, dt):
        self.ball.move()

        # bounce off paddles
        # self.player1.bounce_ball(self.ball)
        # self.player2.bounce_ball(self.ball)
        if self.player1.collide_widget(self.ball):
            self.player1.bounce_ball(self.ball)
        elif self.player2.collide_widget(self.ball):
            self.player2.bounce_ball(self.ball)

        # bounce off top and bottom
        if (self.ball.y < 0) or (self.ball.top > self.height):
            self.ball.velocity_y *= -1

        # # bounce off left and right
        # if (self.ball.x < 0) or (self.ball.right > self.width):
        #     self.ball.velocity_x *= -1
        # went off to a side to score point?
        if self.ball.x < self.x:
            self.player2.score += 1
            self.serve_ball(vel=(4, 0))
        if self.ball.right > self.width:
            self.player1.score += 1
            self.serve_ball(vel=(-4, 0))

    def on_touch_move(self, touch):
        if touch.x < self.width / 3:
            self.player1.center_y = touch.y
        if touch.x > self.width - self.width / 3:
            self.player2.center_y = touch.y


class PongApp(App):

    def build(self):
        game = PongGame()
        game.serve_ball()
        Clock.schedule_interval(game.update, Clock.get_resolution())
        return game

if __name__ == '__main__':
    PongApp().run()