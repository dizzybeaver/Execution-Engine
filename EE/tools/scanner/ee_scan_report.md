# EE UG Architecture Violation Report

**Total Violations:** 78

## CRITICAL Severity (16)

### src\flask_server\routes.py:63
**Pattern:** Wrong Gateway Import Pattern
**Found:** `from EE.gateway import execute_operation, GatewayInterface`
**Gateway Interface:** `EE_GATEWAY_FACTORY`
**Description:** Direct Gateway import instead of EE package import

**Fix:**
```python
Use: from EE import execute_operation, EEGatewayInterface
```

### src\flask_server\routes.py:194
**Pattern:** Wrong Gateway Import Pattern
**Found:** `from EE.gateway import execute_operation, GatewayInterface`
**Gateway Interface:** `EE_GATEWAY_FACTORY`
**Description:** Direct Gateway import instead of EE package import

**Fix:**
```python
Use: from EE import execute_operation, EEGatewayInterface
```

### src\flask_server\routes.py:334
**Pattern:** Wrong Gateway Import Pattern
**Found:** `from EE.gateway import execute_operation, GatewayInterface`
**Gateway Interface:** `EE_GATEWAY_FACTORY`
**Description:** Direct Gateway import instead of EE package import

**Fix:**
```python
Use: from EE import execute_operation, EEGatewayInterface
```

### src\interface\interface_object_pool.py:28
**Pattern:** Direct Object Pool Import (INT-18)
**Found:** `from object_pool.pool_core import ObjectPool, PoolConfig`
**Gateway Interface:** `OBJECT_POOL`
**Description:** Direct pool import bypasses Gateway INT-18 OBJECT_POOL interface

**Fix:**
```python
Use: execute_operation(EEGatewayInterface.OBJECT_POOL, 'acquire', name=name)
```

### src\interface\interface_object_pool.py:28
**Pattern:** Cross-Interface Direct Import
**Found:** `from object_pool.pool_core import ObjectPool, PoolConfig`
**Gateway Interface:** `N/A`
**Description:** Direct import across interfaces violates UG

**Fix:**
```python
Use execute_operation(EEGatewayInterface.*, 'operation', **kwargs)
```

### src\interface\interface_object_pool.py:29
**Pattern:** Direct Object Pool Import (INT-18)
**Found:** `from object_pool.pool_factory import PoolFactory, get_pool_factory`
**Gateway Interface:** `OBJECT_POOL`
**Description:** Direct pool import bypasses Gateway INT-18 OBJECT_POOL interface

**Fix:**
```python
Use: execute_operation(EEGatewayInterface.OBJECT_POOL, 'acquire', name=name)
```

### src\interface\interface_object_pool.py:51
**Pattern:** Internal Debug Helper Function
**Found:** `def _generate_correlation_id() -> str:`
**Gateway Interface:** `DEBUG`
**Description:** Internal debug helper bypasses Gateway ISP routing

**Fix:**
```python
Remove helper. Use execute_operation(EEGatewayInterface.DEBUG, 'log', ...)
```

### src\interface\interface_object_pool.py:58
**Pattern:** Internal Debug Helper Function
**Found:** `def _debug_log(corr_id: str, message: str, **context):`
**Gateway Interface:** `DEBUG`
**Description:** Internal debug helper bypasses Gateway ISP routing

**Fix:**
```python
Remove helper. Use execute_operation(EEGatewayInterface.DEBUG, 'log', ...)
```

### src\interface\network_mqtt.py:48
**Pattern:** Internal Debug Helper Function
**Found:** `def _debug_log(corr_id: str, message: str, **context):`
**Gateway Interface:** `DEBUG`
**Description:** Internal debug helper bypasses Gateway ISP routing

**Fix:**
```python
Remove helper. Use execute_operation(EEGatewayInterface.DEBUG, 'log', ...)
```

### src\interface\network_redis.py:48
**Pattern:** Internal Debug Helper Function
**Found:** `def _debug_log(corr_id: str, message: str, **context):`
**Gateway Interface:** `DEBUG`
**Description:** Internal debug helper bypasses Gateway ISP routing

**Fix:**
```python
Remove helper. Use execute_operation(EEGatewayInterface.DEBUG, 'log', ...)
```

