"""
Example: MCP Server for Text Adventures

A complete MCP server that exposes text adventure games via tools.
This demonstrates a full-featured server with memory, mapping, and inventory.
"""

import sys
import os
import io
import contextlib

# Add parent directory to path to import games module
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from fastmcp import FastMCP
from games.zork_env import TextAdventureEnv, list_available_games


# Get game from environment variable (default: zork1)
INITIAL_GAME = os.environ.get("GAME", "zork1")

# Create the MCP server
mcp = FastMCP("Text Adventure Server")


class GameState:
    """Manages the text adventure game state and exploration data."""
    
    def __init__(self, game: str = "zork1"):
        self.game_name = game
        # Suppress stdout during game environment initialization to avoid MCP protocol errors
        # (spacy downloads and other package output should not interfere with JSON-RPC)
        with contextlib.redirect_stdout(io.StringIO()):
            self.env = TextAdventureEnv(game)
            self.state = self.env.reset()
        self.history: list[tuple[str, str]] = []
        self.explored_locations: dict[str, set[str]] = {}
        self.current_location: str = self._extract_location(self.state.observation)
        self.saved_states = {}  # Dictionary to store saved game states
    
    def _extract_location(self, observation: str) -> str:
        """Extract location name from observation (usually first line)."""
        lines = observation.strip().split('\n')
        return lines[0] if lines else "Unknown"
    
    def take_action(self, action: str) -> str:
        """Execute a game action and return the result."""
        self.state = self.env.step(action)
        result = self.state.observation
        
        # Track history
        self.history.append((action, result))
        if len(self.history) > 50:
            self.history = self.history[-50:]
        
        # Update map
        new_location = self._extract_location(result)
        if action in ["north", "south", "east", "west", "up", "down", 
                      "enter", "exit", "n", "s", "e", "w", "u", "d"]:
            if self.current_location not in self.explored_locations:
                self.explored_locations[self.current_location] = set()
            if new_location != self.current_location:
                self.explored_locations[self.current_location].add(f"{action} -> {new_location}")
        self.current_location = new_location
        
        return result
    
    def get_memory(self) -> str:
        """Get a summary of current game state."""
        recent = self.history[-5:] if self.history else []
        recent_str = "\n".join([f"  > {a} -> {r[:60]}..." for a, r in recent]) if recent else "  (none yet)"
        
        return f"""Current State:
    - Location: {self.current_location}
    - Score: {self.state.score} points
    - Moves: {self.state.moves}
    - Game: {self.game_name}

    Recent Actions:
    {recent_str}

    Current Observation:
    {self.state.observation}"""
    
    def get_map(self) -> str:
        """Get a map of explored locations."""
        if not self.explored_locations:
            return "Map: No locations explored yet. Try moving around!"
        
        lines = ["Explored Locations and Exits:"]
        for loc, exits in sorted(self.explored_locations.items()):
            lines.append(f"\n* {loc}")
            for exit_info in sorted(exits):
                lines.append(f"    -> {exit_info}")
        
        lines.append(f"\n[Current] {self.current_location}")
        return "\n".join(lines)
    
    def get_inventory(self) -> str:
        """Get current inventory."""
        items = self.state.inventory if hasattr(self.state, 'inventory') and self.state.inventory else []
        
        if not items:
            return "Inventory: You are empty-handed."
        
        item_names = []
        for item in items:
            item_str = str(item)
            item_lower = item_str.lower()
            if "parent" in item_lower:
                idx = item_lower.index("parent")
                name = item_str[:idx].strip()
                if ":" in name:
                    name = name.split(":", 1)[1].strip()
                item_names.append(name)
            elif ":" in item_str:
                name = item_str.split(":")[1].strip()
                item_names.append(name)
            else:
                item_names.append(item_str)
        
        return f"Inventory: {', '.join(item_names)}"
    
    def get_valid_actions(self) -> str:
        """Get list of valid actions available in current state."""
        try:
            actions = self.env.get_valid_actions()
            if not actions:
                return "No valid actions available."
            return "Valid Actions:\n" + "\n".join(f"  - {action}" for action in actions)
        except Exception as e:
            return f"Could not retrieve valid actions: {e}"
    
    def check_vocabulary(self, word: str) -> str:
        """Check if a specific word is understood by the game engine."""
        try:
            vocab = self.env.get_dictionary()
            # Jericho dictionaries often store the first 6-9 characters of a word
            # due to Z-machine limitations, so check for partial matches.
            word_lower = word.lower()
            matches = [w for w in vocab if w.startswith(word_lower[:6])]
            
            if matches:
                return f"Yes, the game understands '{word}' (matches: {', '.join(matches)})."
            return f"No, the game does NOT understand the word '{word}'. Try a different synonym."
        except Exception as e:
            return f"Could not check vocabulary: {e}"
    
    def save_game(self, slot_name: str) -> str:
        """Save the current game state to a named slot."""
        try:
            self.saved_states[slot_name] = self.env.get_state()
            return f"Game saved successfully to slot: '{slot_name}'"
        except Exception as e:
            return f"Error saving game to slot '{slot_name}': {e}"
    
    def load_game(self, slot_name: str) -> str:
        """Load a previously saved game state from a named slot."""
        if slot_name not in self.saved_states:
            return f"Error: No save found in slot '{slot_name}'"
        try:
            self.env.set_state(self.saved_states[slot_name])
            # Refresh the observation after loading
            self.state = self.env.step("look")
            self.current_location = self._extract_location(self.state.observation)
            return f"Game loaded from slot: '{slot_name}'.\nCurrent location: {self.state.observation}"
        except Exception as e:
            return f"Error loading game from slot '{slot_name}': {e}"


