import kivy
kivy.require('2.0.0')

from kivy.app import App
from kivy.uix.widget import Widget
from kivy.uix.button import Button
from kivy.uix.label import Label
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.floatlayout import FloatLayout
from kivy.uix.screenmanager import ScreenManager, Screen
from kivy.uix.popup import Popup
from kivy.uix.slider import Slider
from kivy.uix.switch import Switch
from kivy.graphics import Rectangle, Color, Line, Ellipse
from kivy.clock import Clock
from kivy.core.window import Window
from kivy.vector import Vector
import random
import math
import json
import os
import requests
import webbrowser
import threading
import time

# Import AdMob Configuration
try:
    from admob_config import *
except ImportError:
    # Fallback to your real IDs if config file is missing
    ADMOB_APP_ID = "ca-app-pub-8134227271086623~8232284552"
    BANNER_AD_UNIT_ID = "ca-app-pub-8134227271086623/2979957871"
    INTERSTITIAL_AD_UNIT_ID = "ca-app-pub-8134227271086623/6727631198"
    REWARDED_AD_UNIT_ID = "ca-app-pub-8134227271086623/3954692844"

# Google AdMob Configuration
class AdManager:
    def __init__(self):
        # Google AdMob IDs from admob_config.py
        self.app_id = ADMOB_APP_ID
        self.banner_ad_unit_id = BANNER_AD_UNIT_ID
        self.interstitial_ad_unit_id = INTERSTITIAL_AD_UNIT_ID
        self.rewarded_ad_unit_id = REWARDED_AD_UNIT_ID
        
        self.game_count = 0
        self.ad_shown_count = 0
        self.ads_enabled = True
        
    def should_show_ad(self):
        """Show ad after every game over"""
        return self.ads_enabled
    
    def show_game_over_ad(self, callback=None):
        """Show interstitial ad when game is over"""
        self.game_count += 1
        if self.should_show_ad():
            self.show_interstitial_ad(callback)
        elif callback:
            callback()
    
    def show_interstitial_ad(self, callback=None):
        """Show Google AdMob interstitial ad"""
        try:
            # For mobile app, use real AdMob
            from kivmob import KivMob
            ads = KivMob(self.app_id)
            ads.new_interstitial(self.interstitial_ad_unit_id)
            ads.request_interstitial()
            ads.show_interstitial()
            self.ad_shown_count += 1
            if callback:
                callback()
        except ImportError:
            # Fallback for desktop testing
            self.show_ad_placeholder("Advertisement", callback)
    
    def show_rewarded_ad(self, callback=None):
        """Show Google AdMob rewarded ad for revive"""
        try:
            # For mobile app, use real AdMob
            from kivmob import KivMob
            ads = KivMob(self.app_id)
            ads.new_rewarded(self.rewarded_ad_unit_id)
            ads.request_rewarded()
            ads.show_rewarded()
            self.ad_shown_count += 1
            if callback:
                callback(True)  # Reward granted
        except ImportError:
            # Fallback for desktop testing
            self.show_ad_placeholder("Watch Ad to Revive", callback, is_revive=True)
    
    def show_ad_placeholder(self, title, callback=None, is_revive=False):
        """Placeholder ad for desktop testing"""
        from kivy.uix.popup import Popup
        from kivy.uix.boxlayout import BoxLayout
        from kivy.uix.label import Label
        from kivy.uix.button import Button
        from kivy.graphics import Rectangle, Color
        from kivy.clock import Clock
        
        layout = BoxLayout(orientation='vertical', padding=20, spacing=15)
        
        with layout.canvas.before:
            Color(0.1, 0.1, 0.2, 0.95)
        
        title_label = Label(
            text=title,
            font_size='24sp',
            bold=True,
            color=(0.4, 1, 0.4, 1),
            size_hint_y=0.3
        )
        layout.add_widget(title_label)
        
        ad_label = Label(
            text='Google AdMob Ad\n(Desktop Testing Mode)\n\nReal ads will show on mobile',
            font_size='18sp',
            color=(1, 1, 1, 1),
            text_size=(300, None),
            halign='center',
            size_hint_y=0.4
        )
        layout.add_widget(ad_label)
        
        close_text = 'REVIVE!' if is_revive else 'CONTINUE'
        close_btn = Button(
            text=close_text,
            font_size='18sp',
            background_color=(0.2, 0.8, 0.2, 1),
            size_hint_y=0.3
        )
        layout.add_widget(close_btn)
        
        popup = Popup(
            title='',
            content=layout,
            size_hint=(0.7, 0.6),
            auto_dismiss=False
        )
        
        def close_ad(*args):
            popup.dismiss()
            self.ad_shown_count += 1
            if callback:
                callback(is_revive)
        
        close_btn.bind(on_press=close_ad)
        popup.open()
    
    def create_banner_ad(self):
        """Create Google AdMob banner ad"""
        try:
            # For mobile app, use real AdMob banner
            from kivmob import KivMob
            from kivy.uix.label import Label
            
            # This would be replaced with actual AdMob banner in mobile app
            banner = Label(
                text='[Google AdMob Banner - Mobile Only]',
                font_size='12sp',
                color=(0.8, 0.8, 0.8, 1),
            size_hint_y=None,
                height=50
            )
            return banner
            
        except ImportError:
            # Desktop placeholder
            from kivy.uix.label import Label
            banner = Label(
                text='[Google AdMob Banner Placeholder]',
                font_size='12sp',
                color=(0.8, 0.8, 0.8, 1),
                size_hint_y=None,
                height=50
            )
            return banner
    
    def get_stats_text(self):
        """Get ad statistics"""
        return f'Games: {self.game_count} | Ads: {int(self.ad_shown_count)}'

# Global ad manager
ad_manager = AdManager()

# Simple color constants
BLACK = (0, 0, 0, 1)
WHITE = (1, 1, 1, 1)
GREEN = (0, 1, 0, 1)
RED = (1, 0, 0, 1)
BLUE = (0, 0, 1, 1)
YELLOW = (1, 1, 0, 1)
PURPLE = (1, 0, 1, 1)
ORANGE = (1, 0.5, 0, 1)
GRAY = (0.5, 0.5, 0.5, 1)