### src\object_pool\pool_core.py:94
**Pattern:** Internal Debug Helper Function
**Found:** `def _generate_correlation_id(self) -> str:`
**Gateway Interface:** `DEBUG`
**Description:** Internal debug helper bypasses Gateway ISP routing

**Fix:**
```python
Remove helper. Use execute_operation(EEGatewayInterface.DEBUG, 'log', ...)
```

### src\object_pool\pool_core.py:98
**Pattern:** Internal Debug Helper Function
**Found:** `def _debug_log(self, message: str, **context):`
**Gateway Interface:** `DEBUG`
**Description:** Internal debug helper bypasses Gateway ISP routing

**Fix:**
```python
Remove helper. Use execute_operation(EEGatewayInterface.DEBUG, 'log', ...)
```

### src\object_pool\pool_factory.py:44
**Pattern:** Internal Debug Helper Function
**Found:** `def _generate_correlation_id(self) -> str:`
**Gateway Interface:** `DEBUG`
**Description:** Internal debug helper bypasses Gateway ISP routing

**Fix:**
```python
Remove helper. Use execute_operation(EEGatewayInterface.DEBUG, 'log', ...)
```

### src\object_pool\pool_factory.py:49
**Pattern:** Internal Debug Helper Function
**Found:** `def _debug_log(self, message: str, **context):`
**Gateway Interface:** `DEBUG`
**Description:** Internal debug helper bypasses Gateway ISP routing

**Fix:**
```python
Remove helper. Use execute_operation(EEGatewayInterface.DEBUG, 'log', ...)
```

### src\object_pool\pool_metrics.py:59
**Pattern:** Internal Debug Helper Function
**Found:** `def _generate_correlation_id(self) -> str:`
**Gateway Interface:** `DEBUG`
**Description:** Internal debug helper bypasses Gateway ISP routing

**Fix:**
```python
Remove helper. Use execute_operation(EEGatewayInterface.DEBUG, 'log', ...)
```

### src\object_pool\pool_metrics.py:63
**Pattern:** Internal Debug Helper Function
**Found:** `def _debug_log(self, message: str, **context):`
**Gateway Interface:** `DEBUG`
**Description:** Internal debug helper bypasses Gateway ISP routing

**Fix:**
```python
Remove helper. Use execute_operation(EEGatewayInterface.DEBUG, 'log', ...)
```

## HIGH Severity (48)

### src\interface\interface_plugins.py:26
**Pattern:** Custom Plugin Implementation
**Found:** `class PluginState(Enum):`
**Gateway Interface:** `PLUGINS`
**Description:** Custom plugin implementation instead of Gateway PLUGINS interface

**Fix:**
```python
Use Gateway PLUGINS interface operations
```

### src\interface\network_mqtt.py:10
**Pattern:** Direct Network Protocol Import (INT-17)
**Found:** `from protocols.protocol_mqtt import MQTTProtocol`
**Gateway Interface:** `NETWORK`
**Description:** Direct protocol import bypasses Gateway INT-17 NETWORK interface

**Fix:**
```python
Use: execute_operation(EEGatewayInterface.NETWORK, 'redis_get', key=key)
```

### src\interface\network_ntp.py:10
**Pattern:** Direct Network Protocol Import (INT-17)
**Found:** `from protocols.protocol_ntp import NTPProtocol`
**Gateway Interface:** `NETWORK`
**Description:** Direct protocol import bypasses Gateway INT-17 NETWORK interface

**Fix:**
```python
Use: execute_operation(EEGatewayInterface.NETWORK, 'redis_get', key=key)
```

### src\interface\network_snmp.py:10
**Pattern:** Direct Network Protocol Import (INT-17)
**Found:** `from protocols.protocol_snmp import SNMPProtocol`
**Gateway Interface:** `NETWORK`
**Description:** Direct protocol import bypasses Gateway INT-17 NETWORK interface

**Fix:**
```python
Use: execute_operation(EEGatewayInterface.NETWORK, 'redis_get', key=key)
```

### src\object_pool\pool_core.py:21
**Pattern:** Custom Object Pool Implementation
**Found:** `class PoolConfig:`
**Gateway Interface:** `OBJECT_POOL`
**Description:** Custom pool implementation instead of Gateway OBJECT_POOL interface

**Fix:**
```python
Use Gateway OBJECT_POOL interface operations
```

