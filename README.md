# ELARA - Personal AI Voice Assistant for Windows

ELARA is a sophisticated personal AI voice assistant designed for Windows that brings natural voice interaction to your desktop computing experience. Built with privacy and security at its core, ELARA operates locally for voice processing while leveraging powerful AI models for intelligent understanding and action execution.

## 🌟 Features

### Core Capabilities
- **Natural Voice Interaction**: Speak naturally to ELARA without memorizing specific commands
- **Wake Word Activation**: Simply say "Hey Elara" to activate the assistant
- **Voice Authentication**: Secure speaker verification ensures only authorized users can access sensitive features
- **Windows Automation**: Control applications, manage windows, adjust system settings, and more
- **File Management**: Create, read, edit, and organize files with voice commands
- **Browser Automation**: Control web browsers, search the internet, and navigate websites
- **Coding Assistant**: Create projects, write code, debug errors, and manage development workflows
- **Git Integration**: Manage version control with natural language commands
- **Memory System**: ELARA remembers your preferences, workspaces, and frequently used information
- **Modern GUI**: Beautiful dark-themed desktop interface with real-time status updates

### Security & Privacy
- **Local-First Architecture**: Voice processing happens locally on your machine
- **Permission System**: Multi-level permission controls for different types of actions
- **Confirmation Engine**: Sensitive operations require explicit user confirmation
- **Workspace Security**: File operations restricted to approved directories
- **Audit Logging**: Comprehensive logging of all actions for security monitoring
- **No Secret Storage**: API keys and credentials never stored in project files

## 🏗️ Architecture

ELARA follows a secure, modular architecture:

```
USER VOICE
↓
VOICE ACTIVITY DETECTION
↓
WAKE WORD DETECTION
↓
SPEAKER VERIFICATION
↓
SPEECH TO TEXT
↓
AI UNDERSTANDING
↓
STRUCTURED ACTION/PLAN
↓
SECURITY + PERMISSION ENGINE
↓
ACTION REGISTRY
↓
EXECUTOR
↓
RESULT
↓
AI RESPONSE
↓
TEXT TO SPEECH
```

## 📁 Project Structure

```
ELARA/
│
├── app/
│   ├── main.py                 # Application entry point
│   ├── config/
│   │   ├── settings.py         # Configuration management
│   │   └── constants.py        # Application constants
│   ├── core/
│   │   ├── assistant.py        # Main assistant logic
│   │   ├── event_bus.py        # Event system
│   │   ├── state.py            # State machine
│   │   └── lifecycle.py        # Application lifecycle
│   ├── voice/
│   │   ├── microphone.py       # Audio input handling
│   │   ├── vad.py              # Voice activity detection
│   │   ├── speech_to_text.py   # Speech recognition
│   │   └── audio.py            # Audio utilities
│   ├── wakeword/
│   │   └── detector.py         # Wake word detection
│   ├── authentication/
│   │   ├── enrollment.py       # Voice enrollment
│   │   ├── speaker_verification.py  # Voice authentication
│   │   └── voice_profile.py    # Voice profile management
│   ├── ai/
│   │   ├── provider.py         # AI provider abstraction
│   │   ├── client.py           # AI client implementation
│   │   ├── intent.py           # Intent recognition
│   │   ├── planner.py          # Action planning
│   │   ├── schemas.py          # Data schemas
│   │   └── response.py         # Response generation
│   ├── actions/
│   │   ├── registry.py         # Action registry
│   │   ├── executor.py         # Action execution
│   │   ├── permissions.py      # Permission management
│   │   └── confirmation.py     # Confirmation handling
│   ├── windows/
│   │   ├── applications.py     # Application control
│   │   ├── windows.py          # Window management
│   │   ├── volume.py           # Volume control
│   │   ├── screenshots.py      # Screen capture
│   │   └── system.py           # System operations
│   ├── files/
│   │   ├── manager.py          # File operations
│   │   ├── validator.py        # Path validation
│   │   └── workspace.py         # Workspace management
│   ├── browser/
│   │   ├── manager.py          # Browser control
│   │   ├── navigation.py       # Web navigation
│   │   └── automation.py       # Web automation
│   ├── coding/
│   │   ├── workspace.py        # Coding workspace
│   │   ├── project_manager.py  # Project management
│   │   ├── code_editor.py      # Code editor integration
│   │   ├── runner.py           # Code execution
│   │   └── error_analyzer.py   # Error analysis
│   ├── git/
│   │   ├── manager.py          # Git operations
│   │   ├── status.py           # Git status
│   │   ├── commit.py           # Commit operations
│   │   └── github.py           # GitHub integration
│   ├── memory/
│   │   ├── database.py         # Database management
│   │   ├── models.py           # Database models
│   │   ├── memory.py           # Memory operations
│   │   └── preferences.py      # User preferences
│   ├── security/
│   │   ├── policy.py           # Security policies
│   │   ├── sanitizer.py        # Input sanitization
│   │   ├── audit.py            # Audit logging
│   │   └── secrets.py          # Secret management
│   ├── tts/
│   │   └── speaker.py          # Text-to-speech
│   ├── ui/
│   │   ├── main_window.py      # Main window
│   │   ├── dashboard.py        # Dashboard UI
│   │   ├── settings.py         # Settings UI
│   │   ├── history.py          # History UI
│   │   ├── voice_setup.py      # Voice setup UI
│   │   └── widgets/            # Custom widgets
│   └── utils/
│       ├── logger.py           # Logging system
│       ├── paths.py            # Path utilities
│       └── helpers.py          # Helper functions
│
├── tests/                       # Test suite
├── data/                        # Data storage
├── logs/                        # Log files
├── workspace/                   # Default workspace
├── models/                      # Model storage
├── scripts/                     # Utility scripts
├── .env.example                 # Environment configuration template
├── .gitignore                   # Git ignore rules
├── requirements.txt             # Python dependencies
├── README.md                    # This file
├── run.py                       # Quick start script
└── LICENSE                      # License file
```

