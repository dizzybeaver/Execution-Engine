# Python Core Concepts Index

**Version:** 1.0.0  
**Date:** 2025-12-31  
**Purpose:** Index of fundamental Python concepts and language features

## Core List

| REF-ID | Title | Difficulty | Lines | Description |
|--------|-------|-----------|-------|-------------|
| CR-PY-01 | Decorators | Intermediate | 85 | Core decorator concepts and implementation |
| CR-PY-02 | Context Managers | Beginner | 65 | Understanding `with` statements |
| CR-PY-03 | Generators | Intermediate | 70 | Iterator patterns and generator expressions |
| CR-PY-04 | Metaclasses | Advanced | 90 | Class creation and metaclass programming |
| CR-PY-05 | Descriptors | Advanced | 75 | Attribute access protocols |

## Core Categories

### Language Fundamentals (2)
- CR-PY-02 (Context Managers)
- CR-PY-03 (Generators)

### Advanced OOP (3)
- CR-PY-01 (Decorators)
- CR-PY-04 (Metaclasses)
- CR-PY-05 (Descriptors)

## Learning Path

### Beginner Core (Essential knowledge)
1. **CR-PY-02 - Context Managers** (65 lines)
   - Resource management basics
   - `with` statement usage

2. **CR-PY-03 - Generators** (70 lines)
   - Iterator protocol fundamentals
   - Generator expressions and functions

### Intermediate Core (Code enhancement)
3. **CR-PY-01 - Decorators** (85 lines)
   - Function and class modification
   - Common decorator patterns

### Advanced Core (Language internals)
4. **CR-PY-05 - Descriptors** (75 lines)
   - Attribute access protocols
   - Property implementation

5. **CR-PY-04 - Metaclasses** (90 lines)
   - Class creation process
   - Advanced metaprogramming

## Core Concepts Hierarchy

```
Python Core
├── Language Fundamentals
│   ├── Context Managers (CR-PY-02)
│   └── Generators (CR-PY-03)
├── Code Enhancement
│   └── Decorators (CR-PY-01)
└── Advanced OOP
    ├── Descriptors (CR-PY-05)
    └── Metaclasses (CR-PY-04)
```

## Implementation Details

### CR-PY-01: Decorators Fundamentals
```python
# Basic decorator
def my_decorator(func):
    def wrapper():
        print("Before function call")
        result = func()
        print("After function call")
        return result
    return wrapper

# Usage
@my_decorator
def say_hello():
    return "Hello"
```

### CR-PY-02: Context Managers Protocol
```python
class MyContext:
    def __enter__(self):
        print("Entering context")
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        print("Exiting context")
        return False

# Usage with 'with'
with MyContext() as ctx:
    print("Inside context")
```

### CR-PY-03: Generator Patterns
```python
# Generator function
def countdown(n):
    while n > 0:
        yield n
        n -= 1

# Generator expression
squares = (x*x for x in range(10))
```

### CR-PY-04: Metaclass Basics
```python
class Meta(type):
    def __new__(cls, name, bases, namespace):
        print(f"Creating class {name}")
        return type.__new__(cls, name, bases, namespace)

class MyClass(metaclass=Meta):
    pass
```

### CR-PY-05: Descriptor Protocol
```python
class Descriptor:
    def __get__(self, obj, objtype=None):
        return f"Getting value from {obj}"
    
    def __set__(self, obj, value):
        print(f"Setting {value} on {obj}")

class MyClass:
    attr = Descriptor()
```

## Related Patterns and Anti-patterns

### Decorators (CR-PY-01)
- **Patterns**: PAT-PY-04 (Decorator patterns), PAT-PY-05 (Context Managers)
- **Lessons**: LESS-PY-01 (Metaclass gotchas)

### Context Managers (CR-PY-02)
- **Patterns**: PAT-PY-05 (Context managers pattern)
- **Anti-patterns**: AP-PY-01 (Global mutation)

### Generators (CR-PY-03)
- **Patterns**: PAT-PY-03 (Comprehensions)
- **Decisions**: DEC-PY-01 (Async vs threading)

### Metaclasses (CR-PY-04)
- **Patterns**: PAT-PY-07 (Magic methods)
- **Lessons**: LESS-PY-01 (Metaclass gotchas)

### Descriptors (CR-PY-05)
- **Patterns**: PAT-PY-07 (Magic methods)
- **Lessons**: LESS-PY-03 (Memory management)

## Implementation Status

- Total Core Concepts: 5/5 (100%)
- Average Lines: 77 (within 350 limit)
- Difficulty Distribution:
  - Beginner: 2 concepts
  - Intermediate: 2 concepts
  - Advanced: 1 concept
- Coverage: Fundamental Python language features covered

## Learning Resources

### Beginner Resources
- **Context Managers**: Python docs, "Python Tricks" book
- **Generators**: Fluent Python, realpython.com/articles

### Intermediate Resources
- **Decorators**: Python Decorators Handbook, Stack Overflow patterns
- **Metaclasses**: "Metaclasses Deep Dive" series

### Advanced Resources
- **Descriptors**: Python data model documentation
- **Metaclasses**: Advanced Python programming books

## Practical Applications

### When to Use Each Concept

**Context Managers**
- File handling
- Database connections
- Resource cleanup
- Transaction management

**Generators**
- Large data processing
- Lazy evaluation
- Infinite sequences
- Memory-efficient pipelines

**Decorators**
- Logging and monitoring
- Authentication
- Caching
- Validation

**Metaclasses**
- ORM frameworks
- Plugin systems
- Code generation
- Validation frameworks

**Descriptors**
- Property management
- Validation
- Lazy loading
- Proxy patterns