### src\object_pool\pool_core.py:33
**Pattern:** Custom Object Pool Implementation
**Found:** `class PoolEntry:`
**Gateway Interface:** `OBJECT_POOL`
**Description:** Custom pool implementation instead of Gateway OBJECT_POOL interface

**Fix:**
```python
Use Gateway OBJECT_POOL interface operations
```

### src\object_pool\pool_core.py:43
**Pattern:** Custom Object Pool Implementation
**Found:** `class PoolStats:`
**Gateway Interface:** `OBJECT_POOL`
**Description:** Custom pool implementation instead of Gateway OBJECT_POOL interface

**Fix:**
```python
Use Gateway OBJECT_POOL interface operations
```

### src\object_pool\pool_core.py:55
**Pattern:** Custom Object Pool Implementation
**Found:** `class ObjectPool:`
**Gateway Interface:** `OBJECT_POOL`
**Description:** Custom pool implementation instead of Gateway OBJECT_POOL interface

**Fix:**
```python
Use Gateway OBJECT_POOL interface operations
```

### src\object_pool\pool_core.py:65
**Pattern:** Direct Pool Usage Without Gateway
**Found:** `pool = ObjectPool("connections", factory_func=create_connection, max_size=5)`
**Gateway Interface:** `OBJECT_POOL`
**Description:** Direct pool usage bypasses Gateway OBJECT_POOL interface

**Fix:**
```python
Use: execute_operation(EEGatewayInterface.OBJECT_POOL, 'acquire', name=name)
```

### src\object_pool\pool_core.py:68
**Pattern:** Direct Pool Usage Without Gateway
**Found:** `conn = pool.acquire()`
**Gateway Interface:** `OBJECT_POOL`
**Description:** Direct pool usage bypasses Gateway OBJECT_POOL interface

**Fix:**
```python
Use: execute_operation(EEGatewayInterface.OBJECT_POOL, 'acquire', name=name)
```

### src\object_pool\pool_core.py:74
**Pattern:** Direct Pool Usage Without Gateway
**Found:** `pool.release(conn)`
**Gateway Interface:** `OBJECT_POOL`
**Description:** Direct pool usage bypasses Gateway OBJECT_POOL interface

**Fix:**
```python
Use: execute_operation(EEGatewayInterface.OBJECT_POOL, 'acquire', name=name)
```

### src\object_pool\pool_factory.py:13
**Pattern:** Custom Object Pool Implementation
**Found:** `class PoolFactory:`
**Gateway Interface:** `OBJECT_POOL`
**Description:** Custom pool implementation instead of Gateway OBJECT_POOL interface

**Fix:**
```python
Use Gateway OBJECT_POOL interface operations
```

### src\object_pool\pool_factory.py:70
**Pattern:** Custom Object Pool Implementation
**Found:** `def create_pool(`
**Gateway Interface:** `OBJECT_POOL`
**Description:** Custom pool implementation instead of Gateway OBJECT_POOL interface

**Fix:**
```python
Use Gateway OBJECT_POOL interface operations
```

### src\object_pool\pool_factory.py:112
**Pattern:** Direct Pool Usage Without Gateway
**Found:** `pool = ObjectPool(name, config)`
**Gateway Interface:** `OBJECT_POOL`
**Description:** Direct pool usage bypasses Gateway OBJECT_POOL interface

**Fix:**
```python
Use: execute_operation(EEGatewayInterface.OBJECT_POOL, 'acquire', name=name)
```

### src\object_pool\pool_factory.py:139
**Pattern:** Direct Pool Usage Without Gateway
**Found:** `return pool.acquire()`
**Gateway Interface:** `OBJECT_POOL`
**Description:** Direct pool usage bypasses Gateway OBJECT_POOL interface

**Fix:**
```python
Use: execute_operation(EEGatewayInterface.OBJECT_POOL, 'acquire', name=name)
```

### src\object_pool\pool_factory.py:158
**Pattern:** Direct Pool Usage Without Gateway
**Found:** `return pool.release(obj)`
**Gateway Interface:** `OBJECT_POOL`
**Description:** Direct pool usage bypasses Gateway OBJECT_POOL interface

**Fix:**
```python
Use: execute_operation(EEGatewayInterface.OBJECT_POOL, 'acquire', name=name)
```

