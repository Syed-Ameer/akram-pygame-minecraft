# Ursina 3D Minecraft-like Game with Multiplayer
# Complete playable 3D game with networking support

import socket
import threading
import json
import time
import random
import os
from typing import Dict, List, Tuple

try:
    from ursina import (
        Ursina, camera, DirectionalLight, Vec3, Entity, color, 
        Text, mouse, curve, window, scene, Sky,
        Button, time as ursina_time, destroy, held_keys, application
    )
    
    # Optional imports that may not be available in all versions
    try:
        from ursina import Audio, Panel, TextField, Mesh, Material, Texture, load_texture
    except ImportError:
        # Create dummy classes for missing imports
        class Audio: pass
        class Panel: pass  
        class TextField: pass
        class Mesh: pass
        class Material: pass
        class Texture: pass
        def load_texture(path): return None
    
    # Try to import FirstPersonController
    try:
        from ursina.prefabs.first_person_controller import FirstPersonController
    except ImportError:
        # Create basic first person controller if not available
        class FirstPersonController(Entity):
            def __init__(self, **kwargs):
                super().__init__(**kwargs)
                self.speed = 5
                self.mouse_sensitivity = Vec3(40, 40, 40)
                camera.parent = self
                camera.position = (0, 2, 0)
                camera.rotation = (0, 0, 0)
                self.cursor = Entity(parent=camera.ui, model='cube', color=color.pink, scale=.008, rotation_z=45)
                mouse.locked = True
                
            def update(self):
                self.rotation_y += mouse.velocity[0] * self.mouse_sensitivity[1]
                camera.rotation_x -= mouse.velocity[1] * self.mouse_sensitivity[0]
                camera.rotation_x = max(-90, min(90, camera.rotation_x))
                
                direction = Vec3()
                if held_keys['w']: direction += Vec3(0,0,1)
                if held_keys['s']: direction += Vec3(0,0,-1)
                if held_keys['a']: direction += Vec3(-1,0,0)
                if held_keys['d']: direction += Vec3(1,0,0)
                if held_keys['space']: direction += Vec3(0,1,0)
                if held_keys['shift']: direction += Vec3(0,-1,0)
                
                if direction.length() > 0:
                    direction = direction.normalized()
                    self.position += direction * self.speed * ursina_time.dt
    
    URSINA_AVAILABLE = True
    print("🎮 Ursina 3D engine available for Minecraft-like game!")
except ImportError as e:
    URSINA_AVAILABLE = False
    print(f"⚠️ Ursina not installed - 3D game will not work: {e}")
    print("📦 Install Ursina with: pip install ursina")
    # Create dummy objects to prevent NameErrors
    class DummyUrsina:
        def __init__(self): pass
        def run(self): pass
        def quit(self): pass
        input = None
    
    class DummyObject:
        def __init__(self, *args, **kwargs): pass
        def __getattr__(self, name): return DummyObject()
        def __call__(self, *args, **kwargs): return DummyObject()
        def animate_color(self, *args, **kwargs): pass
        text = ""
        color = None
        visible = True
        position = (0, 0, 0)
        rotation_x = 0
        hovered_entity = None
        tag = None
        slot_id = 0
    
    # Create dummy classes
    Ursina = DummyUrsina
    camera = DummyObject()
    DirectionalLight = DummyObject
    Vec3 = lambda *args: DummyObject()
    Entity = DummyObject
    color = DummyObject()
    Text = DummyObject
    mouse = DummyObject()
    curve = DummyObject()
    window = DummyObject()


