"""
modules/config.py

Version: 1.0.0
Date: 2025-11-29
Purpose: Configuration and constants for SIMA Manager
Project: SIMA

ADDED: Configuration class
ADDED: Language detection patterns
"""

from pathlib import Path

class Config:
    """Application configuration"""
    SIMA_ROOT = Path("./sima")
    EXPORT_DIR = Path("./exports")
    ARCHIVE_DIR = Path("./archives")
    MAX_FILE_LINES = 350
    SUPPORTED_FORMATS = ["md", "json"]

# Language detection patterns for code blocks
LANGUAGE_PATTERNS = {
    'python': r'```python\n',
    'javascript': r'```(?:javascript|js)\n',
    'typescript': r'```(?:typescript|ts)\n',
    'java': r'```java\n',
    'go': r'```go\n',
    'rust': r'```rust\n',
    'c': r'```c\n',
    'cpp': r'```(?:cpp|c\+\+)\n',
    'csharp': r'```(?:csharp|cs)\n',
    'ruby': r'```ruby\n',
    'php': r'```php\n',
    'swift': r'```swift\n',
    'kotlin': r'```kotlin\n',
    'sql': r'```sql\n',
    'bash': r'```(?:bash|sh)\n',
    'yaml': r'```ya?ml\n',
}
