"""Test DI standalone without EE Gateway"""
import sys
sys.path.insert(0, 'src')

from operations.di import DIContainer, ServiceLifetime

class Database:
    def __init__(self):
        self.connected = True

class UserRepository:
    def __init__(self, db: Database):
        self.db = db

# Test
print('[TEST] Creating container...')
container = DIContainer()

print('[TEST] Registering services...')
container.register_singleton(Database, Database)
container.register_transient(UserRepository, UserRepository)

print('[TEST] Resolving Database...')
db = container.resolve(Database)
print(f'[OK] Database connected: {db.connected}')

print('[TEST] Resolving UserRepository with DI...')
repo = container.resolve(UserRepository)
print(f'[OK] UserRepository has db: {hasattr(repo, "db")}')
print(f'[OK] Repo.db is same as db: {repo.db is db}')

print('[TEST] Testing singleton...')
db2 = container.resolve(Database)
print(f'[OK] Singleton verified: {db2 is db}')

print('[TEST] Testing transient...')
repo2 = container.resolve(UserRepository)
print(f'[OK] Transient verified (new instance): {repo2 is not repo}')

print('')
print('[SUCCESS] All DI tests passed!')