## 🚀 Installation

### Prerequisites
- Python 3.12 or higher
- Windows 10 or Windows 11
- Microphone and speakers
- Administrator access (for some system operations)

### Step-by-Step Installation

1. **Clone the repository**
   ```bash
   git clone https://github.com/yourusername/voice-assistants-Elara.git
   cd voice-assistants-Elara
   ```

2. **Create a virtual environment**
   ```bash
   python -m venv .venv
   .venv\Scripts\activate
   ```

3. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

4. **Install Playwright browsers**
   ```bash
   playwright install
   ```

5. **Configure environment variables**
   ```bash
   copy .env.example .env
   ```

6. **Edit .env file** with your configuration:
   - Set your AI provider API key
   - Configure audio devices if needed
   - Set workspace directory
   - Adjust other settings as desired

7. **Run voice enrollment** (first launch only)
   ```bash
   python run.py
   ```
   Follow the on-screen prompts to record your voice for authentication.

8. **Start ELARA**
   ```bash
   python run.py
   ```

## 🎯 Usage

### Basic Commands

**Wake ELARA:**
```
"Hey Elara"
```

**Application Control:**
```
"Open Chrome"
"Close Discord"
"Minimize VS Code"
"Maximize the browser"
```

**System Control:**
```
"Turn volume down"
"Mute the speakers"
"Take a screenshot"
"Lock the computer"
```

**File Operations:**
```
"Open my Downloads folder"
"Create a folder called Projects"
"Find Python files"
"Open the last document"
```

**Web Browsing:**
```
"Search Google for Python decorators"
"Open YouTube"
"Go back"
"Open a new tab"
```

**Coding Assistance:**
```
"Create a Python project called calculator"
"Write a function to add two numbers"
"Run the program"
"Read the error"
"Fix the bug"
"Run the tests"
```

**Git Operations:**
```
"Check Git status"
"Create a branch called feature-login"
"Commit these changes"
"Push to GitHub"
```

**Memory & Preferences:**
```
"Remember my Python projects are in D:\Projects\Python"
"What do you remember about my workspace?"
"Forget my Python projects folder"
```

### First-Run Experience

When you first launch ELARA, you'll be guided through:

1. **Welcome Screen**: Introduction to ELARA
2. **Microphone Setup**: Select and test your microphone
3. **Speaker Setup**: Select and test your speakers
4. **Voice Enrollment**: Record phrases for voice authentication
5. **Wake Word Test**: Test wake word detection
6. **AI Configuration**: Set up your AI provider
7. **Workspace Selection**: Choose your default workspace
8. **Application Discovery**: Scan for installed applications
9. **Security Configuration**: Set up security preferences
10. **Final Test**: Test the complete system

## 🔒 Security

### Permission Levels

ELARA uses a four-tier permission system:

