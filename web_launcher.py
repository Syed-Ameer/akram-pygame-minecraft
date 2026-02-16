# PyCraft Web Launcher - PERFECT EDITION
# Full-featured launcher with memes, voting, bug reports, DLC, and perfectness!

import asyncio
import pygame
import json
import sys
from datetime import datetime
from pathlib import Path

# Initialize Pygame
pygame.init()

# Screen settings
SCREEN_WIDTH = 1400
SCREEN_HEIGHT = 900
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
pygame.display.set_caption("⛏️ PyCraft Launcher - Perfect Edition 🎮")

# Colors
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
GRAY = (100, 100, 100)
LIGHT_GRAY = (200, 200, 200)
DARK_GRAY = (40, 40, 40)
DARKER_GRAY = (20, 20, 20)
GREEN = (46, 139, 87)
BRIGHT_GREEN = (0, 255, 127)
BLUE = (100, 149, 237)
DARK_BLUE = (25, 25, 112)
RED = (220, 53, 69)
ORANGE = (255, 140, 0)
PURPLE = (138, 43, 226)
GOLD = (255, 215, 0)
PINK = (255, 105, 180)

# Fonts
try:
    title_font = pygame.font.Font(None, 72)
    heading_font = pygame.font.Font(None, 52)
    large_font = pygame.font.Font(None, 40)
    normal_font = pygame.font.Font(None, 32)
    small_font = pygame.font.Font(None, 24)
    tiny_font = pygame.font.Font(None, 20)
except:
    title_font = pygame.font.SysFont('Arial', 72, bold=True)
    heading_font = pygame.font.SysFont('Arial', 52, bold=True)
    large_font = pygame.font.SysFont('Arial', 40)
    normal_font = pygame.font.SysFont('Arial', 32)
    small_font = pygame.font.SysFont('Arial', 24)
    tiny_font = pygame.font.SysFont('Arial', 20)

clock = pygame.time.Clock()

# Game State
current_screen = "login"
logged_in = False
current_user = None
selected_version = 0
dlc_enabled = True
scroll_offset = 0
animation_frame = 0

# Data Storage (simulated localStorage)
accounts = {}
votes = {"cats": 0, "farms": 0, "mangrove": 0, "structures": 0, "voters": []}
bugs = []
meme_likes = 0
meme_voters = []

# Game Versions
game_versions = [
    "🏰 Pre-Classic",
    "🟫 Classic 1 - Beginning", "🟫 Classic 2 - Survival", 
    "🟫 Classic 3 - Multiplayer", "🟫 Classic 4 - Creative",
    "🟫 Classic 5 - Mobs", "🟫 Classic 6 - World", "🟫 Classic 7 - Complete",
    "🏠 Indev 1 - Basics", "🏠 Indev 2 - Building",
    "🏠 Indev 3 - Caves", "🏠 Indev 4 - Redstone",
    "🏠 Indev 5 - Farming", "🏠 Indev 6 - Combat", "🏠 Indev 7 - Dimensions",
    "⚡ Alpha 1", "⚡ Alpha 2",
    "🌍 Alpha 3 Overworld", "🌍 Alpha 4 Overworld", "🌍 Alpha v1.0 Overworld",
    "🔮 Alpha 4 End", "🔮 Alpha v1.0 End",
    "🔥 Alpha 4 Nether", "🔥 Alpha v1.0 Nether",
    "📱 Bedrock Mobile Edition",
    "🧪 Experimental Features"
]

# Meme content (text-based for now)
current_meme = {
    "title": "When you find diamonds in Minecraft:",
    "text": "😱 *Happy mining noises*\n\n💎💎💎\n\n[Insert epic meme image here]",
    "caption": "Every miner's dream! 💙"
}

