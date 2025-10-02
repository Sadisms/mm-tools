# MM-Tools

[![Python](https://img.shields.io/badge/Python-3.8+-blue?style=flat-square&logo=python&logoColor=white)](https://www.python.org)
[![License](https://img.shields.io/badge/License-MIT-yellow?style=flat-square)](LICENSE)

A comprehensive Python toolkit for building interactive Mattermost bot plugins with advanced dialog management, stateful sessions, and database integration.

> [!TIP]
> This toolkit provides a streamlined way to create sophisticated Mattermost bots with minimal boilerplate code.

## Overview

MM-Tools is designed to simplify the development of Mattermost bot plugins by providing a robust foundation with pre-built components for common bot functionality. It offers a plugin-based architecture with built-in support for interactive dialogs, file attachments, session management, and database operations.

The toolkit is built around these core components:

- **Plugin Framework**: Base plugin class with logging, Sentry integration, and message handling utilities
- **Interactive Dialogs**: Rich dialog system with various input elements and validation
- **Attachment System**: Support for buttons, selects, fields, and rich message formatting
- **Session Management**: SQLite-based stateful dialog management with decorators
- **Database Integration**: Async database operations with Peewee ORM and migration support
- **State Machine**: Plugin state management for complex workflows

## Features

- **Rich Interactive Elements**: Buttons, select menus, text inputs, checkboxes, and more
- **Stateful Conversations**: Persistent session storage for multi-step workflows  
- **File Handling**: Upload, download, and share files between channels
- **User Management**: Retrieve user information, send direct messages, and manage permissions
- **Database Operations**: Built-in async database support with migrations
- **Logging & Monitoring**: Structured logging with optional Sentry integration
- **Plugin Architecture**: Extensible base classes for rapid bot development

## Getting Started

### Prerequisites

- Python 3.8 or higher
- Mattermost server instance
- Bot account credentials

### Installation

Install directly from the repository:

```bash
pip install git+https://github.com/Sadisms/mm-tools.git
```

Or clone and install locally:

```bash
git clone https://github.com/Sadisms/mm-tools.git
cd mm-tools
python setup.py install
```

### Dependencies

The toolkit requires the following packages:

- `aiosqlite` - Async SQLite database operations
- `peewee` (~3.16.0) - ORM for database models
- `peewee-async` (~0.8.0) - Async support for Peewee
- `peewee-moves` - Database migration support
- `aiopg` (~1.4.0) - PostgreSQL async adapter

## Quick Start

### Basic Plugin

```python
from mm_tools.plugins import BasePlugin
from mmpy_bot import listen_to

class MyPlugin(BasePlugin):
    @listen_to("hello")
    async def hello_handler(self, message):
        self.driver.reply_to(message, "Hello! How can I help you?")
```

### Interactive Dialog

```python
from mm_tools.dialogs import Dialog, InputTextElement, StaticSelectElement, ElementOption
from mm_tools.sessions import stateful_dialog

class MyPlugin(BasePlugin):
    @stateful_dialog()
    async def show_dialog(self, event, session):
        elements = [
            InputTextElement("Name", "name", placeholder="Enter your name"),
            StaticSelectElement("Department", "dept", [
                ElementOption("Engineering", "eng"),
                ElementOption("Marketing", "mkt")
            ])
        ]
        
        dialog = Dialog(
            title="User Information",
            action_id="submit_info", 
            elements=elements,
            trigger_id=event.trigger_id,
            url="http://your-bot-url.com",
            session_id=session.session_id
        )
        
        self.driver.posts.open_dialog(dialog.to_dict())
```

### Rich Attachments

```python
from mm_tools.attachments import Attachment, Button, Field

class MyPlugin(BasePlugin):
    async def send_rich_message(self, channel_id):
        attachment = Attachment(
            title="System Status",
            color="good",
            fields=[
                Field("CPU Usage", "45%", short=True),
                Field("Memory", "2.1GB", short=True)
            ],
            actions=[
                Button("Restart", "restart_action", "http://your-bot-url.com")
            ]
        )
        
        self.driver.create_post(
            channel_id=channel_id,
            message="Server Status Report",
            props=attachment.to_dict()
        )
```

## Architecture

### Plugin System

The `BasePlugin` class provides:

- **Logging**: Structured logging with optional raw JSON output
- **Sentry Integration**: Performance monitoring and error tracking
- **Message Utilities**: Send, update, delete messages and files
- **User Management**: Retrieve user info and send direct messages
- **State Management**: Built-in state machine for complex workflows

### Session Management

Stateful dialogs are managed through decorators:

```python
@stateful_dialog()  # For dialog submissions
@stateful_attachment()  # For attachment interactions
```

Sessions are automatically created and passed to your handlers, providing persistent storage across interactions.

### Database Integration

The toolkit includes async database support with Peewee ORM:

```python
from mm_tools.plugins.cache_db.models import BaseModel

class CustomModel(BaseModel):
    name = CharField()
    data = JSONField()
    
    class Meta:
        table_name = 'custom_data'
```

## Project Structure

```
mm_tools/
├── attachments/          # Rich message attachments and interactive elements
│   └── base.py          # Button, Select, Field, Attachment classes
├── dialogs/             # Interactive dialog system
│   ├── base.py          # Dialog elements (inputs, selects, etc.)
│   └── custom_dialogs.py # Pre-built dialog templates
├── plugins/             # Plugin framework
│   ├── base_plugin.py   # Core plugin base class
│   ├── state_machine.py # State management utilities
│   └── cache_db/        # Database models and migrations
└── sessions/            # Session management
    └── sessions.py      # SQLite-based session storage
```

## Development

### Setting up Development Environment

1. Clone the repository:
   ```bash
   git clone https://github.com/Sadisms/mm-tools.git
   cd mm-tools
   ```

2. Install in development mode:
   ```bash
   pip install -e .
   ```

3. Install development dependencies:
   ```bash
   pip install -r requirements.txt
   ```

### Running Tests

```bash
python -m pytest tests/
```

### Database Migrations

The toolkit includes migration support through peewee-moves:

```bash
# Create a new migration
python -m peewee_moves create your_migration_name

# Apply migrations  
python -m peewee_moves migrate
```

## Advanced Usage

### Custom Dialog Elements

Create custom input elements by extending `DialogElement`:

```python
from mm_tools.dialogs.base import DialogElement

class DatePickerElement(DialogElement):
    def __init__(self, display_name, element_id, **kwargs):
        super().__init__()
        self.type = 'text'
        self.subtype = 'date'
        self.display_name = display_name
        self.element_id = element_id
```

### State Machine Integration

Use the built-in state machine for complex workflows:

```python
from mm_tools.plugins.state_machine import StateMachine

class WorkflowPlugin(BasePlugin):
    state = StateMachine()
    
    async def start_workflow(self, event):
        self.state.set_state(event.user_id, "collecting_info")
        # Continue workflow...
```

## API Reference

### BasePlugin

Core plugin class with utilities for Mattermost interaction.

**Key Methods:**
- `update_message(post_id, message, props)` - Update existing message
- `delete_message(post_id)` - Delete a message  
- `get_user_info(user_id)` - Get user details
- `direct_post(user_id, message)` - Send direct message
- `upload_file(channel_id, files)` - Upload files

### Dialog System

Create interactive dialogs with various input elements.

**Available Elements:**
- `InputTextElement` - Single line text input
- `InputTextAreaElement` - Multi-line text input  
- `StaticSelectElement` - Dropdown with predefined options
- `SelectUserElement` - User selector
- `SelectChannelElement` - Channel selector
- `CheckBoxElement` - Boolean checkbox
- `RadioButtonElement` - Radio button group

### Attachment System

Rich message formatting with interactive elements.

**Components:**
- `Attachment` - Main attachment container
- `Button` - Interactive buttons
- `Select` - Dropdown selectors
- `Field` - Key-value display fields

## Resources

- [Mattermost Bot Framework](https://github.com/attzonko/mmpy_bot) - The underlying bot framework
- [Mattermost API Documentation](https://api.mattermost.com/) - Official API reference
- [Peewee ORM Documentation](http://docs.peewee-orm.com/) - Database ORM documentation
- [Mattermost Plugin Development](https://developers.mattermost.com/) - Official developer resources