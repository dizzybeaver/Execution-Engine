# config_state.py

**Version:** 2025-12-09_1  
**Module:** Config  
**Layer:** Core  
**Lines:** 35

---

## Purpose

Configuration state management dataclasses for tracking configuration versions, history, and state.

---

## Dataclasses

### ConfigurationVersion

**Purpose:** Track configuration version history entry

**Definition:**
```python
@dataclass
class ConfigurationVersion:
    """Track configuration version history."""
    version: str
    timestamp: float
    changes: Dict[str, Any]
```

**Attributes:**
- `version: str` - Version identifier (e.g., '1.0.0')
- `timestamp: float` - Unix timestamp of version
- `changes: Dict[str, Any]` - Changes made in this version

**Usage:**
```python
from config.config_state import ConfigurationVersion

# Create version entry
version = ConfigurationVersion(
    version='1.0.1',
    timestamp=time.time(),
    changes={'reloaded': True, 'preset': 'debug'}
)

# Access attributes
print(f"Version: {version.version}")
print(f"Time: {datetime.fromtimestamp(version.timestamp)}")
print(f"Changes: {version.changes}")
```

**Example in Version History:**
```python
version_history = [
    ConfigurationVersion(
        version='1.0.0',
        timestamp=1638360000.0,
        changes={'initialized': True}
    ),
    ConfigurationVersion(
        version='1.0.1',
        timestamp=1638360300.0,
        changes={'preset': 'debug'}
    ),
    ConfigurationVersion(
        version='1.0.2',
        timestamp=1638360600.0,
        changes={'reloaded': True}
    )
]
```

---

### ConfigurationState

**Purpose:** Track current configuration state

**Definition:**
```python
@dataclass
class ConfigurationState:
    """Track configuration state."""
    current_version: str = "1.0.0"
    active_preset: Optional[str] = None
    version_history: List[ConfigurationVersion] = field(default_factory=list)
    pending_changes: Dict[str, Any] = field(default_factory=dict)
    last_reload_time: float = 0.0
    reload_count: int = 0
    validation_failures: int = 0
```

**Attributes:**
- `current_version: str` - Current version (default: "1.0.0")
- `active_preset: Optional[str]` - Active preset name (None if none)
- `version_history: List[ConfigurationVersion]` - Version history list
- `pending_changes: Dict[str, Any]` - Changes pending application
- `last_reload_time: float` - Unix timestamp of last reload
- `reload_count: int` - Number of reloads performed
- `validation_failures: int` - Count of validation failures

**Default Values:**
```python
state = ConfigurationState()
# current_version: "1.0.0"
# active_preset: None
# version_history: []
# pending_changes: {}
# last_reload_time: 0.0
# reload_count: 0
# validation_failures: 0
```

**Usage:**
```python
from config.config_state import ConfigurationState

# Create state
state = ConfigurationState()

# Update version
state.current_version = "1.1.0"

# Set active preset
state.active_preset = "debug"

# Track reload
state.last_reload_time = time.time()
state.reload_count += 1

# Add pending changes
state.pending_changes['cache.ttl'] = 600

# Add version history
state.version_history.append(
    ConfigurationVersion(
        version="1.1.0",
        timestamp=time.time(),
        changes={'preset': 'debug'}
    )
)

# Track validation failure
state.validation_failures += 1
```

---

## State Tracking Patterns

### Version History

**Pattern:**
```python
def record_version_change(state: ConfigurationState, 
                         changes: Dict[str, Any]) -> None:
    """Record a version change in history."""
    # Increment version
    major, minor, patch = state.current_version.split('.')
    new_version = f"{major}.{minor}.{int(patch) + 1}"
    state.current_version = new_version
    
    # Create version entry
    version = ConfigurationVersion(
        version=new_version,
        timestamp=time.time(),
        changes=changes
    )
    
    # Add to history
    state.version_history.append(version)
    
    # Keep only last 10 versions
    if len(state.version_history) > 10:
        state.version_history = state.version_history[-10:]
```

### Reload Tracking

**Pattern:**
```python
def track_reload(state: ConfigurationState) -> None:
    """Track configuration reload."""
    state.last_reload_time = time.time()
    state.reload_count += 1
    
    # Record in version history
    record_version_change(state, {'reloaded': True})
```

### Validation Tracking

**Pattern:**
```python
def track_validation(state: ConfigurationState, 
                    validation_result: Dict[str, Any]) -> None:
    """Track validation result."""
    if not validation_result.get('valid', True):
        state.validation_failures += 1
        
        # Record in version history
        record_version_change(state, {
            'validation_failed': True,
            'errors': validation_result.get('errors', [])
        })
```

---

## State Lifecycle

### Initialization

**Pattern:**
```python
# In ConfigurationCore.__init__()
self._state = ConfigurationState()

# Initial version recorded
initial_version = ConfigurationVersion(
    version=self._state.current_version,
    timestamp=time.time(),
    changes={'initialized': True}
)
self._state.version_history.append(initial_version)
```

