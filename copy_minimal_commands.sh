#!/bin/zsh
# copy_realtime_hairbrush.sh
# Replicates project structure and copies files from semantic_gcode to realtimeSDK.

# Create target directories
mkdir -p /mnt/c/Users/wtrem/Projects/realtimeSDK/realtime_hairbrush
mkdir -p /mnt/c/Users/wtrem/Projects/realtimeSDK/realtime_hairbrush/ui
mkdir -p /mnt/c/Users/wtrem/Projects/realtimeSDK/realtime_hairbrush/runtime
mkdir -p /mnt/c/Users/wtrem/Projects/realtimeSDK/realtime_hairbrush/transport
mkdir -p /mnt/c/Users/wtrem/Projects/realtimeSDK/realtime_hairbrush/config
mkdir -p /mnt/c/Users/wtrem/Projects/realtimeSDK/realtime_hairbrush/cli
mkdir -p /mnt/c/Users/wtrem/Projects/realtimeSDK/realtime_hairbrush/cli/utils
mkdir -p /mnt/c/Users/wtrem/Projects/realtimeSDK/realtime_hairbrush/cli/commands
mkdir -p /mnt/c/Users/wtrem/Projects/realtimeSDK/realtime_hairbrush/instructions
mkdir -p /mnt/c/Users/wtrem/Projects/realtimeSDK/realtime_hairbrush/execution

# Copy realtime_hairbrush package root
cp /mnt/c/Users/wtrem/Projects/semantic_gcode/realtime_hairbrush/__init__.py \
   /mnt/c/Users/wtrem/Projects/realtimeSDK/realtime_hairbrush/

# Copy UI (Textual app)
cp /mnt/c/Users/wtrem/Projects/semantic_gcode/realtime_hairbrush/ui/textual_app.py \
   /mnt/c/Users/wtrem/Projects/realtimeSDK/realtime_hairbrush/ui/

# Copy runtime core
cp /mnt/c/Users/wtrem/Projects/semantic_gcode/realtime_hairbrush/runtime/__init__.py \
   /mnt/c/Users/wtrem/Projects/realtimeSDK/realtime_hairbrush/runtime/
cp /mnt/c/Users/wtrem/Projects/semantic_gcode/realtime_hairbrush/runtime/dispatcher.py \
   /mnt/c/Users/wtrem/Projects/realtimeSDK/realtime_hairbrush/runtime/
cp /mnt/c/Users/wtrem/Projects/semantic_gcode/realtime_hairbrush/runtime/readers.py \
   /mnt/c/Users/wtrem/Projects/realtimeSDK/realtime_hairbrush/runtime/
cp /mnt/c/Users/wtrem/Projects/semantic_gcode/realtime_hairbrush/runtime/object_model.py \
   /mnt/c/Users/wtrem/Projects/realtimeSDK/realtime_hairbrush/runtime/
cp /mnt/c/Users/wtrem/Projects/semantic_gcode/realtime_hairbrush/runtime/state.py \
   /mnt/c/Users/wtrem/Projects/realtimeSDK/realtime_hairbrush/runtime/
cp /mnt/c/Users/wtrem/Projects/semantic_gcode/realtime_hairbrush/runtime/queue.py \
   /mnt/c/Users/wtrem/Projects/realtimeSDK/realtime_hairbrush/runtime/
cp /mnt/c/Users/wtrem/Projects/semantic_gcode/realtime_hairbrush/runtime/events.py \
   /mnt/c/Users/wtrem/Projects/realtimeSDK/realtime_hairbrush/runtime/

# Copy transport
cp /mnt/c/Users/wtrem/Projects/semantic_gcode/realtime_hairbrush/transport/__init__.py \
   /mnt/c/Users/wtrem/Projects/realtimeSDK/realtime_hairbrush/transport/
cp /mnt/c/Users/wtrem/Projects/semantic_gcode/realtime_hairbrush/transport/airbrush_transport.py \
   /mnt/c/Users/wtrem/Projects/realtimeSDK/realtime_hairbrush/transport/
cp /mnt/c/Users/wtrem/Projects/semantic_gcode/realtime_hairbrush/transport/config.py \
   /mnt/c/Users/wtrem/Projects/realtimeSDK/realtime_hairbrush/transport/

# Copy config package
cp /mnt/c/Users/wtrem/Projects/semantic_gcode/realtime_hairbrush/config/__init__.py \
   /mnt/c/Users/wtrem/Projects/realtimeSDK/realtime_hairbrush/config/
cp /mnt/c/Users/wtrem/Projects/semantic_gcode/realtime_hairbrush/config/settings.py \
   /mnt/c/Users/wtrem/Projects/realtimeSDK/realtime_hairbrush/config/