# Global game state
_game_state: GameState | None = None


def get_game() -> GameState:
    """Get or initialize the game state."""
    global _game_state
    if _game_state is None:
        _game_state = GameState(INITIAL_GAME)
    return _game_state


# =============================================================================
# MCP Tools
# =============================================================================

@mcp.tool()
def play_action(action: str) -> str:
    """
    Execute a game action in the text adventure.
    
    Args:
        action: The command to execute (e.g., 'north', 'take lamp', 'open mailbox')
    
    Returns:
        The game's response to your action
    """
    game = get_game()
    result = game.take_action(action)

    # Add score info
    score_info = f"\n\n[Score: {game.state.score} | Moves: {game.state.moves}]"
    
    if game.state.reward > 0:
        score_info = f"\n\n+{game.state.reward} points! (Total: {game.state.score})"
    
    done_info = ""
    if game.state.done:
        done_info = "\n\nGAME OVER"
    
    return result + score_info + done_info


@mcp.tool()
def memory() -> str:
    """
    Get a summary of the current game state.
    
    Returns location, score, moves, recent actions, and current observation.
    """
    return get_game().get_memory()


@mcp.tool()
def get_map() -> str:
    """
    Get a map showing explored locations and connections.
    
    Useful for navigation and avoiding getting lost.
    """
    return get_game().get_map()


@mcp.tool()
def inventory() -> str:
    """
    Check what items you are currently carrying.
    """
    return get_game().get_inventory()


@mcp.tool()
def valid_actions() -> str:
    """
    Get the list of valid actions you can perform in the current game state.
    
    Returns a list of actions that are currently available.
    """
    return get_game().get_valid_actions()


@mcp.tool()
def check_vocabulary(word: str) -> str:
    """
    Check if a specific word is understood by the game engine.
    Use this before trying unusual verbs or interacting with weird objects.
    """
    return get_game().check_vocabulary(word)


@mcp.tool()
def save_state(slot_name: str) -> str:
    """
    Save the current game state to a named slot before doing something risky.
    
    Args:
        slot_name: Name of the save slot (e.g., "before_combat", "checkpoint_1")
    
    Returns:
        Confirmation message
    """
    return get_game().save_game(slot_name)


@mcp.tool()
def load_state(slot_name: str) -> str:
    """
    Load a previously saved game state if you died or made a mistake.
    
    Args:
        slot_name: Name of the save slot to load from
    
    Returns:
        Confirmation message with current location
    """
    return get_game().load_game(slot_name)


# =============================================================================
# Main
# =============================================================================

if __name__ == "__main__":
    mcp.run()