### Preset Switch

**Pattern:**
```python
# In switch_preset()
def switch_preset(preset_name: str):
    # ... apply preset ...
    
    # Update state
    state.active_preset = preset_name
    
    # Record version
    record_version_change(state, {
        'preset': preset_name,
        'applied_count': len(preset_config)
    })
```

### Reload

**Pattern:**
```python
# In reload_config()
def reload_config():
    # ... reload logic ...
    
    # Update state
    track_reload(state)
    
    return {
        'success': True,
        'reload_count': state.reload_count,
        'last_reload': state.last_reload_time
    }
```

---

## State Reporting

### Get State Summary

**Pattern:**
```python
def get_state_summary(state: ConfigurationState) -> Dict[str, Any]:
    """Get human-readable state summary."""
    return {
        'version': state.current_version,
        'preset': state.active_preset or 'none',
        'reload_count': state.reload_count,
        'last_reload': datetime.fromtimestamp(state.last_reload_time).isoformat()
                       if state.last_reload_time > 0 else 'never',
        'validation_failures': state.validation_failures,
        'pending_changes': len(state.pending_changes),
        'version_history_size': len(state.version_history)
    }
```

### Get Version History

**Pattern:**
```python
def get_version_history(state: ConfigurationState, 
                       limit: int = 10) -> List[Dict[str, Any]]:
    """Get formatted version history."""
    history = []
    for version in state.version_history[-limit:]:
        history.append({
            'version': version.version,
            'timestamp': datetime.fromtimestamp(version.timestamp).isoformat(),
            'changes': version.changes
        })
    return history
```

---

## State Persistence

### Save State (Future)

**Pattern:**
```python
def save_state(state: ConfigurationState, filepath: str) -> None:
    """Save state to file (future enhancement)."""
    state_dict = {
        'version': state.current_version,
        'preset': state.active_preset,
        'reload_count': state.reload_count,
        'last_reload': state.last_reload_time,
        'validation_failures': state.validation_failures,
        'version_history': [
            {
                'version': v.version,
                'timestamp': v.timestamp,
                'changes': v.changes
            }
            for v in state.version_history
        ]
    }
    
    with open(filepath, 'w') as f:
        json.dump(state_dict, f, indent=2)
```

### Load State (Future)

**Pattern:**
```python
def load_state(filepath: str) -> ConfigurationState:
    """Load state from file (future enhancement)."""
    with open(filepath, 'r') as f:
        state_dict = json.load(f)
    
    state = ConfigurationState()
    state.current_version = state_dict['version']
    state.active_preset = state_dict.get('preset')
    state.reload_count = state_dict.get('reload_count', 0)
    state.last_reload_time = state_dict.get('last_reload', 0.0)
    state.validation_failures = state_dict.get('validation_failures', 0)
    
    # Reconstruct version history
    for v_dict in state_dict.get('version_history', []):
        version = ConfigurationVersion(
            version=v_dict['version'],
            timestamp=v_dict['timestamp'],
            changes=v_dict['changes']
        )
        state.version_history.append(version)
    
    return state
```

---

## Usage in ConfigurationCore

### Integration Example

```python
class ConfigurationCore:
    def __init__(self):
        self._config = {}
        self._state = ConfigurationState()  # State tracking
        # ... other initialization ...
    
    def reload_config(self):
        # ... reload logic ...
        
        # Update state
        self._state.last_reload_time = time.time()
        self._state.reload_count += 1
        
        # Record version
        version = ConfigurationVersion(
            version=self._state.current_version,
            timestamp=time.time(),
            changes={'reloaded': True}
        )
        self._state.version_history.append(version)
    
    def get_state(self):
        return {
            'version': self._state.current_version,
            'preset': self._state.active_preset,
            'reload_count': self._state.reload_count,
            'validation_failures': self._state.validation_failures
        }
```

---

## Performance

### Memory Usage

**ConfigurationVersion:**
- Instance: ~200 bytes
- 10 versions: ~2KB
- 100 versions: ~20KB

**ConfigurationState:**
- Instance: ~500 bytes
- With 10 versions: ~2.5KB
- With 100 versions: ~21KB

### Operation Timing

| Operation | Time | Notes |
|-----------|------|-------|
| Create ConfigurationState | ~2μs | Initialization |
| Add version to history | ~5μs | List append |
| Update state fields | ~1μs | Attribute assignment |
| Get state summary | ~10μs | Dict creation |

---

## Dependencies

**Standard Library:**
- `dataclasses` - Dataclass decorator and field
- `typing` - Type hints (Dict, Any, Optional, List)

**No External Dependencies**

---

## Changelog

### 2025-12-09_1
- Refactored into config module
- Simplified dataclasses
- Removed tier-specific fields
- Added comprehensive documentation

---

**END OF DOCUMENTATION**