### src\object_pool\pool_metrics.py:12
**Pattern:** Custom Object Pool Implementation
**Found:** `class PoolMetrics:`
**Gateway Interface:** `OBJECT_POOL`
**Description:** Custom pool implementation instead of Gateway OBJECT_POOL interface

**Fix:**
```python
Use Gateway OBJECT_POOL interface operations
```

### src\operations\di\__init__.py:51
**Pattern:** Direct DI AOP Import
**Found:** `add_logging_aspect,`
**Gateway Interface:** `DI`
**Description:** Direct AOP import bypasses Gateway DI interface

**Fix:**
```python
Use: execute_operation(EEGatewayInterface.DI, 'AOP_ADD_LOGGING', weaver=weaver)
```

### src\operations\di\__init__.py:94
**Pattern:** Direct DI AOP Import
**Found:** `'add_logging_aspect',`
**Gateway Interface:** `DI`
**Description:** Direct AOP import bypasses Gateway DI interface

**Fix:**
```python
Use: execute_operation(EEGatewayInterface.DI, 'AOP_ADD_LOGGING', weaver=weaver)
```

### src\operations\di\di_aop.py:490
**Pattern:** Direct DI AOP Import
**Found:** `def add_logging_aspect(weaver: AspectWeaver,`
**Gateway Interface:** `DI`
**Description:** Direct AOP import bypasses Gateway DI interface

**Fix:**
```python
Use: execute_operation(EEGatewayInterface.DI, 'AOP_ADD_LOGGING', weaver=weaver)
```

### src\operations\di\di_aop.py:568
**Pattern:** Direct DI AOP Import
**Found:** `'add_logging_aspect',`
**Gateway Interface:** `DI`
**Description:** Direct AOP import bypasses Gateway DI interface

**Fix:**
```python
Use: execute_operation(EEGatewayInterface.DI, 'AOP_ADD_LOGGING', weaver=weaver)
```

### src\operations\di\di_decorators.py:48
**Pattern:** Direct DI Decorator Import
**Found:** `@singleton`
**Gateway Interface:** `DI`
**Description:** Direct DI decorator import instead of Gateway DI interface

**Fix:**
```python
Use Gateway DI interface for decorator operations
```

### src\operations\di\di_decorators.py:52
**Pattern:** Direct DI Decorator Import
**Found:** `@singleton(interface=IService)`
**Gateway Interface:** `DI`
**Description:** Direct DI decorator import instead of Gateway DI interface

**Fix:**
```python
Use Gateway DI interface for decorator operations
```

### src\operations\di\di_decorators.py:84
**Pattern:** Direct DI Decorator Import
**Found:** `@transient`
**Gateway Interface:** `DI`
**Description:** Direct DI decorator import instead of Gateway DI interface

**Fix:**
```python
Use Gateway DI interface for decorator operations
```

### src\operations\di\di_decorators.py:148
**Pattern:** Direct DI Decorator Import
**Found:** `@inject(Database, Logger)`
**Gateway Interface:** `DI`
**Description:** Direct DI decorator import instead of Gateway DI interface

**Fix:**
```python
Use Gateway DI interface for decorator operations
```

### src\operations\di\interface_di.py:36
**Pattern:** Direct DI AOP Import
**Found:** `add_logging_aspect,`
**Gateway Interface:** `DI`
**Description:** Direct AOP import bypasses Gateway DI interface

**Fix:**
```python
Use: execute_operation(EEGatewayInterface.DI, 'AOP_ADD_LOGGING', weaver=weaver)
```

### src\operations\di\interface_di.py:156
**Pattern:** Direct DI AOP Import
**Found:** `return AspectWeaver()`
**Gateway Interface:** `DI`
**Description:** Direct AOP import bypasses Gateway DI interface

**Fix:**
```python
Use: execute_operation(EEGatewayInterface.DI, 'AOP_ADD_LOGGING', weaver=weaver)
```

### src\operations\di\interface_di.py:171
**Pattern:** Direct DI AOP Import
**Found:** `add_logging_aspect(weaver, pointcut, order)`
**Gateway Interface:** `DI`
**Description:** Direct AOP import bypasses Gateway DI interface

**Fix:**
```python
Use: execute_operation(EEGatewayInterface.DI, 'AOP_ADD_LOGGING', weaver=weaver)
```

