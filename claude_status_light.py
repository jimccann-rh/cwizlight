#!/usr/bin/env python3
"""Control WizLight bulb to show Claude Code status."""
import asyncio
import sys
from pywizlight import wizlight, PilotBuilder

BULB_IP = "192.168.0.220"

async def set_status(status: str):
    """Set the bulb color based on Claude's status.

    Args:
        status: One of 'working', 'idle', 'input', 'warm', 'flash', 'off'
    """
    light = wizlight(BULB_IP)

    try:
        if status == "working":
            # Red - needs user input
            await light.turn_on(PilotBuilder(rgb=(255, 0, 0), brightness=255))
        elif status == "idle":
            # Yellow - processing
            await light.turn_on(PilotBuilder(rgb=(255, 255, 0), brightness=255))
        elif status == "input":
            # Green - ready
            await light.turn_on(PilotBuilder(rgb=(0, 255, 0), brightness=255))
        elif status == "warm":
            # Warm white at 20% brightness - goodbye/session ending
            await light.turn_on(PilotBuilder(warm_white=255, brightness=51))
        elif status == "flash":
            # Bright white flash - file written/edited
            await light.turn_on(PilotBuilder(rgb=(255, 255, 255), brightness=255))
        elif status == "off":
            # Turn off - session ended
            await light.turn_off()
        else:
            print(f"Unknown status: {status}", file=sys.stderr)
            sys.exit(1)
    except Exception as e:
        print(f"Error controlling light: {e}", file=sys.stderr)
        sys.exit(1)
    finally:
        # Properly close the connection to avoid cleanup warnings
        await light.async_close()

if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("Usage: claude_status_light.py <working|idle|input|warm|flash|off>", file=sys.stderr)
        sys.exit(1)

    asyncio.run(set_status(sys.argv[1]))