# Settings Manager
class GameSettings:
    def __init__(self):
        self.settings_file = 'game_settings.json'
        self.default_settings = {
            'difficulty': 'medium',  # easy, medium, hard
            'sound_enabled': True,
            'vibration_enabled': True,
            'touch_controls': True,
            'control_sensitivity': 0.7,
            'game_speed': 0.15,
            'grid_size': 'medium'  # small, medium, large
        }
        self.load_settings()
    
    def load_settings(self):
        try:
            if os.path.exists(self.settings_file):
                with open(self.settings_file, 'r') as f:
                    self.settings = json.load(f)
            else:
                self.settings = self.default_settings.copy()
        except:
            self.settings = self.default_settings.copy()
    
    def save_settings(self):
        try:
            with open(self.settings_file, 'w') as f:
                json.dump(self.settings, f, indent=2)
        except:
            pass
    
    def get(self, key):
        return self.settings.get(key, self.default_settings.get(key))
    
    def set(self, key, value):
        self.settings[key] = value
        self.save_settings()
    
    def get_speed_for_difficulty(self):
        speeds = {'easy': 0.2, 'medium': 0.15, 'hard': 0.1}
        return speeds.get(self.get('difficulty'), 0.15)
    
    def get_grid_size_info(self):
        sizes = {
            'small': {'width': 20, 'height': 15, 'cell_size': 30},
            'medium': {'width': 25, 'height': 20, 'cell_size': 25},
            'large': {'width': 30, 'height': 25, 'cell_size': 20}
        }
        return sizes.get(self.get('grid_size'), sizes['medium'])

# Global settings instance
game_settings = GameSettings()

class SimpleButton(Button):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.background_color = (0, 0, 0, 0)  # Transparent background
        self.color = WHITE
        self.font_size = '20sp'
        self.bold = True
        self.size_hint = (None, None)
        self.size = (200, 50)
        
        # Custom graphics
        self.bind(pos=self.update_graphics, size=self.update_graphics)
        self.update_graphics()
        
    def update_graphics(self, *args):
        self.canvas.before.clear()
        with self.canvas.before:
            # Button glow
            Color(0.2, 0.6, 1, 0.3)
            Rectangle(pos=(self.x-4, self.y-4), size=(self.width+8, self.height+8))
            
            # Main button
            Color(0.1, 0.3, 0.8, 0.9)
            Rectangle(pos=self.pos, size=self.size)
            
            # Button highlight
            Color(0.3, 0.5, 1, 0.6)
            Rectangle(pos=(self.x+2, self.y+2), size=(self.width-4, self.height-4))
            
            # Border
            Color(0.4, 0.7, 1, 1)
            Line(rectangle=(*self.pos, *self.size), width=2)

class Snake:
    def __init__(self, grid_width, grid_height, cell_size):
        self.grid_width = grid_width
        self.grid_height = grid_height
        self.cell_size = cell_size
        self.reset()
        
    def reset(self):
        center_x = self.grid_width // 2
        center_y = self.grid_height // 2
        self.body = [(center_x, center_y), (center_x-1, center_y), (center_x-2, center_y)]
        self.direction = (1, 0)
        self.next_direction = (1, 0)
        self.grow_pending = 0
        
    def move(self):
        self.direction = self.next_direction
        head = self.body[0]
        new_head = (head[0] + self.direction[0], head[1] + self.direction[1])
        self.body.insert(0, new_head)
        
        if self.grow_pending > 0:
            self.grow_pending -= 1
        else:
            self.body.pop()
    
    def change_direction(self, new_direction):
        if (self.direction[0] * -1, self.direction[1] * -1) != new_direction:
            self.next_direction = new_direction
    
    def grow(self, amount=1):
        self.grow_pending += amount
    
    def check_collision(self):
        head = self.body[0]
        
        # Wall collision
        if (head[0] < 0 or head[0] >= self.grid_width or 
            head[1] < 0 or head[1] >= self.grid_height):
            return True
            
        # Self collision
        return head in self.body[1:]

class Food:
    def __init__(self, grid_width, grid_height):
        self.grid_width = grid_width
        self.grid_height = grid_height
        self.types = {
            'normal': {'color': ORANGE, 'points': 10, 'growth': 1},
            'bonus': {'color': PURPLE, 'points': 25, 'growth': 2},
            'speed': {'color': BLUE, 'points': 15, 'growth': 1}
        }
        self.spawn()
        
    def spawn(self):
        self.position = (
            random.randint(0, self.grid_width - 1),
            random.randint(0, self.grid_height - 1)
        )
        
        rand = random.random()
        if rand < 0.7:
            self.type = 'normal'
        elif rand < 0.9:
            self.type = 'bonus'
        else:
            self.type = 'speed'
    
    def get_info(self):
        return self.types[self.type]

