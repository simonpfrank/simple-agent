# Phase 4: Raspberry Pi Integration

**Overview**: Deploy Simple Agent on Raspberry Pi with local LLM support, voice I/O, and GPIO integration for edge computing scenarios.

**Status**: 🔴 Not Started
**Effort**: Estimated 12-16 hours for Phase 4.1
**Dependencies**: RPi.GPIO, Ollama, voice libraries, local embeddings

---

## Phase 4.1: Local LLM & Pi Optimization 🔴 NOT STARTED

**Status**: 🔴 Not Started
**Effort**: Estimated 6-8 hours
**Tests**: 0/? (not started)

### Planned Features:

#### 1. Ollama Integration
- **Local LLM Support**: Run open-source models (Llama 2, Mistral, etc.) on Pi
- **Model Management**: Download, list, and switch models
- **Ollama Server**: Connect to local Ollama instance
- **Configuration**: Set Ollama endpoint in config.yaml

#### 2. Pi-Optimized Configuration
- **Memory Management**: Config options for limited RAM
- **Tool Filtering**: Auto-disable expensive tools (browser, large datasets)
- **Batch Processing**: Queue-based execution for resource-constrained ops
- **Caching**: Cache embeddings and model outputs locally

#### 3. Local Embeddings
- **Sentence Transformers**: Use lightweight embeddings for RAG
- **Vector Storage**: Keep Chroma DB on local storage
- **Efficient Similarity**: Pre-compute and cache vectors

#### 4. Resource Monitoring
- **Memory Tracking**: Monitor RAM usage
- **CPU Throttling**: Detect and adapt to thermal constraints
- **Timeout Management**: Extend timeouts for slower hardware

### Configuration Example:
```yaml
llm:
  provider: ollama
  ollama:
    base_url: http://localhost:11434
    model: llama2  # Run locally

rag:
  embeddings:
    model: all-MiniLM-L6-v2  # Lightweight model
  storage: /home/pi/.simple-agent/chroma

agent_optimization:
  memory_limit: 512mb
  disable_tools: [browser_automation, image_analysis]
  cache_embeddings: true
```

### Files to Create:
- `simple_agent/core/ollama_provider.py` - Ollama LLM provider
- `simple_agent/core/pi_optimizer.py` - Pi-specific optimizations
- `tests/unit/test_ollama_provider.py` - Unit tests
- `tests/integration/test_pi_integration.py` - Integration tests

### Tests Needed:
- Ollama connection tests
- Memory usage tracking
- Embedding caching
- Tool filtering logic

---

## Phase 4.2: Voice I/O 🔴 BACKLOG

**Status**: 🔴 Backlog
**Effort**: Estimated 4-6 hours
**Dependencies**: vosk or whisper.cpp for input, pyttsx3 for output

### Planned Features:

#### 1. Voice Input
- **Microphone Listening**: Capture audio from Pi microphone
- **Speech-to-Text**: Convert to text (Whisper or Vosk)
- **Keyword Spotting**: Detect wake words
- **Continuous Listening**: Background monitoring

#### 2. Voice Output
- **Text-to-Speech**: Speak agent responses
- **Voice Selection**: Multiple voice options
- **Audio Output**: Play through Pi speakers

#### 3. Voice Commands
- **Agent Invocation**: "Run researcher"
- **Query Input**: "What is quantum computing?"
- **Tool Control**: "Stop listening"

### Configuration:
```yaml
voice:
  enabled: true
  input:
    provider: whisper  # or vosk for lighter
    language: en
  output:
    provider: pyttsx3
    voice: female
  wake_word: hey agent
```

---

## Phase 4.3: GPIO & Hardware Tools 🔴 BACKLOG

**Status**: 🔴 Backlog
**Effort**: Estimated 5-8 hours
**Dependencies**: RPi.GPIO

### Planned Features:

#### 1. GPIO Control
- **Pin Configuration**: Set up GPIO pins from YAML
- **Digital I/O**: Read/write pins
- **PWM Control**: Pulse width modulation for motors/LEDs
- **Interrupt Handling**: React to pin changes

#### 2. Hardware Tools
- **LED Control Tool**: Turn LEDs on/off, blink, fade
- **Motor Control Tool**: Speed/direction control
- **Sensor Reading Tool**: Temperature, humidity, motion sensors
- **Relay Control Tool**: Switch high-voltage devices

#### 3. Safety
- **Voltage Limits**: Prevent damage to pins
- **Current Limiting**: Prevent overcurrent
- **Timeout Protection**: Auto-disable on error
- **Cleanup**: Reset pins on shutdown

### Configuration:
```yaml
gpio:
  pins:
    led_red:
      pin: 17
      mode: output
      initial: low
    button:
      pin: 27
      mode: input
      pull: up

hardware_tools:
  - led_red
  - button
```

### Example Tool:
```python
# Agent can use: /hardware led_red on/off
/hardware led_red on      # Turn LED on
/hardware led_red blink --duration 2  # Blink for 2 seconds
```

---

## Phase 4.4: Edge Computing Patterns 🔴 BACKLOG

**Status**: 🔴 Backlog
**Effort**: Estimated 3-4 hours

### Planned Features:

#### 1. Offline Mode
- **Cache Everything**: Pre-cache tools, models, embeddings
- **No Network Fallback**: Continue working if network drops
- **Sync Queue**: Queue remote operations for later sync

#### 2. Batch Processing
- **Job Queue**: Queue multiple queries
- **Off-Peak Execution**: Run expensive ops at night
- **Scheduled Tasks**: Cron-like task execution

#### 3. Monitoring & Logging
- **System Health**: CPU, memory, disk usage
- **Agent Performance**: Latency, success rate
- **Local Logging**: Write to SD card with rotation

#### 4. Updates & Deployment
- **Model Updates**: Download new models safely
- **Code Updates**: Git pull with verification
- **Configuration Sync**: Cloud -> local config

---

## Next Steps

### Immediate (if context is lost, start here):
1. ✅ Phase 3 extensions created (phase_3_extensions.md)
2. ✅ This phase_4_raspberrypi.md created
3. 🔴 Still need to create new simplified progress.md
4. 🔴 Still need to update README.md with examples

### Phase 4.1 Implementation Plan:
1. Create `simple_agent/core/ollama_provider.py` with Ollama LLM support
2. Create `simple_agent/core/pi_optimizer.py` for resource optimization
3. Add Ollama config to config.yaml template
4. Write unit tests for provider
5. Write integration tests with actual Ollama instance

### Phase 4.2-4.4 (Future):
- Voice I/O: Integrate Whisper/Vosk and pyttsx3
- GPIO: RPi.GPIO library integration
- Edge patterns: Caching, offline mode, job queue

### Dependencies to Add (requirements.txt):
- `ollama` - Ollama Python client
- `RPi.GPIO` - GPIO control (only install on Pi)
- `vosk` or `openai-whisper` - Speech recognition
- `pyttsx3` - Text-to-speech
- `sentence-transformers` - Local embeddings
