# Hooks Configuration Explained

This document explains the hooks configuration used in this project to control the WizLight bulb based on Claude Code's status.

## What Are Hooks?

Hooks are automated commands that Claude Code runs in response to specific events during a conversation session. They allow you to trigger external actions (like controlling smart lights, sending notifications, running tests, etc.) without manual intervention.

## Hook Configuration Structure

The hooks are defined in `.claude/settings.json` following this structure:

```json
{
  "hooks": {
    "EventName": [
      {
        "hooks": [
          {
            "type": "command",
            "command": "shell command to run",
            "statusMessage": "Optional message shown in UI"
          }
        ]
      }
    ]
  }
}
```

### Key Fields

- **EventName**: The name of the event that triggers the hook (e.g., `SessionStart`, `Stop`)
- **type**: The type of hook - `"command"` runs a shell command
- **command**: The shell command to execute when the event fires
- **statusMessage**: Optional human-readable message shown in the Claude Code UI while the hook runs

## Events Used in This Project

### 1. SessionStart
**When it fires:** When you first launch Claude Code or start a new session

**What it does:** Sets the light to green (ready state) to indicate Claude is ready and waiting

```json
"SessionStart": [
  {
    "hooks": [
      {
        "type": "command",
        "command": "python3 /home/jimccann/cwizlight/claude_status_light.py input",
        "statusMessage": "Setting light to ready (green)"
      }
    ]
  }
]
```

### 2. UserPromptSubmit
**When it fires:** Immediately after you submit a prompt/question to Claude

**What it does:** Sets the light to yellow (processing state) to indicate Claude is working on your request

```json
"UserPromptSubmit": [
  {
    "hooks": [
      {
        "type": "command",
        "command": "python3 /home/jimccann/cwizlight/claude_status_light.py idle",
        "statusMessage": "Setting light to processing (yellow)"
      }
    ]
  }
]
```

### 3. Stop
**When it fires:** When Claude finishes generating a response and stops

**What it does:** Sets the light back to green (ready) to indicate Claude is done and waiting for the next prompt

```json
"Stop": [
  {
    "hooks": [
      {
        "type": "command",
        "command": "python3 /home/jimccann/cwizlight/claude_status_light.py input",
        "statusMessage": "Setting light to ready (green)"
      }
    ]
  }
]
```

### 4. PermissionRequest
**When it fires:** When Claude needs to ask for permission to perform an action (like editing a file, running a command, etc.)

**What it does:** Sets the light to red (input needed) to alert you that Claude is waiting for your approval

```json
"PermissionRequest": [
  {
    "hooks": [
      {
        "type": "command",
        "command": "python3 /home/jimccann/cwizlight/claude_status_light.py working",
        "statusMessage": "Setting light to input needed (red)"
      }
    ]
  }
]
```

### 5. PostToolUse (Write/Edit Files)
**When it fires:** After Claude successfully writes or edits a file

**What it does:** Flashes the light bright white to provide visual feedback when files are modified

**Why flash?** This gives you immediate visual confirmation that Claude has saved changes to disk, which is especially useful when working on multiple files or when you're not actively watching the screen.

**The matcher:** The `"Write|Edit"` matcher means this hook only fires when Claude uses the Write or Edit tools, not for other tools like Bash or Read.

```json
"PostToolUse": [
  {
    "matcher": "Write|Edit",
    "hooks": [
      {
        "type": "command",
        "command": "python3 /home/jimccann/cwizlight/claude_status_light.py flash",
        "statusMessage": "Flashing light (white) - file written/edited"
      }
    ]
  }
]
```

**Note:** The flash is brief - it sets the light to bright white, and the next hook event (like Stop when Claude finishes) will set it back to the appropriate color.

### 6. SessionEnd
**When it fires:** When you exit Claude Code or the session terminates

**What it does:** Sets the light to a warm white at 20% brightness (a gentle "goodbye"), then immediately turns off

**Why the sequence?** The warm dim light provides a brief visual transition instead of an abrupt shutoff, signaling that the session is ending gracefully.

```json
"SessionEnd": [
  {
    "hooks": [
      {
        "type": "command",
        "command": "python3 /home/jimccann/cwizlight/claude_status_light.py warm && python3 /home/jimccann/cwizlight/claude_status_light.py off",
        "statusMessage": "Setting warm goodbye light, then turning off"
      }
    ]
  }
]
```

**Note:** This hook runs two commands sequentially using `&&`:
1. Set to warm white at 20% brightness
2. Turn off the light

## Other Available Hook Events

While this project doesn't use them, Claude Code supports many other hook events you could use:

- **PreToolUse**: Before Claude uses a tool (Read, Write, Bash, etc.)
- **PostToolUse**: After Claude successfully uses a tool
- **PostToolUseFailure**: When a tool use fails
- **Notification**: When a notification occurs
- **PreCompact**: Before conversation context is compacted
- **PostCompact**: After conversation context is compacted

## Customization Ideas

### Add More States
You could add hooks for other events, like flashing the light when a file is edited:

```json
"PostToolUse": [
  {
    "matcher": "Write|Edit",
    "hooks": [
      {
        "type": "command",
        "command": "python3 /home/jimccann/cwizlight/claude_status_light.py flash"
      }
    ]
  }
]
```

### Use Different Colors
Modify `claude_status_light.py` to add more color states, then map them to different events.

### Add Timeouts
Add a timeout to prevent hooks from hanging:

```json
{
  "type": "command",
  "command": "python3 /home/jimccann/cwizlight/claude_status_light.py working",
  "timeout": 5
}
```

### Run Multiple Hooks per Event
You can run multiple commands for a single event:

```json
"SessionStart": [
  {
    "hooks": [
      {
        "type": "command",
        "command": "python3 /home/jimccann/cwizlight/claude_status_light.py idle"
      },
      {
        "type": "command",
        "command": "notify-send 'Claude Code started'"
      }
    ]
  }
]
```

## Conditional Hooks (Advanced)

You can use the `matcher` field to only run hooks when specific tools are used:

```json
"PostToolUse": [
  {
    "matcher": "Bash",
    "hooks": [
      {
        "type": "command",
        "command": "echo 'Claude ran a bash command' >> ~/claude-bash-log.txt"
      }
    ]
  }
]
```

The `matcher` field supports:
- Exact tool names: `"Bash"`, `"Write"`, `"Edit"`
- Multiple tools: `"Write|Edit"` (pipe-separated)
- Wildcards for command matching: `"Bash(git *)"` matches any git command

## Hook Input Data

Hooks receive JSON data on stdin describing the event. You can parse this in your scripts:

```bash
#!/bin/bash
# Example: Log tool usage
jq -r '.tool_name' | while read tool; do
  echo "$(date): Used $tool" >> ~/claude-tools.log
done
```

The JSON structure includes:
- `session_id`: Current session ID
- `tool_name`: Name of the tool being used (for tool-related hooks)
- `tool_input`: Parameters passed to the tool
- `tool_response`: Response from the tool (PostToolUse only)

## Debugging Hooks

1. **Check hook syntax**: Validate JSON with `jq . .claude/settings.json`
2. **View active hooks**: Type `/hooks` in Claude Code
3. **Test commands manually**: Run the hook command in your terminal
4. **Check hook output**: Hooks that error or take >1 second will show in the UI

## Resources

- Full hooks documentation: See the update-config skill documentation
- Example file: `example-settings.json` in this directory
- Active configuration: `.claude/settings.json`