class GameWidget(Widget):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        
        # Use settings for grid configuration
        grid_info = game_settings.get_grid_size_info()
        self.grid_width = grid_info['width']
        self.grid_height = grid_info['height']
        self.cell_size = grid_info['cell_size']
        
        self.snake = Snake(self.grid_width, self.grid_height, self.cell_size)
        self.food = Food(self.grid_width, self.grid_height)
        
        self.score = 0
        self.level = 1
        self.high_score = 0
        self.game_over = False
        self.paused = False
        
        # Touch controls for mobile
        self.touch_start_pos = None
        self.min_swipe_distance = 50
        
        self.bind(size=self.update_graphics)
        self.bind(pos=self.update_graphics)
        
        # Enable touch if settings allow
        if game_settings.get('touch_controls'):
            self.bind(on_touch_down=self.on_touch_down)
            self.bind(on_touch_up=self.on_touch_up)
        
    def start_game(self):
        self.snake.reset()
        self.food.spawn()
        self.score = 0
        self.level = 1
        self.game_over = False
        self.paused = False
        
        Clock.unschedule(self.update)
        # Use settings-based speed
        game_speed = game_settings.get_speed_for_difficulty()
        Clock.schedule_interval(self.update, game_speed)
        
    def update(self, dt):
        if not self.game_over and not self.paused:
            self.move_snake()
            self.check_food_collision()
            self.update_graphics()
            
            if self.snake.check_collision():
                self.game_over = True
                Clock.unschedule(self.update)
                return False
        
    def move_snake(self):
        self.snake.move()
        
    def check_food_collision(self):
        if self.snake.body[0] == self.food.position:
            food_info = self.food.get_info()
            self.score += food_info['points']
            self.snake.grow(food_info['growth'])
            
            # Avoid spawning food on snake
            while True:
                self.food.spawn()
                if self.food.position not in self.snake.body:
                    break
            
            # Level up every 100 points
            new_level = (self.score // 100) + 1
            if new_level > self.level:
                self.level = new_level
                
            if self.score > self.high_score:
                self.high_score = self.score
        
    def update_graphics(self, *args):
        self.canvas.clear()
        
        with self.canvas:
            # STUNNING gradient background with depth
            # Base layer - deep space blue
            Color(0.02, 0.02, 0.1, 1)
            Rectangle(pos=self.pos, size=self.size)
            
            # Gradient overlay
            Color(0.05, 0.05, 0.15, 0.8)
            Rectangle(pos=self.pos, size=self.size)
            
            # Animated hexagonal pattern
            Color(0.1, 0.1, 0.25, 0.4)
            hex_size = 40
            for i in range(0, int(self.width), hex_size):
                for j in range(0, int(self.height), hex_size):
                    if (i // hex_size + j // hex_size) % 3 == 0:
                        # Create hexagon-like pattern
                        center_x = self.x + i + hex_size//2
                        center_y = self.y + j + hex_size//2
                        
                        # Simple diamond pattern
                        points = [
                            center_x, center_y - 15,
                            center_x + 15, center_y,
                            center_x, center_y + 15,
                            center_x - 15, center_y
                        ]
                        Line(points=points + [points[0], points[1]], width=1)
            
            # Glowing circuit-like grid
            Color(0.2, 0.4, 0.6, 0.6)
            for i in range(self.grid_width + 1):
                x = self.x + i * self.cell_size
                Line(points=[x, self.y, x, self.y + self.grid_height * self.cell_size], width=2)
            
            for i in range(self.grid_height + 1):
                y = self.y + i * self.cell_size
                Line(points=[self.x, y, self.x + self.grid_width * self.cell_size, y], width=2)
                
            # Grid intersection glows
            Color(0.3, 0.6, 0.9, 0.4)
            for i in range(self.grid_width + 1):
                for j in range(self.grid_height + 1):
                    if (i + j) % 3 == 0:
                        x = self.x + i * self.cell_size
                        y = self.y + j * self.cell_size
                        Ellipse(pos=(x-2, y-2), size=(4, 4))
            
            # AMAZING Snake with ultra-realistic effects
            for i, segment in enumerate(self.snake.body):
                x = self.x + segment[0] * self.cell_size
                y = self.y + segment[1] * self.cell_size
                
                if i == 0:  # Snake Head - Ultra realistic with multiple glow layers
                    # Mega outer glow
                    Color(0.3, 1, 0.3, 0.15)
                    Ellipse(pos=(x-8, y-8), size=(self.cell_size+16, self.cell_size+16))
                    
                    # Medium glow
                    Color(0.4, 1, 0.4, 0.25)
                    Ellipse(pos=(x-5, y-5), size=(self.cell_size+10, self.cell_size+10))
                    
                    # Inner glow
                    Color(0.5, 1, 0.5, 0.4)
                    Ellipse(pos=(x-3, y-3), size=(self.cell_size+6, self.cell_size+6))
                    
                    # Main head - bright neon green
                    Color(0.1, 1, 0.1, 1)
                    Ellipse(pos=(x+1, y+1), size=(self.cell_size-2, self.cell_size-2))
                    
                    # Head metallic highlight
                    Color(0.8, 1, 0.8, 0.9)
                    Ellipse(pos=(x+3, y+5), size=(self.cell_size-8, self.cell_size-12))
                    
                    # Secondary highlight
                    Color(0.9, 1, 0.9, 0.6)
                    Ellipse(pos=(x+5, y+7), size=(self.cell_size-12, self.cell_size-16))
                    
                    # Animated eyes with pupils
                    Color(1, 1, 1, 1)  # White eye base
                    eye_size = 5
                    pupil_size = 2
                    
                    if self.snake.direction == (1, 0):  # Right
                        # Eyes
                        Ellipse(pos=(x+self.cell_size-10, y+5), size=(eye_size, eye_size))
                        Ellipse(pos=(x+self.cell_size-10, y+15), size=(eye_size, eye_size))
                        # Pupils
                        Color(0, 0, 0, 1)
                        Ellipse(pos=(x+self.cell_size-8, y+6), size=(pupil_size, pupil_size))
                        Ellipse(pos=(x+self.cell_size-8, y+16), size=(pupil_size, pupil_size))
                    elif self.snake.direction == (-1, 0):  # Left
                        Ellipse(pos=(x+2, y+5), size=(eye_size, eye_size))
                        Ellipse(pos=(x+2, y+15), size=(eye_size, eye_size))
                        Color(0, 0, 0, 1)
                        Ellipse(pos=(x+4, y+6), size=(pupil_size, pupil_size))
                        Ellipse(pos=(x+4, y+16), size=(pupil_size, pupil_size))
                    elif self.snake.direction == (0, 1):  # Up
                        Ellipse(pos=(x+5, y+self.cell_size-10), size=(eye_size, eye_size))
                        Ellipse(pos=(x+15, y+self.cell_size-10), size=(eye_size, eye_size))
                        Color(0, 0, 0, 1)
                        Ellipse(pos=(x+6, y+self.cell_size-8), size=(pupil_size, pupil_size))
                        Ellipse(pos=(x+16, y+self.cell_size-8), size=(pupil_size, pupil_size))
                    else:  # Down
                        Ellipse(pos=(x+5, y+2), size=(eye_size, eye_size))
                        Ellipse(pos=(x+15, y+2), size=(eye_size, eye_size))
                        Color(0, 0, 0, 1)
                        Ellipse(pos=(x+6, y+4), size=(pupil_size, pupil_size))
                        Ellipse(pos=(x+16, y+4), size=(pupil_size, pupil_size))
                        
                else:  # Snake Body - Ultra gradient with glow trail
                    # Trail glow effect
                    trail_intensity = max(0.1, 1.0 - (i * 0.08))
                    Color(0.2, 0.8, 0.2, trail_intensity * 0.3)
                    Ellipse(pos=(x-4, y-4), size=(self.cell_size+8, self.cell_size+8))
                    
                    # Body shadow with depth
                    Color(0, 0.2, 0, 0.6)
                    Ellipse(pos=(x+2, y-1), size=(self.cell_size-2, self.cell_size-2))
                    
                    # Main body with gradient
                    intensity = max(0.4, 1.0 - (i * 0.06))
                    Color(0.05, intensity * 0.9, 0.05, 1)
                    Ellipse(pos=(x+2, y+2), size=(self.cell_size-4, self.cell_size-4))
                    
                    # Body metallic highlight
                    Color(0.2, intensity, 0.2, 0.8)
                    Ellipse(pos=(x+4, y+4), size=(self.cell_size-8, self.cell_size-8))
                    
                    # Inner body shine
                    Color(0.4, min(1.0, intensity + 0.3), 0.4, 0.5)
                    Ellipse(pos=(x+6, y+6), size=(self.cell_size-12, self.cell_size-12))
            
            # STUNNING Food with ultra-realistic glow effects
            food_info = self.food.get_info()
            x = self.x + self.food.position[0] * self.cell_size
            y = self.y + self.food.position[1] * self.cell_size
            
            # Multi-layer glow effects
            Color(*food_info['color'][:3], 0.1)
            Ellipse(pos=(x-10, y-10), size=(self.cell_size+20, self.cell_size+20))
            
            Color(*food_info['color'][:3], 0.2)
            Ellipse(pos=(x-6, y-6), size=(self.cell_size+12, self.cell_size+12))
            
            Color(*food_info['color'][:3], 0.4)
            Ellipse(pos=(x-3, y-3), size=(self.cell_size+6, self.cell_size+6))
            
            if self.food.type == 'normal':  # Ultra-realistic Apple
                # Apple shadow
                Color(0.2, 0.1, 0, 0.5)
                Ellipse(pos=(x+3, y), size=(self.cell_size-4, self.cell_size-4))
                
                # Main apple body
                Color(*food_info['color'])
                Ellipse(pos=(x+2, y+2), size=(self.cell_size-4, self.cell_size-4))
                
                # Apple gradient highlight
                Color(1, 0.9, 0.5, 0.8)
                Ellipse(pos=(x+4, y+8), size=(self.cell_size-12, self.cell_size-16))
                
                # Apple shine
                Color(1, 1, 0.8, 0.9)
                Ellipse(pos=(x+6, y+10), size=(self.cell_size-16, self.cell_size-20))
                
                # Apple stem with leaf
                Color(0.4, 0.2, 0, 1)
                Rectangle(pos=(x+self.cell_size//2-1, y+self.cell_size-6), size=(2, 5))
                # Leaf
                Color(0.2, 0.6, 0.2, 1)
                Ellipse(pos=(x+self.cell_size//2+1, y+self.cell_size-4), size=(4, 2))
                
            elif self.food.type == 'bonus':  # Glowing Crystal Diamond
                center_x = x + self.cell_size//2
                center_y = y + self.cell_size//2
                
                # Crystal shadow
                Color(0.2, 0, 0.2, 0.6)
                points = [
                    center_x+1, center_y-8,  # Top
                    center_x+8, center_y+1,  # Right
                    center_x+1, center_y+8,  # Bottom
                    center_x-8, center_y+1   # Left
                ]
                Line(points=points + [points[0], points[1]], width=4)
                
                # Main crystal
                Color(*food_info['color'])
                points = [
                    center_x, center_y-10,  # Top
                    center_x+10, center_y,  # Right
                    center_x, center_y+10,  # Bottom
                    center_x-10, center_y   # Left
                ]
                Line(points=points + [points[0], points[1]], width=4)
                
                # Crystal inner glow
                Color(*food_info['color'][:3], 0.8)
                Ellipse(pos=(center_x-6, center_y-6), size=(12, 12))
                
                # Crystal core
                Color(1, 0.8, 1, 1)
                Ellipse(pos=(center_x-3, center_y-3), size=(6, 6))
                
                # Crystal sparkles
                Color(1, 1, 1, 0.9)
                for i in range(4):
                    angle = i * math.pi / 2
                    spark_x = center_x + 6 * math.cos(angle)
                    spark_y = center_y + 6 * math.sin(angle)
                    Ellipse(pos=(spark_x-1, spark_y-1), size=(2, 2))
                
            else:  # Blazing Speed Star
                center_x = x + self.cell_size//2
                center_y = y + self.cell_size//2
                
                # Star shadow
                Color(0, 0, 0.3, 0.5)
                for i in range(5):
                    outer_angle = i * 2 * math.pi / 5 - math.pi/2
                    inner_angle = (i + 0.5) * 2 * math.pi / 5 - math.pi/2
                    
                    outer_x = center_x + 10 * math.cos(outer_angle) + 1
                    outer_y = center_y + 10 * math.sin(outer_angle) - 1
                    inner_x = center_x + 5 * math.cos(inner_angle) + 1
                    inner_y = center_y + 5 * math.sin(inner_angle) - 1
                    
                    Line(points=[center_x+1, center_y-1, outer_x, outer_y, inner_x, inner_y], width=2)
                
                # Main star with gradient
                Color(*food_info['color'])
                for i in range(5):
                    outer_angle = i * 2 * math.pi / 5 - math.pi/2
                    inner_angle = (i + 0.5) * 2 * math.pi / 5 - math.pi/2
                    
                    outer_x = center_x + 10 * math.cos(outer_angle)
                    outer_y = center_y + 10 * math.sin(outer_angle)
                    inner_x = center_x + 5 * math.cos(inner_angle)
                    inner_y = center_y + 5 * math.sin(inner_angle)
                    
                    Line(points=[center_x, center_y, outer_x, outer_y, inner_x, inner_y], width=3)
                
                # Star center with pulsing effect
                Color(0.8, 0.8, 1, 1)
                Ellipse(pos=(center_x-4, center_y-4), size=(8, 8))
                
                # Star core
                Color(1, 1, 1, 1)
                Ellipse(pos=(center_x-2, center_y-2), size=(4, 4))
                
                # Energy trails
                Color(*food_info['color'][:3], 0.6)
                for i in range(8):
                    trail_angle = i * math.pi / 4
                    trail_x = center_x + 12 * math.cos(trail_angle)
                    trail_y = center_y + 12 * math.sin(trail_angle)
                    Line(points=[center_x, center_y, trail_x, trail_y], width=1)
    
    def on_touch_down(self, touch):
        if self.collide_point(*touch.pos) and game_settings.get('touch_controls'):
            self.touch_start_pos = touch.pos
            return True
        return False
    
    def on_touch_up(self, touch):
        if (self.touch_start_pos and game_settings.get('touch_controls') and 
            not self.game_over and not self.paused):
            
            # Calculate swipe direction
            dx = touch.pos[0] - self.touch_start_pos[0]
            dy = touch.pos[1] - self.touch_start_pos[1]
            
            # Check if swipe is long enough
            swipe_distance = math.sqrt(dx*dx + dy*dy)
            sensitivity = game_settings.get('control_sensitivity')
            min_distance = self.min_swipe_distance * sensitivity
            
            if swipe_distance > min_distance:
                # Determine primary direction
                if abs(dx) > abs(dy):
                    # Horizontal swipe
                    if dx > 0:
                        self.snake.change_direction((1, 0))  # Right
                    else:
                        self.snake.change_direction((-1, 0))  # Left
                else:
                    # Vertical swipe
                    if dy > 0:
                        self.snake.change_direction((0, 1))  # Up
                    else:
                        self.snake.change_direction((0, -1))  # Down
            else:
                # Short tap - pause/unpause
                self.paused = not self.paused
                
            self.touch_start_pos = None
            return True
        return False

class MenuScreen(Screen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        
        layout = FloatLayout()
        
        # Add beautiful background
        with self.canvas.before:
            Color(0.05, 0.05, 0.15, 1)  # Dark blue background
            self.bg_rect = Rectangle(pos=self.pos, size=self.size)
            
            # Add animated background pattern
            Color(0.1, 0.1, 0.2, 0.2)
            for i in range(0, 800, 60):
                for j in range(0, 600, 60):
                    if (i // 60 + j // 60) % 2 == 0:
                        Rectangle(pos=(i, j), size=(30, 30))
        
        self.bind(size=self.update_bg, pos=self.update_bg)
        
        # Title with glow effect
        title = Label(
            text='🐍 SNAKE GAME 🐍',
            font_size='52sp',
            bold=True,
            color=(0.3, 1, 0.3, 1),  # Bright green
            pos_hint={'center_x': 0.5, 'center_y': 0.8}
        )
        layout.add_widget(title)
        
        # High Score with bright styling
        self.high_score_label = Label(
            text='High Score: 0',
            font_size='26sp',
            color=(1, 0.8, 0.3, 1),  # Bright orange
            bold=True,
            pos_hint={'center_x': 0.5, 'center_y': 0.65}
        )
        layout.add_widget(self.high_score_label)
        
        # Start Button
        start_btn = SimpleButton(
            text='START GAME',
            pos_hint={'center_x': 0.5, 'center_y': 0.5}
        )
        start_btn.bind(on_press=self.start_game)
        layout.add_widget(start_btn)
        
        # Settings Button
        settings_btn = SimpleButton(
            text='SETTINGS',
            pos_hint={'center_x': 0.5, 'center_y': 0.4}
        )
        settings_btn.bind(on_press=self.show_settings)
        layout.add_widget(settings_btn)
        
        # Help Button
        help_btn = SimpleButton(
            text='HELP',
            pos_hint={'center_x': 0.5, 'center_y': 0.3}
        )
        help_btn.bind(on_press=self.show_help)
        layout.add_widget(help_btn)
        
        # Quit Button
        quit_btn = SimpleButton(
            text='QUIT',
            pos_hint={'center_x': 0.5, 'center_y': 0.2}
        )
        quit_btn.bind(on_press=self.quit_game)
        layout.add_widget(quit_btn)
        
        # Add banner ad at bottom (mobile-friendly)
        banner_ad = ad_manager.create_banner_ad()
        layout.add_widget(banner_ad)
        
        self.add_widget(layout)
    
    def update_bg(self, *args):
        self.bg_rect.size = self.size
        self.bg_rect.pos = self.pos
        
    def update_high_score(self, score):
        self.high_score_label.text = f'High Score: {score}'
        
    def start_game(self, instance):
        self.manager.current = 'game'
    
    def show_settings(self, instance):
        self.manager.current = 'settings'
        
    def show_help(self, instance):
        # Create beautiful help popup
        help_layout = BoxLayout(orientation='vertical', padding=20, spacing=15)
        
        # Title
        title = Label(
            text='🎮 HOW TO PLAY 🎮',
            font_size='28sp',
            bold=True,
            color=(0.3, 1, 0.3, 1),
            size_hint_y=None,
            height=60
        )
        help_layout.add_widget(title)
        
        # Controls section
        controls_label = Label(
            text='🕹️ CONTROLS:',
            font_size='22sp',
            bold=True,
            color=(1, 1, 0.3, 1),
            size_hint_y=None,
            height=40
        )
        help_layout.add_widget(controls_label)
        
        # Dynamic controls text based on settings
        if game_settings.get('touch_controls'):
            controls_info = '📱 Mobile: Swipe to move snake, tap to pause\n⌨️ Desktop: Arrow Keys or WASD to move\n⏸️ Space to pause/unpause'
        else:
            controls_info = '⬆️⬇️⬅️➡️ Arrow Keys or WASD to move\n⏸️ Space to pause/unpause'
            
        controls_text = Label(
            text=controls_info,
            font_size='18sp',
            color=(1, 1, 1, 1),
            size_hint_y=None,
            height=80
        )
        help_layout.add_widget(controls_text)
        
        # Food section
        food_label = Label(
            text='🍎 FOOD TYPES:',
            font_size='22sp',
            bold=True,
            color=(1, 0.8, 0.3, 1),
            size_hint_y=None,
            height=40
        )
        help_layout.add_widget(food_label)
        
        food_text = Label(
            text='🍎 Orange Apple: 10 points, 1 growth\n💎 Purple Crystal: 25 points, 2 growth\n⭐ Blue Star: 15 points, 1 growth',
            font_size='18sp',
            color=(1, 1, 1, 1),
            size_hint_y=None,
            height=80
        )
        help_layout.add_widget(food_text)
        
        # Goal section
        goal_text = Label(
            text='🎯 GOAL: Eat food to grow and score points!\n💀 Don\'t hit walls or yourself!',
            font_size='18sp',
            color=(0.3, 1, 0.8, 1),
            bold=True,
            size_hint_y=None,
            height=60
        )
        help_layout.add_widget(goal_text)
        
        # Add small banner ad in help (mobile-friendly)
        help_banner = ad_manager.create_banner_ad()
        help_layout.add_widget(help_banner)
        
        # Close button
        close_btn = SimpleButton(
            text='GOT IT! 👍',
            size_hint=(None, None),
            size=(150, 50)
        )
        help_layout.add_widget(close_btn)
        
        # Create popup with beautiful styling
        popup = Popup(
            title='',
            content=help_layout,
            size_hint=(0.8, 0.85),  # Slightly taller for banner
            background_color=(0.05, 0.05, 0.15, 0.95)
        )
        
        close_btn.bind(on_press=popup.dismiss)
        popup.open()
        
    def quit_game(self, instance):
        App.get_running_app().stop()

class SettingsScreen(Screen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        
        main_layout = BoxLayout(orientation='vertical', padding=20, spacing=10)
        
        # Add beautiful background
        with self.canvas.before:
            Color(0.05, 0.05, 0.15, 1)  # Dark blue background
            self.bg_rect = Rectangle(pos=self.pos, size=self.size)
            
            # Add pattern
            Color(0.1, 0.1, 0.2, 0.2)
            for i in range(0, 800, 60):
                for j in range(0, 600, 60):
                    if (i // 60 + j // 60) % 2 == 0:
                        Rectangle(pos=(i, j), size=(30, 30))
        
        self.bind(size=self.update_bg, pos=self.update_bg)
        
        # Title
        title = Label(
            text='⚙️ GAME SETTINGS ⚙️',
            font_size='42sp',
            bold=True,
            color=(0.3, 1, 0.3, 1),
            size_hint_y=None,
            height=80
        )
        main_layout.add_widget(title)
        
        # Settings content in scrollable area
        settings_layout = BoxLayout(orientation='vertical', spacing=15, size_hint_y=None)
        settings_layout.bind(minimum_height=settings_layout.setter('height'))
        
        # Difficulty Setting
        diff_layout = BoxLayout(orientation='horizontal', size_hint_y=None, height=50)
        diff_label = Label(
            text='🎯 Difficulty:', 
            font_size='22sp', 
            color=WHITE, 
            bold=True,
            size_hint_x=0.4
        )
        diff_layout.add_widget(diff_label)
        
        self.difficulty_buttons = {}
        difficulty_box = BoxLayout(orientation='horizontal', size_hint_x=0.6)
        for diff in ['Easy', 'Medium', 'Hard']:
            btn = Button(
                text=diff,
                font_size='18sp',
                size_hint=(1, 1)
            )
            btn.bind(on_press=lambda x, d=diff.lower(): self.set_difficulty(d))
            self.difficulty_buttons[diff.lower()] = btn
            difficulty_box.add_widget(btn)
        
        diff_layout.add_widget(difficulty_box)
        settings_layout.add_widget(diff_layout)
        
        # Grid Size Setting
        grid_layout = BoxLayout(orientation='horizontal', size_hint_y=None, height=50)
        grid_label = Label(
            text='📏 Grid Size:', 
            font_size='22sp', 
            color=WHITE, 
            bold=True,
            size_hint_x=0.4
        )
        grid_layout.add_widget(grid_label)
        
        self.grid_buttons = {}
        grid_box = BoxLayout(orientation='horizontal', size_hint_x=0.6)
        for size in ['Small', 'Medium', 'Large']:
            btn = Button(
                text=size,
                font_size='18sp',
                size_hint=(1, 1)
            )
            btn.bind(on_press=lambda x, s=size.lower(): self.set_grid_size(s))
            self.grid_buttons[size.lower()] = btn
            grid_box.add_widget(btn)
        
        grid_layout.add_widget(grid_box)
        settings_layout.add_widget(grid_layout)
        
        # Touch Controls Setting
        touch_layout = BoxLayout(orientation='horizontal', size_hint_y=None, height=50)
        touch_label = Label(
            text='📱 Touch Controls:', 
            font_size='22sp', 
            color=WHITE, 
            bold=True,
            size_hint_x=0.7
        )
        touch_layout.add_widget(touch_label)
        
        self.touch_switch = Switch(
            active=game_settings.get('touch_controls'),
            size_hint_x=0.3
        )
        self.touch_switch.bind(active=self.toggle_touch_controls)
        touch_layout.add_widget(self.touch_switch)
        settings_layout.add_widget(touch_layout)
        
        # Control Sensitivity Setting
        sensitivity_layout = BoxLayout(orientation='vertical', size_hint_y=None, height=80)
        sens_label = Label(
            text='🎮 Touch Sensitivity:', 
            font_size='22sp', 
            color=WHITE, 
            bold=True,
            size_hint_y=0.6
        )
        sensitivity_layout.add_widget(sens_label)
        
        self.sensitivity_slider = Slider(
            min=0.3, max=1.0, 
            value=game_settings.get('control_sensitivity'),
            size_hint_y=0.4
        )
        self.sensitivity_slider.bind(value=self.change_sensitivity)
        sensitivity_layout.add_widget(self.sensitivity_slider)
        settings_layout.add_widget(sensitivity_layout)
        
        # Sound Setting
        sound_layout = BoxLayout(orientation='horizontal', size_hint_y=None, height=50)
        sound_label = Label(
            text='🔊 Sound Effects:', 
            font_size='22sp', 
            color=WHITE, 
            bold=True,
            size_hint_x=0.7
        )
        sound_layout.add_widget(sound_label)
        
        self.sound_switch = Switch(
            active=game_settings.get('sound_enabled'),
            size_hint_x=0.3
        )
        self.sound_switch.bind(active=self.toggle_sound)
        sound_layout.add_widget(self.sound_switch)
        settings_layout.add_widget(sound_layout)
        
        # Vibration Setting (for mobile)
        vibration_layout = BoxLayout(orientation='horizontal', size_hint_y=None, height=50)
        vibration_label = Label(
            text='📳 Vibration:', 
            font_size='22sp', 
            color=WHITE, 
            bold=True,
            size_hint_x=0.7
        )
        vibration_layout.add_widget(vibration_label)
        
        self.vibration_switch = Switch(
            active=game_settings.get('vibration_enabled'),
            size_hint_x=0.3
        )
        self.vibration_switch.bind(active=self.toggle_vibration)
        vibration_layout.add_widget(self.vibration_switch)
        settings_layout.add_widget(vibration_layout)
        
        main_layout.add_widget(settings_layout)
        
        # Control instructions
        instructions = Label(
            text='📋 Mobile Controls:\n• Swipe to move snake\n• Tap to pause/unpause\n• Adjust sensitivity below',
            font_size='16sp',
            color=(0.7, 0.7, 1, 1),
            text_size=(None, None),
            halign='center',
            size_hint_y=None,
            height=80
        )
        main_layout.add_widget(instructions)
        
        # Ad stats (shows revenue info)
        self.ad_stats = Label(
            text=ad_manager.get_stats_text(),
            font_size='14sp',
            color=(0.3, 1, 0.3, 1),
            size_hint_y=None,
            height=40
        )
        main_layout.add_widget(self.ad_stats)
        
        # Back button
        back_btn = SimpleButton(
            text='◀ BACK TO MENU',
            size_hint=(None, None),
            size=(250, 50),
            pos_hint={'center_x': 0.5}
        )
        back_btn.bind(on_press=self.go_back)
        main_layout.add_widget(back_btn)
        
        # Add banner ad at bottom (mobile-friendly)
        banner_ad = ad_manager.create_banner_ad()
        main_layout.add_widget(banner_ad)
        
        self.add_widget(main_layout)
        self.update_button_colors()
    
    def update_bg(self, *args):
        self.bg_rect.size = self.size
        self.bg_rect.pos = self.pos
    
    def set_difficulty(self, difficulty):
        game_settings.set('difficulty', difficulty)
        self.update_button_colors()
    
    def set_grid_size(self, size):
        game_settings.set('grid_size', size)
        self.update_button_colors()
    
    def toggle_touch_controls(self, instance, value):
        game_settings.set('touch_controls', value)
    
    def change_sensitivity(self, instance, value):
        game_settings.set('control_sensitivity', value)
    
    def toggle_sound(self, instance, value):
        game_settings.set('sound_enabled', value)
    
    def toggle_vibration(self, instance, value):
        game_settings.set('vibration_enabled', value)
    
    def update_button_colors(self):
        # Update difficulty buttons
        current_diff = game_settings.get('difficulty')
        for diff, btn in self.difficulty_buttons.items():
            if diff == current_diff:
                btn.background_color = (0.2, 0.8, 0.2, 1)  # Green for selected
            else:
                btn.background_color = (0.3, 0.3, 0.3, 1)  # Gray for unselected
        
        # Update grid size buttons
        current_grid = game_settings.get('grid_size')
        for size, btn in self.grid_buttons.items():
            if size == current_grid:
                btn.background_color = (0.2, 0.8, 0.2, 1)  # Green for selected
            else:
                btn.background_color = (0.3, 0.3, 0.3, 1)  # Gray for unselected
    
    def on_enter(self):
        """Update ad stats when entering settings"""
        if hasattr(self, 'ad_stats'):
            self.ad_stats.text = ad_manager.get_stats_text()
    
    def go_back(self, instance):
        self.manager.current = 'menu'

class GameScreen(Screen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        
        main_layout = BoxLayout(orientation='vertical')
        
        # HUD with beautiful styling
        hud_layout = BoxLayout(orientation='horizontal', size_hint_y=0.1)
        
        self.score_label = Label(
            text='Score: 0', 
            font_size='22sp', 
            color=(0.3, 1, 0.3, 1),  # Bright green
            bold=True
        )
        # Show both game level and difficulty
        difficulty_emoji = {'easy': '😊', 'medium': '😐', 'hard': '😤'}
        current_diff = game_settings.get('difficulty')
        
        self.level_label = Label(
            text=f'Level: 1 {difficulty_emoji.get(current_diff, "😐")}', 
            font_size='22sp', 
            color=(1, 1, 0.3, 1),  # Bright yellow
            bold=True
        )
        
        # Touch control indicator
        self.touch_indicator = Label(
            text='📱' if game_settings.get('touch_controls') else '',
            font_size='20sp',
            color=(0.3, 0.8, 1, 1),  # Bright blue
            size_hint_x=0.1
        )
        
        pause_btn = SimpleButton(
            text='PAUSE',
            size_hint=(0.2, 1)
        )
        pause_btn.bind(on_press=self.toggle_pause)
        
        hud_layout.add_widget(self.score_label)
        hud_layout.add_widget(self.level_label)
        hud_layout.add_widget(self.touch_indicator)
        hud_layout.add_widget(pause_btn)
        
        # Game Area
        self.game_widget = GameWidget()
        
        main_layout.add_widget(hud_layout)
        main_layout.add_widget(self.game_widget)
        
        self.add_widget(main_layout)
        
        # Keyboard bindings
        Window.bind(on_key_down=self.on_key_down)
        
    def on_enter(self):
        # Refresh game widget with current settings
        self.refresh_game_widget()
        self.game_widget.start_game()
        Clock.schedule_interval(self.update_game, 1/60)
    
    def refresh_game_widget(self):
        # Update grid size if settings changed
        grid_info = game_settings.get_grid_size_info()
        self.game_widget.grid_width = grid_info['width']
        self.game_widget.grid_height = grid_info['height']
        self.game_widget.cell_size = grid_info['cell_size']
        
        # Recreate snake and food with new dimensions
        self.game_widget.snake = Snake(
            self.game_widget.grid_width, 
            self.game_widget.grid_height, 
            self.game_widget.cell_size
        )
        self.game_widget.food = Food(
            self.game_widget.grid_width, 
            self.game_widget.grid_height
        )
        
        # Update touch controls
        if game_settings.get('touch_controls'):
            if not hasattr(self.game_widget, 'touch_start_pos'):
                self.game_widget.touch_start_pos = None
                self.game_widget.min_swipe_distance = 50
            self.game_widget.bind(on_touch_down=self.game_widget.on_touch_down)
            self.game_widget.bind(on_touch_up=self.game_widget.on_touch_up)
            self.touch_indicator.text = '📱'
        else:
            try:
                self.game_widget.unbind(on_touch_down=self.game_widget.on_touch_down)
                self.game_widget.unbind(on_touch_up=self.game_widget.on_touch_up)
            except:
                pass
            self.touch_indicator.text = ''
        
    def update_game(self, dt):
        if self.game_widget.game_over:
            self.show_game_over()
            return False
            
        # Update HUD with difficulty indicator
        difficulty_emoji = {'easy': '😊', 'medium': '😐', 'hard': '😤'}
        current_diff = game_settings.get('difficulty')
        
        self.score_label.text = f'Score: {self.game_widget.score}'
        self.level_label.text = f'Level: {self.game_widget.level} {difficulty_emoji.get(current_diff, "😐")}'
        
    def show_game_over(self):
        Clock.unschedule(self.update_game)
        
        # Show game over screen with revive option
        game_over_screen = self.manager.get_screen('game_over')
        game_over_screen.set_score(
            self.game_widget.score, 
            self.game_widget.level,
            self.game_widget.high_score
        )
        # Pass game widget reference for potential revive
        game_over_screen.game_widget = self.game_widget
        game_over_screen.game_screen = self
        self.manager.current = 'game_over'
        
    def toggle_pause(self, instance):
        self.game_widget.paused = not self.game_widget.paused
        
    def on_key_down(self, window, key, *args):
        if not self.game_widget.game_over and not self.game_widget.paused:
            # Arrow keys
            if key == 273:  # Up
                self.game_widget.snake.change_direction((0, 1))
            elif key == 274:  # Down
                self.game_widget.snake.change_direction((0, -1))
            elif key == 275:  # Right
                self.game_widget.snake.change_direction((1, 0))
            elif key == 276:  # Left
                self.game_widget.snake.change_direction((-1, 0))
            # WASD
            elif key == 119:  # W
                self.game_widget.snake.change_direction((0, 1))
            elif key == 115:  # S
                self.game_widget.snake.change_direction((0, -1))
            elif key == 100:  # D
                self.game_widget.snake.change_direction((1, 0))
            elif key == 97:   # A
                self.game_widget.snake.change_direction((-1, 0))
                
        # Pause (Space)
        if key == 32:
            self.toggle_pause(None)

class GameOverScreen(Screen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        
        layout = FloatLayout()
        
        # Add beautiful background matching the game
        with self.canvas.before:
            Color(0.05, 0.05, 0.15, 1)  # Dark blue background
            self.bg_rect = Rectangle(pos=self.pos, size=self.size)
            
            # Add pattern
            Color(0.1, 0.1, 0.2, 0.2)
            for i in range(0, 800, 60):
                for j in range(0, 600, 60):
                    if (i // 60 + j // 60) % 2 == 0:
                        Rectangle(pos=(i, j), size=(30, 30))
        
        self.bind(size=self.update_bg, pos=self.update_bg)
        
        # Game Over Title
        title = Label(
            text='GAME OVER',
            font_size='48sp',
            bold=True,
            color=(1, 0.3, 0.3, 1),  # Bright red
            pos_hint={'center_x': 0.5, 'center_y': 0.8}
        )
        layout.add_widget(title)
        
        # Score Labels with bright colors
        self.score_label = Label(
            text='Score: 0',
            font_size='26sp',
            color=(0.3, 1, 0.3, 1),  # Bright green
            bold=True,
            pos_hint={'center_x': 0.5, 'center_y': 0.65}
        )
        layout.add_widget(self.score_label)
        
        self.level_label = Label(
            text='Level: 1',
            font_size='26sp',
            color=(1, 1, 0.3, 1),  # Bright yellow
            bold=True,
            pos_hint={'center_x': 0.5, 'center_y': 0.6}
        )
        layout.add_widget(self.level_label)
        
        self.high_score_label = Label(
            text='High Score: 0',
            font_size='26sp',
            color=(1, 0.8, 0.3, 1),  # Bright orange
            bold=True,
            pos_hint={'center_x': 0.5, 'center_y': 0.55}
        )
        layout.add_widget(self.high_score_label)
        
        # Performance message
        self.performance_label = Label(
            text='',
            font_size='22sp',
            color=(0.3, 1, 0.8, 1),  # Bright cyan
            bold=True,
            pos_hint={'center_x': 0.5, 'center_y': 0.45}
        )
        layout.add_widget(self.performance_label)
        
        # Buttons
        # Watch Ad to Revive Button
        revive_btn = SimpleButton(
            text='WATCH AD TO REVIVE',
            pos_hint={'center_x': 0.5, 'center_y': 0.35}
        )
        revive_btn.bind(on_press=self.watch_ad_revive)
        layout.add_widget(revive_btn)
        
        play_again_btn = SimpleButton(
            text='PLAY AGAIN',
            pos_hint={'center_x': 0.5, 'center_y': 0.25}
        )
        play_again_btn.bind(on_press=self.play_again)
        layout.add_widget(play_again_btn)
        
        menu_btn = SimpleButton(
            text='MAIN MENU',
            pos_hint={'center_x': 0.5, 'center_y': 0.15}
        )
        menu_btn.bind(on_press=self.go_menu)
        layout.add_widget(menu_btn)
        
        # Add banner ad at bottom (mobile-friendly)
        banner_ad = ad_manager.create_banner_ad()
        layout.add_widget(banner_ad)
        
        self.add_widget(layout)
        
        # Initialize game references
        self.game_widget = None
        self.game_screen = None
    
    def update_bg(self, *args):
        self.bg_rect.size = self.size
        self.bg_rect.pos = self.pos
        
    def on_enter(self):
        """Show regular ad when entering game over screen"""
        def after_regular_ad(is_revive=False):
            pass  # Just continue to game over screen
        
        # Show regular game over ad
        ad_manager.show_game_over_ad(after_regular_ad)
        
    def watch_ad_revive(self, instance):
        """Watch ad to revive the game"""
        def after_revive_ad(is_revive=False):
            if is_revive and self.game_widget and self.game_screen:
                # Revive the game at death position!
                self.game_widget.game_over = False
                self.game_widget.paused = False
                
                # Keep snake at death position but move it slightly to avoid immediate collision
                if self.game_widget.snake.body:
                    head = self.game_widget.snake.body[0]
                    # Move snake back one step to avoid collision
                    direction = self.game_widget.snake.direction
                    new_head = (head[0] - direction[0], head[1] - direction[1])
                    
                    # Make sure new position is valid
                    if (0 <= new_head[0] < self.game_widget.grid_width and 
                        0 <= new_head[1] < self.game_widget.grid_height):
                        self.game_widget.snake.body[0] = new_head
                    else:
                        # If can't move back, just move to center
                center_x = self.game_widget.grid_width // 2
                center_y = self.game_widget.grid_height // 2
                self.game_widget.snake.body[0] = (center_x, center_y)
                
                # Go back to game and continue playing
                self.manager.current = 'game'
                # Resume game loop
                Clock.schedule_interval(self.game_screen.update_game, 1/60)
        
        # Show rewarded ad for revive
        ad_manager.show_rewarded_ad(after_revive_ad)
        
    def set_score(self, score, level, high_score):
        self.score_label.text = f'Final Score: {score}'
        self.level_label.text = f'Level Reached: {level}'
        self.high_score_label.text = f'High Score: {high_score}'
        
        # Performance message
        if score >= 200:
            message = "AMAZING! Snake Master!"
        elif score >= 100:
            message = "Great job! Keep it up!"
        elif score >= 50:
            message = "Good effort! Try again!"
        else:
            message = "Keep practicing!"
            
        self.performance_label.text = message
        
        # Update menu high score
        menu_screen = self.manager.get_screen('menu')
        menu_screen.update_high_score(high_score)
        
    def play_again(self, instance):
        self.manager.current = 'game'
        
    def go_menu(self, instance):
        self.manager.current = 'menu'

class SnakeApp(App):
    def build(self):
        Window.clearcolor = BLACK
        
        sm = ScreenManager()
        sm.add_widget(MenuScreen(name='menu'))
        sm.add_widget(SettingsScreen(name='settings'))
        sm.add_widget(GameScreen(name='game'))
        sm.add_widget(GameOverScreen(name='game_over'))
        
        return sm

if __name__ == '__main__':
    SnakeApp().run() 