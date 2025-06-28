#!/usr/bin/env python3
"""
Snake Game with Google AdMob Integration
Main entry point for APK
"""

# Import and run the full snake game
if __name__ == '__main__':
    try:
        from snake_game import SnakeApp
        SnakeApp().run()
    except Exception as e:
        print(f"Error loading snake_game: {e}")
        # Fallback simple app
        import kivy
        from kivy.app import App
        from kivy.uix.label import Label
        
        class FallbackApp(App):
            def build(self):
                return Label(text='Snake Game\nLoading...', font_size='24sp')
        
        FallbackApp().run() 