# UI Classes
class Button:
    def __init__(self, x, y, width, height, text, color=BLUE, text_color=WHITE, icon=""):
        self.rect = pygame.Rect(x, y, width, height)
        self.text = text
        self.color = color
        self.text_color = text_color
        self.icon = icon
        self.hovered = False
        self.pulse = 0
    
    def draw(self, surface):
        # Pulse animation for hovered buttons
        offset = int(self.pulse * 5)
        color = tuple(min(c + 40 + offset, 255) for c in self.color) if self.hovered else self.color
        
        # Draw shadow
        shadow_rect = self.rect.copy()
        shadow_rect.y += 4
        pygame.draw.rect(surface, BLACK, shadow_rect, border_radius=12)
        
        # Draw button
        pygame.draw.rect(surface, color, self.rect, border_radius=12)
        pygame.draw.rect(surface, WHITE, self.rect, 3, border_radius=12)
        
        # Draw text with icon
        full_text = f"{self.icon} {self.text}" if self.icon else self.text
        text_surf = normal_font.render(full_text, True, self.text_color)
        text_rect = text_surf.get_rect(center=self.rect.center)
        surface.blit(text_surf, text_rect)
        
        # Update pulse animation
        if self.hovered:
            self.pulse = (self.pulse + 0.1) % 1
    
    def handle_event(self, event):
        if event.type == pygame.MOUSEMOTION:
            self.hovered = self.rect.collidepoint(event.pos)
        elif event.type == pygame.MOUSEBUTTONDOWN:
            if self.rect.collidepoint(event.pos):
                return True
        return False

class TextBox:
    def __init__(self, x, y, width, height, placeholder="", password=False):
        self.rect = pygame.Rect(x, y, width, height)
        self.text = ""
        self.placeholder = placeholder
        self.active = False
        self.password = password
    
    def draw(self, surface):
        color = BRIGHT_GREEN if self.active else GRAY
        
        # Draw background
        pygame.draw.rect(surface, WHITE, self.rect, border_radius=8)
        pygame.draw.rect(surface, color, self.rect, 3, border_radius=8)
        
        # Draw text
        display_text = self.text if self.text else self.placeholder
        if self.password and self.text:
            display_text = "*" * len(self.text)
        
        text_color = BLACK if self.text else GRAY
        text_surf = normal_font.render(display_text, True, text_color)
        
        # Add cursor if active
        if self.active:
            cursor_text = display_text + "|"
            text_surf = normal_font.render(cursor_text, True, text_color)
        
        surface.blit(text_surf, (self.rect.x + 15, self.rect.y + 12))
    
    def handle_event(self, event):
        if event.type == pygame.MOUSEBUTTONDOWN:
            self.active = self.rect.collidepoint(event.pos)
        elif event.type == pygame.KEYDOWN and self.active:
            if event.key == pygame.K_BACKSPACE:
                self.text = self.text[:-1]
            elif event.key == pygame.K_RETURN:
                return "submit"
            elif event.key == pygame.K_TAB:
                return "tab"
            elif len(self.text) < 25:
                self.text += event.unicode
        return None

class ProgressBar:
    def __init__(self, x, y, width, height, value, max_value, color=BLUE):
        self.rect = pygame.Rect(x, y, width, height)
        self.value = value
        self.max_value = max_value
        self.color = color
    
    def draw(self, surface):
        # Background
        pygame.draw.rect(surface, GRAY, self.rect, border_radius=5)
        
        # Progress
        if self.max_value > 0:
            progress_width = int((self.value / self.max_value) * self.rect.width)
            progress_rect = pygame.Rect(self.rect.x, self.rect.y, progress_width, self.rect.height)
            pygame.draw.rect(surface, self.color, progress_rect, border_radius=5)
        
        # Border
        pygame.draw.rect(surface, WHITE, self.rect, 2, border_radius=5)
        
        # Percentage text
        if self.max_value > 0:
            percentage = (self.value / self.max_value) * 100
            text = small_font.render(f"{percentage:.1f}%", True, WHITE)
            text_rect = text.get_rect(center=self.rect.center)
            surface.blit(text, text_rect)