### src\plugins\examples\example_plugins.py:11
**Pattern:** Custom Plugin Implementation
**Found:** `class DatabasePlugin(EEPlugin):`
**Gateway Interface:** `PLUGINS`
**Description:** Custom plugin implementation instead of Gateway PLUGINS interface

**Fix:**
```python
Use Gateway PLUGINS interface operations
```

### src\plugins\examples\example_plugins.py:79
**Pattern:** Custom Plugin Implementation
**Found:** `class MonitoringPlugin(EEPlugin):`
**Gateway Interface:** `PLUGINS`
**Description:** Custom plugin implementation instead of Gateway PLUGINS interface

**Fix:**
```python
Use Gateway PLUGINS interface operations
```

### src\plugins\examples\example_plugins.py:129
**Pattern:** Custom Plugin Implementation
**Found:** `class CachingPlugin(EEPlugin):`
**Gateway Interface:** `PLUGINS`
**Description:** Custom plugin implementation instead of Gateway PLUGINS interface

**Fix:**
```python
Use Gateway PLUGINS interface operations
```

### src\plugins\examples\example_plugins.py:198
**Pattern:** Direct Redis Client Usage
**Found:** `import redis`
**Gateway Interface:** `NETWORK`
**Description:** Direct Redis client instead of Gateway NETWORK interface

**Fix:**
```python
Use: execute_operation(EEGatewayInterface.NETWORK, 'redis_get', key=key)
```

### src\plugins\examples\example_plugins.py:200
**Pattern:** Direct Redis Client Usage
**Found:** `redis_client = redis.Redis(`
**Gateway Interface:** `NETWORK`
**Description:** Direct Redis client instead of Gateway NETWORK interface

**Fix:**
```python
Use: execute_operation(EEGatewayInterface.NETWORK, 'redis_get', key=key)
```

### src\plugins\faas_plugin.py:34
**Pattern:** Custom Plugin Implementation
**Found:** `class FaaSPlugin(EEPlugin):`
**Gateway Interface:** `PLUGINS`
**Description:** Custom plugin implementation instead of Gateway PLUGINS interface

**Fix:**
```python
Use Gateway PLUGINS interface operations
```

### src\plugins\ha_plugin.py:33
**Pattern:** Custom Plugin Implementation
**Found:** `class HAPlugin(EEPlugin):`
**Gateway Interface:** `PLUGINS`
**Description:** Custom plugin implementation instead of Gateway PLUGINS interface

**Fix:**
```python
Use Gateway PLUGINS interface operations
```

### src\plugins\plugin_core.py:11
**Pattern:** Custom Plugin Implementation
**Found:** `class PluginError(Exception):`
**Gateway Interface:** `PLUGINS`
**Description:** Custom plugin implementation instead of Gateway PLUGINS interface

**Fix:**
```python
Use Gateway PLUGINS interface operations
```

### src\plugins\plugin_core.py:16
**Pattern:** Custom Plugin Implementation
**Found:** `class PluginLoadError(PluginError):`
**Gateway Interface:** `PLUGINS`
**Description:** Custom plugin implementation instead of Gateway PLUGINS interface

**Fix:**
```python
Use Gateway PLUGINS interface operations
```

### src\plugins\plugin_core.py:21
**Pattern:** Custom Plugin Implementation
**Found:** `class PluginInitError(PluginError):`
**Gateway Interface:** `PLUGINS`
**Description:** Custom plugin implementation instead of Gateway PLUGINS interface

**Fix:**
```python
Use Gateway PLUGINS interface operations
```

### src\plugins\plugin_core.py:26
**Pattern:** Custom Plugin Implementation
**Found:** `class PluginRuntimeError(PluginError):`
**Gateway Interface:** `PLUGINS`
**Description:** Custom plugin implementation instead of Gateway PLUGINS interface

**Fix:**
```python
Use Gateway PLUGINS interface operations
```

### src\plugins\plugin_core.py:31
**Pattern:** Custom Plugin Implementation
**Found:** `class EEPlugin(ABC):`
**Gateway Interface:** `PLUGINS`
**Description:** Custom plugin implementation instead of Gateway PLUGINS interface

**Fix:**
```python
Use Gateway PLUGINS interface operations
```

### src\plugins\plugin_core.py:105
**Pattern:** Custom Plugin Implementation
**Found:** `class PluginInfo:`
**Gateway Interface:** `PLUGINS`
**Description:** Custom plugin implementation instead of Gateway PLUGINS interface