class Minecraft3DGame:
    """Complete 3D Minecraft-like game with multiplayer support"""
    def __init__(self, player_inventory=None, player_hotbar=None):
        self.player_inventory = player_inventory.copy() if player_inventory else []
        self.player_hotbar = player_hotbar.copy() if player_hotbar else []
        
        # Game state
        self.app = None
        self.player = None
        self.world_blocks = {}
        self.other_players = {}
        
        # Block types
        self.block_types = {
            1: {'color': color.green, 'name': 'Grass'},
            2: {'color': color.brown, 'name': 'Dirt'},
            3: {'color': color.gray, 'name': 'Stone'},
            4: {'color': color.orange, 'name': 'Wood'},  # Using orange instead of wood
            5: {'color': color.blue, 'name': 'Water'},
            6: {'color': color.yellow, 'name': 'Sand'}
        }
        
        # Selected block type
        self.selected_block = 1
        
        # Multiplayer components
        self.is_multiplayer = False
        self.is_server = False
        self.server_socket = None
        self.client_socket = None
        self.server_thread = None
        self.client_thread = None
        self.connected_clients = {}
        self.player_id = f"player_{random.randint(1000, 9999)}"
        
        # UI components
        self.menu_state = 'main'  # main, singleplayer, multiplayer, hosting
        self.ui_elements = []
        
        # Game settings
        self.world_size = 50
        self.render_distance = 20
        
    def launch_game(self):
        """Launch the 3D Minecraft-like game"""
        if not URSINA_AVAILABLE:
            print("❌ Ursina not available - cannot launch 3D game")
            return False
            
        print("🎮 Launching 3D Minecraft Game...")
        try:
            # Initialize Ursina app
            self.app = Ursina(title="Minecraft 3D - Multiplayer Edition")
            window.borderless = False
            window.fullscreen = False
            window.color = color.cyan
            
            # Set up the main menu first
            self.setup_main_menu()
            
            # Input handling
            self.setup_input()
            
            # Run the game
            self.app.run()
            
            return True
        except Exception as e:
            print(f"❌ Failed to launch 3D game: {e}")
            return False
    
    def setup_main_menu(self):
        """Set up the main menu"""
        try:
            # Sky background
            Sky()
            
            # Clear any existing UI
            self.clear_ui()
            
            # Title
            title = Text('Minecraft 3D - Multiplayer Edition', position=(0, 0.3), scale=3, color=color.white, origin=(0, 0))
            self.ui_elements.append(title)
            
            # Menu buttons
            singleplayer_btn = Button('Singleplayer', position=(-0.2, 0.1), scale=(0.3, 0.08), color=color.green)
            singleplayer_btn.on_click = self.start_singleplayer
            self.ui_elements.append(singleplayer_btn)
            
            multiplayer_btn = Button('Multiplayer', position=(0.2, 0.1), scale=(0.3, 0.08), color=color.blue)
            multiplayer_btn.on_click = self.show_multiplayer_menu
            self.ui_elements.append(multiplayer_btn)
            
            quit_btn = Button('Quit', position=(0, -0.1), scale=(0.3, 0.08), color=color.red)
            quit_btn.on_click = self.quit_game
            self.ui_elements.append(quit_btn)
            
            # Instructions
            instructions = Text('WASD: Move, Mouse: Look, Left Click: Break, Right Click: Place\nNumbers: Select Block Type, ESC: Menu', 
                              position=(0, -0.3), scale=1.5, color=color.gray, origin=(0, 0))
            self.ui_elements.append(instructions)
            
            self.menu_state = 'main'
            
        except Exception as e:
            print(f"❌ Failed to setup main menu: {e}")
    
    def setup_game_world(self):
        """Set up the 3D game world"""
        try:
            # Clear menu
            self.clear_ui()
            
            # Player controller
            self.player = FirstPersonController()
            self.player.cursor.color = color.red
            self.player.position = (0, 10, 0)
            
            # Camera setup
            camera.fov = 90
            
            # Lighting
            sun = DirectionalLight()
            sun.look_at(Vec3(1, -1, -1))
            
            # Sky
            Sky()
            
            # Generate terrain
            self.generate_terrain()
            
            # Game UI
            self.create_game_ui()
            
            self.menu_state = 'playing'
            
        except Exception as e:
            print(f"❌ Failed to setup game world: {e}")
    
    def generate_terrain(self):
        """Generate the initial terrain"""
        print("🌍 Generating terrain...")
        
        # Generate a simple flat world with some hills
        for x in range(-self.world_size // 2, self.world_size // 2):
            for z in range(-self.world_size // 2, self.world_size // 2):
                # Create height variation
                height = int(3 + 2 * (0.5 + 0.5 * (x * 0.1) + 0.5 * (z * 0.1)) % 4)
                
                for y in range(height):
                    block_type = 1 if y == height - 1 else 2  # Grass on top, dirt below
                    self.place_block(x, y, z, block_type, update_network=False)
        
        # Add some trees and structures
        self.add_decorations()
        
        print(f"🌍 Generated world with {len(self.world_blocks)} blocks")
    
    def add_decorations(self):
        """Add trees and other decorations to the world"""
        # Add some trees
        for _ in range(10):
            x = random.randint(-20, 20)
            z = random.randint(-20, 20)
            
            # Find ground level
            ground_y = 0
            for y in range(10, -1, -1):
                if (x, y, z) in self.world_blocks:
                    ground_y = y
                    break
            
            # Place tree trunk
            for y in range(ground_y + 1, ground_y + 4):
                self.place_block(x, y, z, 4, update_network=False)  # Wood
            
            # Place leaves
            for dx in range(-1, 2):
                for dz in range(-1, 2):
                    for dy in range(2):
                        if random.random() < 0.7:
                            leaf_x, leaf_y, leaf_z = x + dx, ground_y + 3 + dy, z + dz
                            if (leaf_x, leaf_y, leaf_z) not in self.world_blocks:
                                self.place_block(leaf_x, leaf_y, leaf_z, 1, update_network=False)  # Green blocks as leaves
    
    # Multiplayer Methods
    def start_server(self, port=12345):
        """Start a multiplayer server"""
        try:
            self.server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
            self.server_socket.bind(('localhost', port))
            self.server_socket.listen(5)
            
            self.is_server = True
            self.is_multiplayer = True
            
            print(f"🌐 Server started on port {port}")
            
            # Start server thread
            self.server_thread = threading.Thread(target=self.server_loop, daemon=True)
            self.server_thread.start()
            
            # Start game
            self.setup_game_world()
            
        except Exception as e:
            print(f"❌ Failed to start server: {e}")
    
    def connect_to_server(self, host='localhost', port=12345):
        """Connect to a multiplayer server"""
        try:
            self.client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.client_socket.connect((host, port))
            
            self.is_multiplayer = True
            self.is_server = False
            
            print(f"🌐 Connected to server {host}:{port}")
            
            # Send join message
            join_msg = {
                'type': 'join',
                'player_id': self.player_id,
                'position': [0, 10, 0]
            }
            self.send_message(join_msg)
            
            # Start client thread
            self.client_thread = threading.Thread(target=self.client_loop, daemon=True)
            self.client_thread.start()
            
            # Start game
            self.setup_game_world()
            
        except Exception as e:
            print(f"❌ Failed to connect to server: {e}")
    
    def server_loop(self):
        """Main server loop for handling clients"""
        while self.is_server and self.server_socket:
            try:
                client_sock, addr = self.server_socket.accept()
                print(f"🔌 Client connected from {addr}")
                
                client_thread = threading.Thread(
                    target=self.handle_client, 
                    args=(client_sock, addr), 
                    daemon=True
                )
                client_thread.start()
                
            except Exception as e:
                if self.is_server:
                    print(f"❌ Server error: {e}")
                break
    
    def handle_client(self, client_sock, addr):
        """Handle individual client connections"""
        client_id = f"client_{addr[1]}"
        self.connected_clients[client_id] = {
            'socket': client_sock,
            'address': addr,
            'player_id': None,
            'position': [0, 10, 0]
        }
        
        try:
            while self.is_server:
                data = client_sock.recv(4096)
                if not data:
                    break
                
                try:
                    message = json.loads(data.decode())
                    self.handle_client_message(client_id, message)
                except json.JSONDecodeError:
                    print(f"❌ Invalid JSON from {addr}")
                    
        except Exception as e:
            print(f"❌ Client {addr} error: {e}")
        finally:
            if client_id in self.connected_clients:
                del self.connected_clients[client_id]
            client_sock.close()
            print(f"🔌 Client {addr} disconnected")
    
    def client_loop(self):
        """Main client loop for receiving server messages"""
        try:
            while self.is_multiplayer and self.client_socket:
                data = self.client_socket.recv(4096)
                if not data:
                    break
                
                try:
                    message = json.loads(data.decode())
                    self.handle_server_message(message)
                except json.JSONDecodeError:
                    print("❌ Invalid JSON from server")
                    
        except Exception as e:
            if self.is_multiplayer:
                print(f"❌ Client error: {e}")
    
    def handle_client_message(self, client_id, message):
        """Handle messages from clients"""
        msg_type = message.get('type')
        
        if msg_type == 'join':
            player_id = message.get('player_id')
            self.connected_clients[client_id]['player_id'] = player_id
            
            # Send world data to new client
            world_msg = {
                'type': 'world_data',
                'blocks': [(x, y, z, block_type) for (x, y, z), block_type in self.world_blocks.items()]
            }
            self.send_to_client(client_id, world_msg)
            
            # Notify other clients about new player
            player_join_msg = {
                'type': 'player_joined',
                'player_id': player_id,
                'position': message.get('position', [0, 10, 0])
            }
            self.broadcast_message(player_join_msg, exclude=client_id)
            
        elif msg_type == 'block_place':
            x, y, z = message['position']
            block_type = message['block_type']
            self.place_block(x, y, z, block_type, update_network=False)
            
            # Broadcast to all clients
            self.broadcast_message(message)
            
        elif msg_type == 'block_break':
            x, y, z = message['position']
            self.break_block(x, y, z, update_network=False)
            
            # Broadcast to all clients
            self.broadcast_message(message)
            
        elif msg_type == 'player_move':
            self.connected_clients[client_id]['position'] = message['position']
            
            # Broadcast player position to other clients
            move_msg = {
                'type': 'player_move',
                'player_id': self.connected_clients[client_id]['player_id'],
                'position': message['position']
            }
            self.broadcast_message(move_msg, exclude=client_id)
    
    def handle_server_message(self, message):
        """Handle messages from server"""
        msg_type = message.get('type')
        
        if msg_type == 'world_data':
            # Receive initial world data
            blocks = message.get('blocks', [])
            for x, y, z, block_type in blocks:
                self.place_block(x, y, z, block_type, update_network=False)
            
        elif msg_type == 'block_place':
            x, y, z = message['position']
            block_type = message['block_type']
            self.place_block(x, y, z, block_type, update_network=False)
            
        elif msg_type == 'block_break':
            x, y, z = message['position']
            self.break_block(x, y, z, update_network=False)
            
        elif msg_type == 'player_joined':
            player_id = message['player_id']
            position = message['position']
            self.add_other_player(player_id, position)
            
        elif msg_type == 'player_move':
            player_id = message['player_id']
            position = message['position']
            self.update_other_player(player_id, position)
    
    def send_message(self, message):
        """Send message to server (client side)"""
        if self.client_socket:
            try:
                data = json.dumps(message).encode()
                self.client_socket.send(data)
            except Exception as e:
                print(f"❌ Failed to send message: {e}")
    
    def send_to_client(self, client_id, message):
        """Send message to specific client (server side)"""
        if client_id in self.connected_clients:
            try:
                data = json.dumps(message).encode()
                self.connected_clients[client_id]['socket'].send(data)
            except Exception as e:
                print(f"❌ Failed to send to client {client_id}: {e}")
    
    def broadcast_message(self, message, exclude=None):
        """Broadcast message to all clients (server side)"""
        for client_id in list(self.connected_clients.keys()):
            if client_id != exclude:
                self.send_to_client(client_id, message)
    
    # Game Mechanics
    def place_block(self, x, y, z, block_type, update_network=True):
        """Place a block at the specified coordinates"""
        pos = (x, y, z)
        
        # Don't place if block already exists
        if pos in self.world_blocks:
            return
        
        # Create block entity
        block_color = self.block_types.get(block_type, {}).get('color', color.white)
        block = Entity(
            model='cube',
            color=block_color,
            position=(x, y, z)
        )
        
        self.world_blocks[pos] = block_type
        block.block_type = block_type
        block.world_position = pos
        
        # Network update
        if update_network and self.is_multiplayer:
            if self.is_server:
                msg = {
                    'type': 'block_place',
                    'position': [x, y, z],
                    'block_type': block_type
                }
                self.broadcast_message(msg)
            else:
                msg = {
                    'type': 'block_place',
                    'position': [x, y, z],
                    'block_type': block_type
                }
                self.send_message(msg)
    
    def break_block(self, x, y, z, update_network=True):
        """Break a block at the specified coordinates"""
        pos = (x, y, z)
        
        if pos not in self.world_blocks:
            return
        
        # Find and destroy the block entity
        for entity in scene.entities:
            if hasattr(entity, 'world_position') and entity.world_position == pos:
                destroy(entity)
                break
        
        del self.world_blocks[pos]
        
        # Network update
        if update_network and self.is_multiplayer:
            if self.is_server:
                msg = {
                    'type': 'block_break',
                    'position': [x, y, z]
                }
                self.broadcast_message(msg)
            else:
                msg = {
                    'type': 'block_break',
                    'position': [x, y, z]
                }
                self.send_message(msg)
    
    def add_other_player(self, player_id, position):
        """Add another player to the game"""
        if player_id not in self.other_players:
            player_entity = Entity(
                model='cube',
                color=color.blue,
                position=position,
                scale=(0.8, 1.8, 0.8)  # Player-like dimensions
            )
            
            # Add name tag
            name_tag = Text(
                player_id,
                position=(position[0], position[1] + 2, position[2]),
                scale=0.5,
                color=color.white,
                billboard=True
            )
            
            self.other_players[player_id] = {
                'entity': player_entity,
                'name_tag': name_tag,
                'position': position
            }
            
            print(f"👥 Player {player_id} joined the game")
    
    def update_other_player(self, player_id, position):
        """Update another player's position"""
        if player_id in self.other_players:
            player_data = self.other_players[player_id]
            player_data['entity'].position = position
            player_data['name_tag'].position = (position[0], position[1] + 2, position[2])
            player_data['position'] = position
    
    # UI Methods
    def show_multiplayer_menu(self):
        """Show multiplayer options menu"""
        self.clear_ui()
        
        title = Text('Multiplayer Options', position=(0, 0.3), scale=2.5, color=color.white, origin=(0, 0))
        self.ui_elements.append(title)
        
        host_btn = Button('Host Game', position=(-0.2, 0.1), scale=(0.3, 0.08), color=color.green)
        host_btn.on_click = self.host_game
        self.ui_elements.append(host_btn)
        
        join_btn = Button('Join Game', position=(0.2, 0.1), scale=(0.3, 0.08), color=color.blue)
        join_btn.on_click = self.join_game
        self.ui_elements.append(join_btn)
        
        back_btn = Button('Back', position=(0, -0.1), scale=(0.3, 0.08), color=color.gray)
        back_btn.on_click = self.setup_main_menu
        self.ui_elements.append(back_btn)
        
        self.menu_state = 'multiplayer'
    
    def create_game_ui(self):
        """Create in-game UI elements"""
        # Block selector
        self.block_selector = Text(
            f'Selected Block: {self.block_types.get(self.selected_block, {}).get("name", "Unknown")}',
            position=(-0.85, 0.45),
            scale=1.5,
            color=color.white
        )
        self.ui_elements.append(self.block_selector)
        
        # Player count (for multiplayer)
        if self.is_multiplayer:
            player_count = len(self.other_players) + 1  # +1 for local player
            self.player_count_text = Text(
                f'Players Online: {player_count}',
                position=(-0.85, 0.4),
                scale=1.5,
                color=color.yellow
            )
            self.ui_elements.append(self.player_count_text)
        
        # Controls reminder
        controls = Text(
            'ESC: Menu | 1-6: Select Block | Mouse: Look/Build/Break',
            position=(0, -0.45),
            scale=1.2,
            color=color.gray,
            origin=(0, 0)
        )
        self.ui_elements.append(controls)
    
    def clear_ui(self):
        """Clear all UI elements"""
        for element in self.ui_elements:
            if element:
                destroy(element)
        self.ui_elements.clear()
    
    # Menu Actions
    def start_singleplayer(self):
        """Start singleplayer game"""
        self.is_multiplayer = False
        self.setup_game_world()
    
    def host_game(self):
        """Host a multiplayer game"""
        self.start_server()
    
    def join_game(self):
        """Join a multiplayer game"""
        # For now, just connect to localhost
        # In a full implementation, you'd have an IP input field
        self.connect_to_server()
    
    def quit_game(self):
        """Quit the game"""
        if self.app:
            self.app.quit()
    
    def setup_input(self):
        """Set up input handling"""
        def input(key):
            if self.menu_state == 'playing':
                # Block selection
                if key in '123456':
                    self.selected_block = int(key)
                    if hasattr(self, 'block_selector'):
                        self.block_selector.text = f'Selected Block: {self.block_types.get(self.selected_block, {}).get("name", "Unknown")}'
                
                # Building/breaking
                elif key == 'left mouse down':
                    self.break_block_at_cursor()
                elif key == 'right mouse down':
                    self.place_block_at_cursor()
                
                # Menu
                elif key == 'escape':
                    self.setup_main_menu()
            
            elif key == 'escape' and self.menu_state != 'main':
                self.setup_main_menu()
        
        self.app.input = input
    
    def break_block_at_cursor(self):
        """Break block at cursor position"""
        if not self.player:
            return
        
        # Raycast to find target block
        hit_info = mouse.hovered_entity
        if hit_info and hasattr(hit_info, 'world_position'):
            x, y, z = hit_info.world_position
            self.break_block(x, y, z)
    
    def place_block_at_cursor(self):
        """Place block at cursor position"""
        if not self.player:
            return
        
        # Raycast to find placement position
        hit_info = mouse.hovered_entity
        if hit_info and hasattr(hit_info, 'world_position'):
            # Place block adjacent to the hit block
            hit_pos = hit_info.world_position
            
            # Simple placement logic - place above the hit block
            x, y, z = hit_pos
            new_pos = (x, y + 1, z)
            
            # Don't place where player is standing
            player_pos = (int(self.player.x), int(self.player.y), int(self.player.z))
            if new_pos != player_pos:
                self.place_block(new_pos[0], new_pos[1], new_pos[2], self.selected_block)
    
    def update_game(self):
        """Update game state (called every frame)"""
        if self.menu_state == 'playing' and self.player:
            # Update player position for multiplayer
            if self.is_multiplayer and not self.is_server:
                current_time = time.time()
                if not hasattr(self, 'last_position_update'):
                    self.last_position_update = 0
                
                # Send position update every 100ms
                if current_time - self.last_position_update > 0.1:
                    pos = [self.player.x, self.player.y, self.player.z]
                    msg = {
                        'type': 'player_move',
                        'position': pos
                    }
                    self.send_message(msg)
                    self.last_position_update = current_time
            
            # Update player count display
            if self.is_multiplayer and hasattr(self, 'player_count_text'):
                player_count = len(self.other_players) + 1
                self.player_count_text.text = f'Players Online: {player_count}'
    
    def get_updated_inventory(self):
        """Return the updated inventory after 3D interaction"""
        return self.player_inventory, self.player_hotbar
    
    def cleanup(self):
        """Clean up resources"""
        # Close network connections
        if self.server_socket:
            self.server_socket.close()
        if self.client_socket:
            self.client_socket.close()
        
        self.is_server = False
        self.is_multiplayer = False

# Compatibility with old End Portal system
class EndPortal3D(Minecraft3DGame):
    """Backward compatibility wrapper for the old End Portal system"""
    def __init__(self, player_inventory, player_hotbar):
        super().__init__(player_inventory, player_hotbar)
        
    def launch_3d_portal(self):
        """Launch the 3D game in a separate process (compatibility method)"""
        import subprocess
        import sys
        
        try:
            # Launch the 3D game in a separate process
            print("🌌 Launching 3D Portal in new window...")
            subprocess.Popen([sys.executable, __file__], 
                           cwd=os.path.dirname(os.path.abspath(__file__)))
            return True
        except Exception as e:
            print(f"❌ Failed to launch 3D portal: {e}")
            return False

# Main execution for standalone testing
if __name__ == "__main__":
    if URSINA_AVAILABLE:
        game = Minecraft3DGame()
        game.launch_game()
    else:
        print("❌ Ursina not available - cannot run 3D Minecraft game")
        print("📦 Install Ursina with: pip install ursina")

# Export the availability flag and classes
__all__ = ['URSINA_AVAILABLE', 'Minecraft3DGame', 'EndPortal3D']