# Initialize UI Elements
login_username = TextBox(SCREEN_WIDTH // 2 - 250, 300, 500, 60, "Enter username")
login_button = Button(SCREEN_WIDTH // 2 - 200, 400, 400, 70, "LOGIN", GREEN, icon="✓")
create_button = Button(SCREEN_WIDTH // 2 - 200, 490, 400, 70, "CREATE ACCOUNT", ORANGE, icon="➕")

# Main screen buttons
play_button = Button(SCREEN_WIDTH // 2 - 250, 200, 500, 90, "PLAY NOW", BRIGHT_GREEN, icon="🚀")
version_left = Button(150, 320, 60, 50, "<", BLUE)
version_right = Button(SCREEN_WIDTH - 210, 320, 60, 50, ">", BLUE)
dlc_toggle = Button(SCREEN_WIDTH // 2 - 150, 750, 300, 60, "AKRAM DLC: ON", PURPLE, icon="🔥")

# Vote buttons
vote_buttons = [
    Button(50, 520, 310, 70, "Cats & Mods", PINK, icon="🐱"),
    Button(380, 520, 310, 70, "Farms & Fixes", ORANGE, icon="🌾"),
    Button(710, 520, 310, 70, "Mangrove Update", GREEN, icon="🌳"),
    Button(1040, 520, 310, 70, "Structures & Villages", BLUE, icon="🏰")
]

# Meme interaction
meme_like_button = Button(SCREEN_WIDTH // 2 - 100, 670, 200, 50, "👍 LIKE MEME", PINK)

# Bug report button
bug_report_button = Button(50, SCREEN_HEIGHT - 80, 250, 60, "Report Bug", RED, icon="🐛")
back_button = Button(SCREEN_WIDTH - 200, SCREEN_HEIGHT - 80, 150, 60, "Back", GRAY, icon="←")

# Helper Functions
def draw_text(surface, text, font, color, x, y, center=False):
    text_surf = font.render(text, True, color)
    if center:
        text_rect = text_surf.get_rect(center=(x, y))
        surface.blit(text_surf, text_rect)
    else:
        surface.blit(text_surf, (x, y))

def draw_multiline(surface, text, font, color, x, y, max_width):
    lines = text.split('\n')
    y_offset = y
    for line in lines:
        words = line.split(' ')
        current_line = []
        for word in words:
            test_line = ' '.join(current_line + [word])
            if font.size(test_line)[0] <= max_width:
                current_line.append(word)
            else:
                if current_line:
                    draw_text(surface, ' '.join(current_line), font, color, x, y_offset)
                    y_offset += font.get_height() + 5
                current_line = [word]
        if current_line:
            draw_text(surface, ' '.join(current_line), font, color, x, y_offset)
            y_offset += font.get_height() + 5

def save_data():
    """Save all data to file (localStorage simulation)"""
    try:
        data = {
            "accounts": accounts,
            "votes": votes,
            "bugs": bugs,
            "meme_likes": meme_likes,
            "meme_voters": meme_voters
        }
        with open("launcher_data.json", "w") as f:
            json.dump(data, f, indent=2)
    except Exception as e:
        print(f"Save error: {e}")

def load_data():
    """Load data from file"""
    global accounts, votes, bugs, meme_likes, meme_voters
    try:
        with open("launcher_data.json", "r") as f:
            data = json.load(f)
            accounts = data.get("accounts", {})
            votes = data.get("votes", {"cats": 0, "farms": 0, "mangrove": 0, "structures": 0, "voters": []})
            bugs = data.get("bugs", [])
            meme_likes = data.get("meme_likes", 0)
            meme_voters = data.get("meme_voters", [])
    except:
        pass

def draw_particle_effect(surface, x, y, color):
    """Draw decorative particles"""
    global animation_frame
    for i in range(5):
        offset_x = int(30 * pygame.math.Vector2(1, 0).rotate(animation_frame * 5 + i * 72).x)
        offset_y = int(30 * pygame.math.Vector2(1, 0).rotate(animation_frame * 5 + i * 72).y)
        pygame.draw.circle(surface, color, (x + offset_x, y + offset_y), 5)

# Screen Drawing Functions
def draw_login_screen():
    """Draw gorgeous login screen"""
    # Gradient background
    for y in range(SCREEN_HEIGHT):
        color_ratio = y / SCREEN_HEIGHT
        color = (
            int(DARK_BLUE[0] + (DARKER_GRAY[0] - DARK_BLUE[0]) * color_ratio),
            int(DARK_BLUE[1] + (DARKER_GRAY[1] - DARK_BLUE[1]) * color_ratio),
            int(DARK_BLUE[2] + (DARKER_GRAY[2] - DARK_BLUE[2]) * color_ratio)
        )
        pygame.draw.line(screen, color, (0, y), (SCREEN_WIDTH, y))
    
    # Animated particles
    draw_particle_effect(screen, SCREEN_WIDTH // 2, 150, GOLD)
    
    # Title
    draw_text(screen, "⛏️ PyCraft Launcher ⛏️", title_font, GOLD, SCREEN_WIDTH // 2, 120, center=True)
    draw_text(screen, "Perfect Web Edition", large_font, WHITE, SCREEN_WIDTH // 2, 200, center=True)
    draw_text(screen, "━━━━━━━━━━━━━━━━━━━━━━━━", normal_font, GOLD, SCREEN_WIDTH // 2, 240, center=True)
    
    # Login elements
    login_username.draw(screen)
    login_button.draw(screen)
    create_button.draw(screen)
    
    # Info
    info_text = f"✨ {len(accounts)} adventurers have joined! ✨"
    draw_text(screen, info_text, normal_font, LIGHT_GRAY, SCREEN_WIDTH // 2, 590, center=True)
    
    # Features list
    features = [
        "🎮 25,000+ Lines of Code",
        "🌍 Full Minecraft Mechanics",
        "🔥 Custom Akram DLC",
        "👥 Multiplayer Support",
        "😂 Memes & Community Polls"
    ]
    y_offset = 650
    for feature in features:
        draw_text(screen, feature, small_font, LIGHT_GRAY, SCREEN_WIDTH // 2, y_offset, center=True)
        y_offset += 35

def draw_main_screen():
    """Draw perfect main launcher screen"""
    global animation_frame
    
    # Background
    screen.fill(DARK_GRAY)
    
    # Header bar  
    pygame.draw.rect(screen, DARKER_GRAY, (0, 0, SCREEN_WIDTH, 100))
    pygame.draw.line(screen, GOLD, (0, 100), (SCREEN_WIDTH, 100), 3)
    
    draw_text(screen, "⛏️ PyCraft Launcher", heading_font, GOLD, 30, 25)
    draw_text(screen, f"👤 {current_user}", normal_font, WHITE, SCREEN_WIDTH - 250, 40)
    
    # Play section
    draw_text(screen, "🎮 QUICK PLAY", large_font, WHITE, 50, 130)
    
    # Version display
    version_text = game_versions[selected_version]
    version_bg = pygame.Rect(220, 310, SCREEN_WIDTH - 440, 70)
    pygame.draw.rect(screen, DARKER_GRAY, version_bg, border_radius=10)
    pygame.draw.rect(screen, GOLD, version_bg, 3, border_radius=10)
    draw_text(screen, version_text, large_font, WHITE, SCREEN_WIDTH // 2, 345, center=True)
    
    version_left.draw(screen)
    version_right.draw(screen)
    play_button.draw(screen)
    
    # DLC Section
    draw_text(screen, "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━", tiny_font, GRAY, SCREEN_WIDTH // 2, 420, center=True)
    
    dlc_label = "🔥 AKRAM DLC STATUS: " + ("✅ ENABLED" if dlc_enabled else "❌ DISABLED")
    color = BRIGHT_GREEN if dlc_enabled else RED
    draw_text(screen, dlc_label, large_font, color, SCREEN_WIDTH // 2, 450, center=True)
    
    if dlc_enabled:
        features = "Custom Animals 🦌 | Enhanced Textures 🎨 | Ocean Life 🐠 | Unique Items 🏺"
        draw_text(screen, features, small_font, LIGHT_GRAY, SCREEN_WIDTH // 2, 490, center=True)
    
    dlc_toggle.text = "AKRAM DLC: ON" if dlc_enabled else "AKRAM DLC: OFF"
    dlc_toggle.color = PURPLE if dlc_enabled else GRAY
    dlc_toggle.draw(screen)
    
    # Voting Section
    draw_text(screen, "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━", tiny_font, GRAY, SCREEN_WIDTH // 2, 530, center=True)
    draw_text(screen, "📊 VOTE FOR NEXT UPDATE!", heading_font, GOLD, SCREEN_WIDTH // 2, 560, center=True)
    
    has_voted = current_user in votes.get("voters", [])
    
    if has_voted:
        draw_text(screen, "✅ Thanks for voting! Current results:", normal_font, BRIGHT_GREEN, SCREEN_WIDTH // 2, 600, center=True)
        
        # Calculate votes
        total_votes = votes["cats"] + votes["farms"] + votes["mangrove"] + votes["structures"]
        
        if total_votes > 0:
            vote_data = [
                ("🐱 Cats & Mods", votes["cats"], PINK),
                ("🌾 Farms & Fixes", votes["farms"], ORANGE),
                ("🌳 Mangrove Update", votes["mangrove"], GREEN),
                ("🏰 Structures & Villages", votes["structures"], BLUE)
            ]
            
            y_pos = 640
            for name, count, color in vote_data:
                pct = (count / total_votes) * 100
                bar = ProgressBar(380, y_pos, 640, 30, count, total_votes, color)
                bar.draw(screen)
                draw_text(screen, name, small_font, WHITE, 50, y_pos + 5)
                draw_text(screen, f"{count} votes", small_font, LIGHT_GRAY, 1050, y_pos + 5)
                y_pos += 50
    else:
        draw_text(screen, "Vote for what you want to see next:", normal_font, WHITE, SCREEN_WIDTH // 2, 600, center=True)
        for button in vote_buttons:
            button.draw(screen)
    
    # Meme Section
    draw_text(screen, "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━", tiny_font, GRAY, SCREEN_WIDTH // 2, 770, center=True)
    draw_text(screen, "😂 MEME OF THE MONTH 😂", heading_font, PINK, SCREEN_WIDTH // 2, 800, center=True)
    
    # Draw meme box (simplified for web)
    meme_box = pygame.Rect(SCREEN_WIDTH // 2 - 300, 840, 600, 120)
    pygame.draw.rect(screen, DARKER_GRAY, meme_box, border_radius=15)
    pygame.draw.rect(screen, PINK, meme_box, 3, border_radius=15)
    
    draw_text(screen, current_meme["title"], normal_font, WHITE, SCREEN_WIDTH // 2, 870, center=True)
    draw_text(screen, "💎 *Happy mining noises* 💎", small_font, GOLD, SCREEN_WIDTH // 2, 910, center=True)
    draw_text(screen, f"👍 {meme_likes} likes", small_font, LIGHT_GRAY, SCREEN_WIDTH // 2, 940, center=True)
    
    # Meme like button (if not voted)
    if current_user not in meme_voters:
        meme_like_button.rect.y = 980
        meme_like_button.draw(screen)
    else:
        draw_text(screen, "✅ You liked this meme!", small_font, BRIGHT_GREEN, SCREEN_WIDTH // 2, 995, center=True)
    
    # Bug report button
    bug_report_button.draw(screen)
    
    # Footer
    footer_text = "🌐 Browser Edition | 25,000+ Lines | Full Mechanics | Multiplayer Ready"
    draw_text(screen, footer_text, tiny_font, LIGHT_GRAY, SCREEN_WIDTH // 2, SCREEN_HEIGHT - 25, center=True)

async def main():
    """Main launcher loop"""
    global current_screen, logged_in, current_user, selected_version, dlc_enabled, animation_frame, meme_likes
    
    load_data()
    running = True
    
    while running:
        animation_frame += 1
        
        # Clear screen with background color
        screen.fill(DARKER_GRAY)
        
        # Event handling
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                save_data()
                running = False
            
            if current_screen == "login":
                result = login_username.handle_event(event)
                
                if result == "submit" or login_button.handle_event(event):
                    username = login_username.text.strip()
                    if len(username) >= 3:
                        current_user = username
                        if username not in accounts:
                            accounts[username] = {
                                "created": datetime.now().isoformat(),
                                "play_count": 0
                            }
                        accounts[username]["last_login"] = datetime.now().isoformat()
                        logged_in = True
                        current_screen = "main"
                        save_data()
                
                if create_button.handle_event(event):
                    username = login_username.text.strip()
                    if len(username) >= 3:
                        if username not in accounts:
                            accounts[username] = {
                                "created": datetime.now().isoformat(),
                                "play_count": 0,
                                "last_login": datetime.now().isoformat()
                            }
                            current_user = username
                            logged_in = True
                            current_screen = "main"
                            save_data()
            
            elif current_screen == "main":
                if play_button.handle_event(event):
                    print(f"🎮 Launching: {game_versions[selected_version]}")
                    print("⚠️ Note: Full game requires download")
                    print("🌐 This is the perfect launcher demo!")
                    accounts[current_user]["play_count"] = accounts[current_user].get("play_count", 0) + 1
                    save_data()
                
                if version_left.handle_event(event):
                    selected_version = (selected_version - 1) % len(game_versions)
                
                if version_right.handle_event(event):
                    selected_version = (selected_version + 1) % len(game_versions)
                
                if dlc_toggle.handle_event(event):
                    dlc_enabled = not dlc_enabled
                    save_data()
                
                # Voting
                if current_user not in votes.get("voters", []):
                    if vote_buttons[0].handle_event(event):
                        votes["cats"] += 1
                        votes.setdefault("voters", []).append(current_user)
                        save_data()
                    elif vote_buttons[1].handle_event(event):
                        votes["farms"] += 1
                        votes.setdefault("voters", []).append(current_user)
                        save_data()
                    elif vote_buttons[2].handle_event(event):
                        votes["mangrove"] += 1
                        votes.setdefault("voters", []).append(current_user)
                        save_data()
                    elif vote_buttons[3].handle_event(event):
                        votes["structures"] += 1
                        votes.setdefault("voters", []).append(current_user)
                        save_data()
                
                # Meme likes
                if current_user not in meme_voters:
                    if meme_like_button.handle_event(event):
                        meme_likes += 1
                        meme_voters.append(current_user)
                        save_data()
                
                if bug_report_button.handle_event(event):
                    print("🐛 Bug Report System")
                    print("📧 Report bugs at: github.com/Syed-Ameer/akram-pygame-minecraft")
                
                # Keyboard shortcuts
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_LEFT:
                        selected_version = (selected_version - 1) % len(game_versions)
                    elif event.key == pygame.K_RIGHT:
                        selected_version = (selected_version + 1) % len(game_versions)
                    elif event.key == pygame.K_RETURN or event.key == pygame.K_SPACE:
                        print(f"🎮 Quick Launch: {game_versions[selected_version]}")
                    elif event.key == pygame.K_d:
                        dlc_enabled = not dlc_enabled
        
        # Draw appropriate screen
        if current_screen == "login":
            draw_login_screen()
        elif current_screen == "main":
            draw_main_screen()
        
        # Update display
        pygame.display.flip()
        clock.tick(60)
        
        # REQUIRED: Yield to browser
        await asyncio.sleep(0)
    
    pygame.quit()
    sys.exit()

# Launch the perfect launcher!
if __name__ == "__main__":
    asyncio.run(main())