**Fix:**
```python
Use Gateway PLUGINS interface operations
```

### src\plugins\plugin_core.py:134
**Pattern:** Custom Plugin Implementation
**Found:** `class PluginDependency(ABC):`
**Gateway Interface:** `PLUGINS`
**Description:** Custom plugin implementation instead of Gateway PLUGINS interface

**Fix:**
```python
Use Gateway PLUGINS interface operations
```

### src\plugins\plugin_loader.py:16
**Pattern:** Custom Plugin Implementation
**Found:** `class PluginLoader:`
**Gateway Interface:** `PLUGINS`
**Description:** Custom plugin implementation instead of Gateway PLUGINS interface

**Fix:**
```python
Use Gateway PLUGINS interface operations
```

### src\plugins\plugin_loader.py:112
**Pattern:** Custom Plugin Implementation
**Found:** `if not issubclass(plugin_class, EEPlugin):`
**Gateway Interface:** `PLUGINS`
**Description:** Custom plugin implementation instead of Gateway PLUGINS interface

**Fix:**
```python
Use Gateway PLUGINS interface operations
```

### src\plugins\plugin_loader.py:261
**Pattern:** Custom Plugin Implementation
**Found:** `def plugin(plugin_class: Type[EEPlugin]) -> Type[EEPlugin]:`
**Gateway Interface:** `PLUGINS`
**Description:** Custom plugin implementation instead of Gateway PLUGINS interface

**Fix:**
```python
Use Gateway PLUGINS interface operations
```

### src\plugins\plugin_loader.py:267
**Pattern:** Custom Plugin Implementation
**Found:** `class MyPlugin(EEPlugin):`
**Gateway Interface:** `PLUGINS`
**Description:** Custom plugin implementation instead of Gateway PLUGINS interface

**Fix:**
```python
Use Gateway PLUGINS interface operations
```

### src\plugins\plugin_registry.py:12
**Pattern:** Custom Plugin Implementation
**Found:** `class PluginRegistry:`
**Gateway Interface:** `PLUGINS`
**Description:** Custom plugin implementation instead of Gateway PLUGINS interface

**Fix:**
```python
Use Gateway PLUGINS interface operations
```

### src\plugins\plugin_registry.py:40
**Pattern:** Custom Plugin Implementation
**Found:** `def register_plugin(self, plugin_info: PluginInfo) -> None:`
**Gateway Interface:** `PLUGINS`
**Description:** Custom plugin implementation instead of Gateway PLUGINS interface

**Fix:**
```python
Use Gateway PLUGINS interface operations
```

## MEDIUM Severity (14)

### src\flask_server\flask_app.py:6
**Pattern:** Direct Flask Import
**Found:** `from flask import Flask, render_template`
**Gateway Interface:** `FLASK_SERVER`
**Description:** Direct Flask import instead of EE Flask Server wrapper

**Fix:**
```python
Use EE Flask Server exports
```

### src\flask_server\flask_app.py:8
**Pattern:** Direct Config File Access
**Found:** `import yaml`
**Gateway Interface:** `CONFIG`
**Description:** Direct YAML config file access instead of Gateway CONFIG

**Fix:**
```python
Use: execute_operation(EEGatewayInterface.CONFIG, 'get', key=key)
```

### src\flask_server\flask_app.py:37
**Pattern:** Direct Config File Access
**Found:** `ee_config = yaml.safe_load(f)`
**Gateway Interface:** `CONFIG`
**Description:** Direct YAML config file access instead of Gateway CONFIG

**Fix:**
```python
Use: execute_operation(EEGatewayInterface.CONFIG, 'get', key=key)
```

### src\flask_server\routes.py:6
**Pattern:** Direct Flask Import
**Found:** `from flask import Blueprint, render_template, jsonify, request`
**Gateway Interface:** `FLASK_SERVER`
**Description:** Direct Flask import instead of EE Flask Server wrapper

**Fix:**
```python
Use EE Flask Server exports
```

### src\flask_server\routes.py:7
**Pattern:** Direct Config File Access
**Found:** `import yaml`
**Gateway Interface:** `CONFIG`
**Description:** Direct YAML config file access instead of Gateway CONFIG