cp /mnt/c/Users/wtrem/Projects/semantic_gcode/realtime_hairbrush/config/manager.py \
   /mnt/c/Users/wtrem/Projects/realtimeSDK/realtime_hairbrush/config/
cp /mnt/c/Users/wtrem/Projects/semantic_gcode/realtime_hairbrush/config/default_config.json \
   /mnt/c/Users/wtrem/Projects/realtimeSDK/realtime_hairbrush/config/

# Copy package-level settings
cp /mnt/c/Users/wtrem/Projects/semantic_gcode/realtime_hairbrush/settings.yaml \
   /mnt/c/Users/wtrem/Projects/realtimeSDK/realtime_hairbrush/
cp /mnt/c/Users/wtrem/Projects/semantic_gcode/realtime_hairbrush/commands.yaml \
   /mnt/c/Users/wtrem/Projects/realtimeSDK/realtime_hairbrush/

# Copy CLI entry and init
cp /mnt/c/Users/wtrem/Projects/semantic_gcode/realtime_hairbrush/cli/__init__.py \
   /mnt/c/Users/wtrem/Projects/realtimeSDK/realtime_hairbrush/cli/
cp /mnt/c/Users/wtrem/Projects/semantic_gcode/realtime_hairbrush/cli/main.py \
   /mnt/c/Users/wtrem/Projects/realtimeSDK/realtime_hairbrush/cli/

# Copy CLI utils
cp /mnt/c/Users/wtrem/Projects/semantic_gcode/realtime_hairbrush/cli/utils/__init__.py \
   /mnt/c/Users/wtrem/Projects/realtimeSDK/realtime_hairbrush/cli/utils/
cp /mnt/c/Users/wtrem/Projects/semantic_gcode/realtime_hairbrush/cli/utils/port_selection.py \
   /mnt/c/Users/wtrem/Projects/realtimeSDK/realtime_hairbrush/cli/utils/
cp /mnt/c/Users/wtrem/Projects/semantic_gcode/realtime_hairbrush/cli/utils/interactive.py \
   /mnt/c/Users/wtrem/Projects/realtimeSDK/realtime_hairbrush/cli/utils/
cp /mnt/c/Users/wtrem/Projects/semantic_gcode/realtime_hairbrush/cli/utils/command_parser.py \
   /mnt/c/Users/wtrem/Projects/realtimeSDK/realtime_hairbrush/cli/utils/
cp /mnt/c/Users/wtrem/Projects/semantic_gcode/realtime_hairbrush/cli/utils/formatting.py \
   /mnt/c/Users/wtrem/Projects/realtimeSDK/realtime_hairbrush/cli/utils/

# Copy CLI commands
cp /mnt/c/Users/wtrem/Projects/semantic_gcode/realtime_hairbrush/cli/commands/__init__.py \
   /mnt/c/Users/wtrem/Projects/realtimeSDK/realtime_hairbrush/cli/commands/
cp /mnt/c/Users/wtrem/Projects/semantic_gcode/realtime_hairbrush/cli/commands/connect.py \
   /mnt/c/Users/wtrem/Projects/realtimeSDK/realtime_hairbrush/cli/commands/
cp /mnt/c/Users/wtrem/Projects/semantic_gcode/realtime_hairbrush/cli/commands/config.py \
   /mnt/c/Users/wtrem/Projects/realtimeSDK/realtime_hairbrush/cli/commands/
cp /mnt/c/Users/wtrem/Projects/semantic_gcode/realtime_hairbrush/cli/commands/manual.py \
   /mnt/c/Users/wtrem/Projects/realtimeSDK/realtime_hairbrush/cli/commands/
cp /mnt/c/Users/wtrem/Projects/semantic_gcode/realtime_hairbrush/cli/commands/sequence.py \
   /mnt/c/Users/wtrem/Projects/realtimeSDK/realtime_hairbrush/cli/commands/
cp /mnt/c/Users/wtrem/Projects/semantic_gcode/realtime_hairbrush/cli/commands/stroke.py \
   /mnt/c/Users/wtrem/Projects/realtimeSDK/realtime_hairbrush/cli/commands/

# Copy instructions and execution
cp -r /mnt/c/Users/wtrem/Projects/semantic_gcode/realtime_hairbrush/instructions/* \
      /mnt/c/Users/wtrem/Projects/realtimeSDK/realtime_hairbrush/instructions/
cp -r /mnt/c/Users/wtrem/Projects/semantic_gcode/realtime_hairbrush/execution/* \
      /mnt/c/Users/wtrem/Projects/realtimeSDK/realtime_hairbrush/execution/

# Copy full semantic_gcode SDK
cp -r /mnt/c/Users/wtrem/Projects/semantic_gcode/semantic_gcode \
      /mnt/c/Users/wtrem/Projects/realtimeSDK/