- **LEVEL 0 (SAFE)**: No confirmation required
  - Opening applications
  - Reading system information
  - Opening websites

- **LEVEL 1 (MODERATE)**: May require confirmation
  - Creating files
  - Modifying project files
  - Installing dependencies

- **LEVEL 2 (SENSITIVE)**: Requires confirmation
  - Deleting files
  - Moving files
  - Modifying system settings

- **LEVEL 3 (CRITICAL)**: Explicit confirmation required
  - System shutdown/restart
  - Mass file operations
  - Destructive system commands

### Security Features

- **Voice Authentication**: Only authorized users can execute sensitive commands
- **Workspace Restrictions**: File operations limited to approved directories
- **Path Sanitization**: Prevents path traversal attacks
- **Command Validation**: All commands validated before execution
- **Audit Logging**: Complete audit trail of all actions
- **Secret Protection**: API keys and credentials never exposed or logged

## 🛠️ Configuration

### Environment Variables

Key configuration options in `.env`:

```bash
# AI Provider
AI_PROVIDER=openai
AI_API_KEY=your_api_key_here
AI_MODEL=gpt-4

# Wake Word
ELARA_WAKE_WORD=Hey Elara

# Voice Recognition
ELARA_VOICE_THRESHOLD=0.75

# Speech Recognition
ELARA_STT_MODEL=base
ELARA_STT_LANGUAGE=en

# Text-to-Speech
ELARA_TTS_MODEL=en_US-lessac-medium
ELARA_TTS_SPEED=1.0

# Security
ELARA_WORKSPACE=./workspace
ELARA_ENABLE_WORKSPACE_RESTRICTION=true
```

### Settings GUI

Access the Settings panel through the ELARA interface to configure:
- Audio devices
- Voice settings
- AI provider
- Security preferences
- Workspace directories
- Application aliases
- UI appearance

## 🧪 Testing

Run the test suite:

```bash
pytest tests/
```

Run with coverage:

```bash
pytest --cov=app tests/
```

## 📝 Development

### Code Style

ELARA follows these code quality standards:
- **Black**: Code formatting
- **isort**: Import sorting
- **flake8**: Linting
- **mypy**: Type checking

Format code:
```bash
black app/
isort app/
```

Run linting:
```bash
flake8 app/
mypy app/
```

### Adding New Features

1. Follow the existing architecture patterns
2. Add appropriate database models if needed
3. Implement permission checks for sensitive operations
4. Add comprehensive logging
5. Write tests for new functionality
6. Update documentation

## 🐛 Troubleshooting

### Common Issues

**Microphone not detected:**
- Check microphone permissions in Windows settings
- Ensure microphone is not in use by another application
- Try different audio device in settings

**Speech recognition inaccurate:**
- Improve microphone positioning
- Reduce background noise
- Consider using a larger STT model in settings

**Voice authentication fails:**
- Re-enroll your voice in settings
- Check microphone quality
- Adjust voice threshold in settings

**AI API errors:**
- Verify API key in .env file
- Check internet connection
- Verify API quota/billing status

**Browser automation fails:**
- Ensure Playwright browsers are installed
- Check browser permissions
- Verify browser is not blocked by firewall

## 📄 License

This project is licensed under the MIT License - see the LICENSE file for details.

## 🤝 Contributing

Contributions are welcome! Please follow these guidelines:

1. Fork the repository
2. Create a feature branch
3. Make your changes with proper testing
4. Submit a pull request with description

## 🙏 Acknowledgments

- **faster-whisper**: Fast speech recognition
- **openWakeWord**: Efficient wake word detection
- **SpeechBrain**: Speaker verification
- **PySide6**: Modern GUI framework
- **Playwright**: Browser automation
- **SQLAlchemy**: Database ORM

## 📞 Support

For issues, questions, or contributions:
- GitHub Issues: Report bugs and request features
- Documentation: Check the `/docs` folder for detailed guides
- Community: Join our Discord community (link coming soon)

## 🔮 Future Roadmap

Planned features for future releases:
- [ ] Calendar integration
- [ ] Email management
- [ ] Smart home control
- [ ] Music/media control
- [ ] Weather information
- [ ] Local computer search
- [ ] Multiple AI model support
- [ ] Offline LLM mode
- [ ] Plugin system
- [ ] Mobile companion app
- [ ] Multi-user support

---

**ELARA** - Your Personal AI Voice Assistant for Windows

Built with ❤️ for productive, secure, and natural voice computing.