**Fix:**
```python
Use: execute_operation(EEGatewayInterface.CONFIG, 'get', key=key)
```

### src\flask_server\routes.py:126
**Pattern:** Direct Config File Access
**Found:** `config = yaml.safe_load(f)`
**Gateway Interface:** `CONFIG`
**Description:** Direct YAML config file access instead of Gateway CONFIG

**Fix:**
```python
Use: execute_operation(EEGatewayInterface.CONFIG, 'get', key=key)
```

### src\flask_server\routes.py:266
**Pattern:** Direct Config File Access
**Found:** `config = yaml.safe_load(f)`
**Gateway Interface:** `CONFIG`
**Description:** Direct YAML config file access instead of Gateway CONFIG

**Fix:**
```python
Use: execute_operation(EEGatewayInterface.CONFIG, 'get', key=key)
```

### src\flask_server\routes_ha.py:6
**Pattern:** Direct Flask Import
**Found:** `from flask import Blueprint, render_template, jsonify, request`
**Gateway Interface:** `FLASK_SERVER`
**Description:** Direct Flask import instead of EE Flask Server wrapper

**Fix:**
```python
Use EE Flask Server exports
```

### src\plugins\ha_plugin.py:648
**Pattern:** Direct Environment Variable Access
**Found:** `self._ha_url = os.getenv('HOME_ASSISTANT_URL')`
**Gateway Interface:** `CONFIG`
**Description:** Direct config access instead of Gateway CONFIG interface

**Fix:**
```python
Use execute_operation(EEGatewayInterface.CONFIG, 'get', key=key)
```

### src\plugins\ha_plugin.py:649
**Pattern:** Direct Environment Variable Access
**Found:** `self._ha_token = os.getenv('HOME_ASSISTANT_TOKEN')`
**Gateway Interface:** `CONFIG`
**Description:** Direct config access instead of Gateway CONFIG interface

**Fix:**
```python
Use execute_operation(EEGatewayInterface.CONFIG, 'get', key=key)
```

### src\protocols\protocol_rpc.py:205
**Pattern:** Manual JSON Operations
**Found:** `conn.request('POST', self.path, json.dumps(test_payload), self._headers)`
**Gateway Interface:** `UTILITY`
**Description:** Manual JSON instead of Gateway UTILITY interface

**Fix:**
```python
Use execute_operation(EEGatewayInterface.UTILITY, 'parse_json', json_string=data)
```

### src\protocols\protocol_rpc.py:249
**Pattern:** Manual JSON Operations
**Found:** `conn.request('POST', self.path, json.dumps(payload), self._headers)`
**Gateway Interface:** `UTILITY`
**Description:** Manual JSON instead of Gateway UTILITY interface

**Fix:**
```python
Use execute_operation(EEGatewayInterface.UTILITY, 'parse_json', json_string=data)
```

### src\protocols\protocol_rpc.py:259
**Pattern:** Manual JSON Operations
**Found:** `result = json.loads(response.read().decode('utf-8'))`
**Gateway Interface:** `UTILITY`
**Description:** Manual JSON instead of Gateway UTILITY interface

**Fix:**
```python
Use execute_operation(EEGatewayInterface.UTILITY, 'parse_json', json_string=data)
```

### src\protocols\protocol_rpc.py:349
**Pattern:** Manual JSON Operations
**Found:** `conn.request('POST', self.path, json.dumps(payload), self._headers)`
**Gateway Interface:** `UTILITY`
**Description:** Manual JSON instead of Gateway UTILITY interface

**Fix:**
```python
Use execute_operation(EEGatewayInterface.UTILITY, 'parse_json', json_string=data)
```



## Summary
Total Violations: 78
By Severity: {'MEDIUM': 14, 'CRITICAL': 16, 'HIGH': 48}
By Interface: {'FLASK_SERVER': 3, 'CONFIG': 7, 'EE_GATEWAY_FACTORY': 3, 'OBJECT_POOL': 15, 'DEBUG': 10, 'N/A': 1, 'PLUGINS': 19, 'NETWORK': 5, 'DI': 11, 'UTILITY': 4}

Top Patterns:
   19 - Custom Plugin Implementation
   10 - Internal Debug Helper Function
    7 - Custom Object Pool Implementation
    7 - Direct DI AOP Import
    6 - Direct Pool Usage Without Gateway
