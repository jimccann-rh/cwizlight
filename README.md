# WizLight Claude Status Indicator

Turn your WizLight smart bulb into a visual status indicator for Claude Code! Your bulb will automatically change colors to show when Claude is working, idle, waiting for input, or when the session ends.

## What It Does

This project uses a WizLight smart bulb to provide ambient status notifications while you work with Claude Code:

- 🟢 **Green** - Claude is ready and waiting for your next prompt
- 🟡 **Yellow** - Claude is processing your request
- 🔴 **Red** - Claude needs your input (permission prompt or question)
- ⚪ **White Flash** - File written or edited
- 💡 **Warm White (20%)** - Session ending (briefly before turning off)
- ⚫ **Off** - Session ended

## Requirements

### Hardware
- A WizLight-compatible smart bulb (WiFi-enabled)
- The bulb must be on the same network as your computer

### Software
- Python 3.7+
- `pywizlight` library
- Claude Code CLI

## Installation

1. **Install the pywizlight library:**
   ```bash
   pip install pywizlight
   ```

2. **Find your bulb's IP address:**
   - Check your router's DHCP client list, or
   - Use your WizLight mobile app to find the bulb's IP, or
   - Use network scanning tools like `nmap`:
     ```bash
     nmap -sn 192.168.0.0/24
     ```

3. **Clone or download this repository:**
   ```bash
   cd /home/jimccann/cwizlight
   ```

4. **Update the bulb IP address:**
   Edit `claude_status_light.py` and change the `BULB_IP` constant to your bulb's IP address:
   ```python
   BULB_IP = "192.168.0.220"  # Change this to your bulb's IP
   ```

5. **Test the script:**
   ```bash
   python3 claude_status_light.py input    # Should turn green
   python3 claude_status_light.py idle     # Should turn yellow
   python3 claude_status_light.py working  # Should turn red
   python3 claude_status_light.py flash    # Should turn bright white
   python3 claude_status_light.py warm     # Should turn warm white at 20%
   python3 claude_status_light.py off      # Should turn off
   ```

## How It Works

The system uses Claude Code's **hooks** feature to automatically run commands at specific points in the conversation lifecycle.

### The Script

`claude_status_light.py` is a simple Python script that accepts one argument:
- `input` - Set bulb to green (RGB: 0, 255, 0) - ready state
- `idle` - Set bulb to yellow (RGB: 255, 255, 0) - processing state
- `working` - Set bulb to red (RGB: 255, 0, 0) - needs input state
- `flash` - Set bulb to bright white (RGB: 255, 255, 255) - file activity indicator
- `warm` - Set bulb to warm white at 20% brightness - goodbye state
- `off` - Turn off the bulb

### The Hooks

Hooks are configured in `.claude/settings.json` and trigger automatically:

| Hook Event | When It Fires | Action | Color |
|------------|---------------|--------|-------|
| `SessionStart` | When you start Claude Code | Set to ready | 🟢 Green |
| `UserPromptSubmit` | When you submit a prompt | Set to processing | 🟡 Yellow |
| `Stop` | When Claude finishes responding | Set to ready | 🟢 Green |
| `PermissionRequest` | When Claude needs permission/input | Set to input needed | 🔴 Red |
| `PostToolUse` (Write/Edit) | When Claude writes or edits a file | Flash bright white | ⚪ White |
| `SessionEnd` | When you exit Claude Code | Set to warm white, then turn off | 💡 Warm → ⚫ Off |

**Learn more:** See `HOOKS-EXPLAINED.md` for a detailed explanation of how hooks work and customization ideas. See `example-settings.json` for the complete configuration.

## Configuration Files

### claude_status_light.py
The main Python script that controls the bulb. Modify `BULB_IP` to match your bulb's network address.

### .claude/settings.json
The hooks configuration that tells Claude Code when to trigger the light changes. This file is automatically created and configured during setup.

### example-settings.json
A documented example of the hooks configuration showing all the event triggers. You can use this as a reference if you want to customize the hooks or set them up manually.

## Troubleshooting

### The light doesn't change
1. **Check network connectivity:**
   ```bash
   ping 192.168.0.220  # Use your bulb's IP
   ```

2. **Test the script manually:**
   ```bash
   python3 claude_status_light.py idle
   ```

3. **Check for errors:**
   The script will print error messages if it can't connect to the bulb.

4. **Verify hooks are loaded:**
   - Type `/hooks` in Claude Code to see active hooks
   - Restart Claude Code to reload the configuration

### The bulb IP changed
If your router assigns a new IP to the bulb:
1. Find the new IP address
2. Update `BULB_IP` in `claude_status_light.py`
3. Consider setting a static IP for your bulb in your router settings

### Hooks not firing
1. Make sure you're running Claude Code from `/home/jimccann/cwizlight` (where `.claude/settings.json` is located)
2. Check that `.claude/settings.json` exists and has valid JSON syntax:
   ```bash
   jq . .claude/settings.json
   ```

## Customization

### Change Colors
Edit the RGB values in `claude_status_light.py`:
```python
if status == "working":
    # Change red to blue
    await light.turn_on(PilotBuilder(rgb=(0, 0, 255), brightness=255))
```

### Change Brightness
Adjust the `brightness` parameter (0-255):
```python
await light.turn_on(PilotBuilder(rgb=(255, 0, 0), brightness=128))
```

### Add New States
1. Add a new condition in `claude_status_light.py`
2. Add a corresponding hook in `.claude/settings.json`

### Use Multiple Bulbs
Create separate scripts for each bulb with different IP addresses, or modify the script to accept an IP as a command-line argument.

## Managing Hooks

### View Active Hooks
Type `/hooks` in Claude Code to see all configured hooks.

### Temporarily Disable
Rename the settings file:
```bash
mv .claude/settings.json .claude/settings.json.disabled
```

### Re-enable
```bash
mv .claude/settings.json.disabled .claude/settings.json
```

## Project Structure

```
/home/jimccann/cwizlight/
├── README.md                    # This file
├── HOOKS-EXPLAINED.md           # Detailed explanation of hooks configuration
├── claude_status_light.py       # Main control script
├── example-settings.json        # Example hooks configuration
└── .claude/
    └── settings.json           # Active hooks configuration
```

## Advanced Usage

### Use with Git
If you commit `.claude/settings.json` to your repository, other team members can use the same hooks (after updating the bulb IP to their own bulb).

Add to `.gitignore` if you want to keep hooks local:
```bash
echo ".claude/settings.json" >> .gitignore
```

### Use Different Settings Per Project
The hooks in `.claude/settings.json` only apply when you run Claude Code from this directory. You can have different hooks in different projects.

### Global vs Project Settings
- **Global settings:** `~/.claude/settings.json` - Apply to all projects
- **Project settings:** `.claude/settings.json` - Apply only to this project
- Project settings override global settings

## Resources

### Project Documentation
- `HOOKS-EXPLAINED.md` - Detailed guide to hooks configuration and customization
- `example-settings.json` - Complete hooks configuration example

### External Resources
- [pywizlight documentation](https://github.com/sbidy/pywizlight)
- [Claude Code hooks documentation](https://docs.anthropic.com/claude-code)
- [WizLight product information](https://www.wizconnected.com/)

## License

This project is provided as-is for personal use. Modify and distribute freely.

## Contributing

Feel free to fork and improve! Some ideas:
- Support for other smart light brands (Philips Hue, LIFX, etc.)
- Add sound notifications
- Create a web dashboard showing current status
- Support for light effects/animations
- Desktop notifications in addition to light changes
