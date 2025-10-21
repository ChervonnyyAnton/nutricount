# 🎨 Design Patterns & Best Practices Guide

**Цель:** Продемонстрировать максимальное количество дизайн паттернов, принципов SOLID, OOP, YAGNI, KISS и архитектурных паттернов на практике в Nutricount.

**Область применения:** Код приложения + тесты (полный спектр лучших практик)

---

## 📚 Содержание

1. [Design Patterns (Паттерны проектирования)](#design-patterns)
2. [SOLID Principles](#solid-principles)
3. [Best Practices (YAGNI, KISS, DRY)](#best-practices)
4. [Architectural Patterns](#architectural-patterns)
5. [Testing Patterns](#testing-patterns)
6. [Implementation Roadmap](#implementation-roadmap)

---

## 🎯 Design Patterns

### Уже реализованные в проекте ✅

#### 1. Adapter Pattern (Адаптер)
**Где:** `frontend/src/adapters/`

**Проблема:** Нужно работать с разными backend'ами (API и LocalStorage) через единый интерфейс

**Реализация:**
```javascript
// BackendAdapter - базовый интерфейс
class BackendAdapter {
    async getProducts() { throw new Error('Must implement'); }
    async createProduct(product) { throw new Error('Must implement'); }
}

// ApiAdapter - для работы с REST API
class ApiAdapter extends BackendAdapter {
    async getProducts() { return fetch('/api/products'); }
}

// StorageAdapter - для работы с LocalStorage
class StorageAdapter extends BackendAdapter {
    async getProducts() { return JSON.parse(localStorage.getItem('products')); }
}
```

**Преимущества:**
- Единый интерфейс для разных реализаций
- Легко добавить новые адаптеры (IndexedDB, WebSQL)
- Код бизнес-логики не зависит от хранилища

---

#### 2. Singleton Pattern (Одиночка)
**Где:** `src/cache_manager.py`, `src/monitoring.py`

**Проблема:** Нужен единственный экземпляр кэша/мониторинга

**Реализация (Python):**
```python
class CacheManager:
    _instance = None
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance._initialize()
        return cls._instance
```

**Реализация (JavaScript):**
```javascript
class MetricsCollector {
    constructor() {
        if (MetricsCollector.instance) {
            return MetricsCollector.instance;
        }
        this.metrics = [];
        MetricsCollector.instance = this;
    }
}
```

---

#### 3. Factory Pattern (Фабрика)
**Где:** `src/security.py` (token generation)

**Проблема:** Создание объектов с разной логикой

**Текущая реализация:**
```python
def create_token(user_id, token_type='access'):
    if token_type == 'access':
        return jwt.encode({'user_id': user_id, 'exp': ...}, SECRET)
    elif token_type == 'refresh':
        return jwt.encode({'user_id': user_id, 'exp': ...}, REFRESH_SECRET)
```

**Улучшенная версия (запланировано):**
```python
class TokenFactory:
    @staticmethod
    def create_token(token_type, user_id):
        strategies = {
            'access': AccessTokenStrategy(),
            'refresh': RefreshTokenStrategy(),
            'api_key': ApiKeyStrategy()
        }
        return strategies[token_type].generate(user_id)
```

---

#### 4. Strategy Pattern (Стратегия)
**Где:** `src/nutrition_calculator.py` (различные формулы расчета)

**Проблема:** Разные алгоритмы расчета BMR (Mifflin-St Jeor, Harris-Benedict)

**Запланированная реализация:**
```python
class BMRStrategy(ABC):
    @abstractmethod
    def calculate(self, profile): pass

class MifflinStJeorStrategy(BMRStrategy):
    def calculate(self, profile):
        return 10 * profile.weight + 6.25 * profile.height - 5 * profile.age

class HarrisBenedictStrategy(BMRStrategy):
    def calculate(self, profile):
        return 66 + 13.7 * profile.weight + 5 * profile.height - 6.8 * profile.age

class BMRCalculator:
    def __init__(self, strategy: BMRStrategy):
        self.strategy = strategy
    
    def calculate(self, profile):
        return self.strategy.calculate(profile)
```

---

#### 5. Observer Pattern (Наблюдатель)
**Где:** `static/js/notifications.js`

**Проблема:** Уведомления о событиях в разных частях приложения

**Реализация:**
```javascript
class EventBus {
    constructor() {
        this.listeners = {};
    }
    
    on(event, callback) {
        if (!this.listeners[event]) this.listeners[event] = [];
        this.listeners[event].push(callback);
    }
    
    emit(event, data) {
        if (this.listeners[event]) {
            this.listeners[event].forEach(cb => cb(data));
        }
    }
}

// Usage
eventBus.on('product.created', (product) => showNotification('Product added!'));
eventBus.emit('product.created', newProduct);
```

---

#### 6. Decorator Pattern (Декоратор)
**Где:** `src/security.py` (@require_auth), `src/utils.py` (@handle_api_errors)

**Проблема:** Добавление функциональности без изменения кода

**Реализация:**
```python
def require_auth(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        token = request.headers.get('Authorization')
        if not token:
            return jsonify({'error': 'No token'}), 401
        try:
            decode_token(token)
            return f(*args, **kwargs)
        except:
            return jsonify({'error': 'Invalid token'}), 401
    return decorated_function

@app.route('/api/products')
@require_auth
def get_products():
    return jsonify(Product.all())
```

---

#### 7. Template Method Pattern (Шаблонный метод)
**Где:** Тесты `tests/`

**Проблема:** Общий алгоритм с вариативными шагами

**Реализация:**
```python
class BaseTestCase:
    def setUp(self):
        self.setup_database()
        self.setup_client()
        self.setup_auth()
    
    def setup_database(self): pass  # Переопределяется в подклассах
    def setup_client(self): pass
    def setup_auth(self): pass
    
    def tearDown(self):
        self.cleanup_database()

class ProductTestCase(BaseTestCase):
    def setup_database(self):
        # Специфичная настройка для тестов продуктов
        create_test_products()
```

---

### Паттерны для реализации 📝

#### 8. Repository Pattern (Репозиторий)
**Зачем:** Абстракция доступа к данным

**Планируемая реализация (Week 3-4):**
```python
# repositories/product_repository.py
class ProductRepository:
    def __init__(self, db):
        self.db = db
    
    def find_all(self):
        return self.db.execute("SELECT * FROM products")
    
    def find_by_id(self, id):
        return self.db.execute("SELECT * FROM products WHERE id = ?", (id,))
    
    def save(self, product):
        if product.id:
            return self._update(product)
        return self._insert(product)
    
    def delete(self, id):
        self.db.execute("DELETE FROM products WHERE id = ?", (id,))

# routes/products.py
@app.route('/api/products')
def get_products():
    repo = ProductRepository(db)
    products = repo.find_all()
    return jsonify(products)
```

**Преимущества:**
- Отделение бизнес-логики от работы с БД
- Легко тестировать (mock repository)
- Легко менять БД (SQLite → PostgreSQL)

---

#### 9. Builder Pattern (Строитель)
**Зачем:** Создание сложных объектов пошагово

**Применение:** Создание сложных блюд с ингредиентами

```python
class DishBuilder:
    def __init__(self):
        self.dish = Dish()
    
    def with_name(self, name):
        self.dish.name = name
        return self
    
    def add_ingredient(self, product_id, quantity):
        self.dish.ingredients.append({
            'product_id': product_id,
            'quantity': quantity
        })
        return self
    
    def with_preparation(self, method):
        self.dish.preparation_method = method
        return self
    
    def build(self):
        self.dish.calculate_nutrition()
        return self.dish

# Usage
dish = DishBuilder() \
    .with_name("Chicken Salad") \
    .add_ingredient(1, 150) \
    .add_ingredient(2, 100) \
    .with_preparation("raw") \
    .build()
```

---

#### 10. Chain of Responsibility (Цепочка обязанностей)
**Зачем:** Обработка запросов последовательно

**Применение:** Валидация данных

```python
class ValidationHandler(ABC):
    def __init__(self, next_handler=None):
        self.next = next_handler
    
    def handle(self, data):
        if not self.validate(data):
            raise ValidationError(self.error_message())
        if self.next:
            return self.next.handle(data)
        return True
    
    @abstractmethod
    def validate(self, data): pass
    
    @abstractmethod
    def error_message(self): pass

class NameValidator(ValidationHandler):
    def validate(self, data):
        return len(data.get('name', '')) > 2
    
    def error_message(self):
        return "Name must be at least 2 characters"

class MacrosValidator(ValidationHandler):
    def validate(self, data):
        return data['protein'] + data['fat'] + data['carbs'] <= 100
    
    def error_message(self):
        return "Total macros cannot exceed 100g"

# Usage
validator = NameValidator(
    MacrosValidator(
        CaloriesValidator()
    )
)
validator.handle(product_data)
```

---

#### 11. Command Pattern (Команда)
**Зачем:** Инкапсуляция действий, undo/redo

**Применение:** История изменений в логе питания

```python
class Command(ABC):
    @abstractmethod
    def execute(self): pass
    
    @abstractmethod
    def undo(self): pass

class AddProductCommand(Command):
    def __init__(self, product_data):
        self.product_data = product_data
        self.product_id = None
    
    def execute(self):
        self.product_id = db.insert('products', self.product_data)
        return self.product_id
    
    def undo(self):
        db.delete('products', self.product_id)

class CommandHistory:
    def __init__(self):
        self.commands = []
    
    def execute(self, command):
        command.execute()
        self.commands.append(command)
    
    def undo(self):
        if self.commands:
            self.commands.pop().undo()
```

---

#### 12. Facade Pattern (Фасад)
**Зачем:** Упрощение сложного API

**Применение:** Упрощение работы с nutrition calculator

```python
class NutritionFacade:
    """Простой интерфейс для сложных расчетов"""
    
    def __init__(self):
        self.calculator = NutritionCalculator()
        self.validator = NutritionValidator()
        self.keto_analyzer = KetoAnalyzer()
    
    def analyze_product(self, product):
        # Один метод вместо множества вызовов
        validation = self.validator.validate(product)
        if not validation.valid:
            return {'errors': validation.errors}
        
        calories = self.calculator.calculate_calories(product)
        net_carbs = self.calculator.calculate_net_carbs(product)
        keto_index = self.keto_analyzer.calculate_index(product)
        
        return {
            'calories': calories,
            'net_carbs': net_carbs,
            'keto_index': keto_index,
            'keto_rating': self.keto_analyzer.get_rating(keto_index)
        }
```

---

#### 13. Proxy Pattern (Заместитель)
**Зачем:** Контроль доступа, кэширование

**Применение:** Кэширующий прокси для API

```python
class CachingProductProxy:
    def __init__(self, real_repository):
        self.repo = real_repository
        self.cache = {}
    
    def find_by_id(self, id):
        if id not in self.cache:
            self.cache[id] = self.repo.find_by_id(id)
        return self.cache[id]
    
    def invalidate(self, id):
        if id in self.cache:
            del self.cache[id]
```

---

## 🏛️ SOLID Principles

### S - Single Responsibility Principle (Принцип единственной ответственности)

**Правило:** Класс должен иметь только одну причину для изменения

**Плохо:**
```python
class Product:
    def __init__(self, name):
        self.name = name
    
    def save_to_database(self):
        # Сохранение в БД - это отдельная ответственность!
        db.execute("INSERT INTO products VALUES (?)", (self.name,))
    
    def send_notification(self):
        # Отправка уведомлений - тоже отдельная ответственность!
        email.send("New product added")
```

**Хорошо:**
```python
class Product:
    """Только данные и бизнес-логика продукта"""
    def __init__(self, name, protein, fat, carbs):
        self.name = name
        self.protein = protein
        self.fat = fat
        self.carbs = carbs
    
    def calculate_calories(self):
        return self.protein * 4 + self.fat * 9 + self.carbs * 4

class ProductRepository:
    """Только работа с БД"""
    def save(self, product): pass
    def find(self, id): pass

class NotificationService:
    """Только уведомления"""
    def notify_product_created(self, product): pass
```

**Применение в Nutricount:**
- ✅ `src/nutrition_calculator.py` - только расчеты
- ✅ `src/cache_manager.py` - только кэширование
- ✅ `src/security.py` - только аутентификация
- 📝 Разделить `routes/products.py` на контроллер + сервис

---

### O - Open/Closed Principle (Принцип открытости/закрытости)

**Правило:** Открыт для расширения, закрыт для изменения

**Плохо:**
```python
def calculate_bmr(profile):
    if profile.formula == 'mifflin':
        return 10 * profile.weight + 6.25 * profile.height
    elif profile.formula == 'harris':
        return 66 + 13.7 * profile.weight
    # Для добавления новой формулы нужно менять этот код!
```

**Хорошо:**
```python
class BMRCalculator(ABC):
    @abstractmethod
    def calculate(self, profile): pass

class MifflinCalculator(BMRCalculator):
    def calculate(self, profile):
        return 10 * profile.weight + 6.25 * profile.height

class HarrisCalculator(BMRCalculator):
    def calculate(self, profile):
        return 66 + 13.7 * profile.weight

# Добавление новой формулы не требует изменения существующего кода
class KatchMcArdleCalculator(BMRCalculator):
    def calculate(self, profile):
        return 370 + 21.6 * profile.lean_body_mass
```

**Применение в Nutricount:**
- ✅ `frontend/src/adapters/` - легко добавить IndexedDBAdapter
- 📝 Сделать расчеты nutrition extensible

---

### L - Liskov Substitution Principle (Принцип подстановки Барбары Лисков)

**Правило:** Подклассы должны заменять базовые классы без нарушения работы

**Плохо:**
```python
class Bird:
    def fly(self): pass

class Penguin(Bird):
    def fly(self):
        raise Exception("Penguins can't fly!")  # Нарушение LSP!
```

**Хорошо:**
```python
class Bird:
    def move(self): pass

class FlyingBird(Bird):
    def move(self):
        self.fly()
    
    def fly(self): pass

class Penguin(Bird):
    def move(self):
        self.swim()
    
    def swim(self): pass
```

**Применение в Nutricount:**
```python
class BackendAdapter:
    async def getProducts(self): pass

class ApiAdapter(BackendAdapter):
    async def getProducts(self):
        # Полностью совместим с интерфейсом
        return await fetch('/api/products')

class StorageAdapter(BackendAdapter):
    async def getProducts(self):
        # Полностью совместим с интерфейсом
        return JSON.parse(localStorage.getItem('products'))
```

---

### I - Interface Segregation Principle (Принцип разделения интерфейса)

**Правило:** Клиенты не должны зависеть от методов, которые не используют

**Плохо:**
```python
class AllInOneAdapter:
    def get_products(self): pass
    def get_dishes(self): pass
    def get_logs(self): pass
    def get_stats(self): pass
    def get_fasting(self): pass
    # Если нужны только products, всё равно зависим от всего интерфейса
```

**Хорошо:**
```python
class ProductAdapter:
    def get_products(self): pass
    def save_product(self): pass

class LogAdapter:
    def get_logs(self): pass
    def save_log(self): pass

class StatsAdapter:
    def get_stats(self): pass
```

**Применение в Nutricount:**
- 📝 Разделить `BackendAdapter` на специализированные интерфейсы

---

### D - Dependency Inversion Principle (Принцип инверсии зависимостей)

**Правило:** Зависеть от абстракций, а не от конкретных реализаций

**Плохо:**
```python
class ProductService:
    def __init__(self):
        self.db = SQLiteDatabase()  # Жесткая зависимость!
    
    def get_products(self):
        return self.db.query("SELECT * FROM products")
```

**Хорошо:**
```python
class Database(ABC):
    @abstractmethod
    def query(self, sql): pass

class SQLiteDatabase(Database):
    def query(self, sql): pass

class PostgreSQLDatabase(Database):
    def query(self, sql): pass

class ProductService:
    def __init__(self, database: Database):  # Зависимость от абстракции
        self.db = database
    
    def get_products(self):
        return self.db.query("SELECT * FROM products")

# Usage
service = ProductService(SQLiteDatabase())  # Легко заменить на PostgreSQL
```

**Применение в Nutricount:**
```javascript
// Хорошо: зависимость от интерфейса
class NutritionApp {
    constructor(adapter) {  // BackendAdapter interface
        this.adapter = adapter;
    }
}

// Можем использовать любой адаптер
const localApp = new NutritionApp(new ApiAdapter());
const publicApp = new NutritionApp(new StorageAdapter());
```

---

## 🎯 Best Practices

### YAGNI (You Aren't Gonna Need It)

**Правило:** Не добавляйте функциональность, пока она не нужна

**Примеры в Nutricount:**

**✅ Хорошо:**
```python
# Простая валидация - достаточно для текущих нужд
def validate_product(data):
    if not data.get('name'):
        return False, "Name required"
    return True, None
```

**❌ Плохо (YAGNI violation):**
```python
# Сложная система валидации, которая пока не нужна
class ValidationRule: pass
class ValidationEngine: pass
class ValidationContext: pass
class ValidationResult: pass
# ... 500 строк кода для простой валидации
```

**Применение:**
- Начали с простого adapter pattern
- Добавим Repository pattern только когда БД усложнится
- Command pattern для undo/redo - только если пользователи запросят

---

### KISS (Keep It Simple, Stupid)

**Правило:** Простота превыше всего

**Примеры:**

**✅ Хорошо:**
```javascript
function calculateCalories(protein, fat, carbs) {
    return protein * 4 + fat * 9 + carbs * 4;
}
```

**❌ Плохо:**
```javascript
function calculateCalories(macros) {
    const coefficients = new Map([
        [MacroType.PROTEIN, CalorieCoefficients.ATWATER_PROTEIN],
        [MacroType.FAT, CalorieCoefficients.ATWATER_FAT],
        [MacroType.CARBS, CalorieCoefficients.ATWATER_CARBS]
    ]);
    return MacroCalculatorFactory
        .getInstance()
        .createCalculator(CalculatorType.CALORIE)
        .calculate(macros, coefficients);
}
```

---

### DRY (Don't Repeat Yourself)

**Правило:** Не повторяйтесь

**Примеры:**

**❌ Плохо:**
```python
@app.route('/api/products')
def get_products():
    token = request.headers.get('Authorization')
    if not token:
        return jsonify({'error': 'No auth'}), 401
    # ...

@app.route('/api/dishes')
def get_dishes():
    token = request.headers.get('Authorization')
    if not token:
        return jsonify({'error': 'No auth'}), 401
    # ... (дублирование!)
```

**✅ Хорошо:**
```python
def require_auth(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        token = request.headers.get('Authorization')
        if not token:
            return jsonify({'error': 'No auth'}), 401
        return f(*args, **kwargs)
    return decorated

@app.route('/api/products')
@require_auth
def get_products():
    # Код без дублирования
```

---

## 🏗️ Architectural Patterns

### 1. Layered Architecture (Слоистая архитектура)

**Текущая структура:**
```
Presentation Layer (Templates, JS)
         ↓
API Layer (Routes)
         ↓
Business Logic Layer (src/)
         ↓
Data Access Layer (SQLite)
```

**Улучшение:**
```
Presentation Layer
         ↓
Controller Layer (routes/) - Тонкие контроллеры
         ↓
Service Layer (NEW) - Бизнес-логика
         ↓
Repository Layer (NEW) - Доступ к данным
         ↓
Database Layer
```

---

### 2. MVC (Model-View-Controller)

**Запланировано:**
```
Model (src/models/) - Данные и бизнес-логика
View (templates/) - Представление
Controller (routes/) - Обработка запросов
```

---

### 3. Clean Architecture (Чистая архитектура)

**Принципы:**
- Независимость от фреймворков
- Тестируемость
- Независимость от UI
- Независимость от БД

**Структура:**
```
┌─────────────────────────────────────┐
│  Entities (Business Objects)         │ ← Ядро
├─────────────────────────────────────┤
│  Use Cases (Business Rules)          │
├─────────────────────────────────────┤
│  Interface Adapters (Controllers)    │
├─────────────────────────────────────┤
│  Frameworks & Drivers (Flask, DB)    │ ← Детали
└─────────────────────────────────────┘
```

---

## 🧪 Testing Patterns

### 1. AAA Pattern (Arrange-Act-Assert)

**Уже используется:**
```python
def test_calculate_calories():
    # Arrange
    protein, fat, carbs = 20, 10, 30
    
    # Act
    result = calculate_calories(protein, fat, carbs)
    
    # Assert
    assert result == 290  # 20*4 + 10*9 + 30*4
```

---

### 2. Test Fixtures (Фикстуры)

**Текущее использование:**
```python
@pytest.fixture
def client():
    app.config['TESTING'] = True
    with app.test_client() as client:
        yield client

def test_get_products(client):
    response = client.get('/api/products')
    assert response.status_code == 200
```

---

### 3. Mock Objects (Моки)

**Примеры:**
```python
@patch('src.cache_manager.redis')
def test_cache_with_mock(mock_redis):
    mock_redis.get.return_value = b'cached_data'
    result = cache.get('key')
    assert result == 'cached_data'
```

---

### 4. Test Data Builders

**Запланировано:**
```python
class ProductBuilder:
    def __init__(self):
        self.product = {
            'name': 'Test Product',
            'protein': 20,
            'fat': 10,
            'carbs': 5
        }
    
    def with_name(self, name):
        self.product['name'] = name
        return self
    
    def high_protein(self):
        self.product['protein'] = 80
        return self
    
    def build(self):
        return self.product

# Usage in tests
product = ProductBuilder().with_name("Chicken").high_protein().build()
```

---

### 5. Page Object Pattern

**Для E2E тестов (Week 4):**
```python
class ProductsPage:
    def __init__(self, driver):
        self.driver = driver
    
    def add_product(self, name, protein, fat, carbs):
        self.driver.find_element_by_id('product-name').send_keys(name)
        self.driver.find_element_by_id('protein').send_keys(protein)
        self.driver.find_element_by_id('submit').click()
    
    def get_products_count(self):
        return len(self.driver.find_elements_by_class('product-item'))

# Test
def test_add_product(driver):
    page = ProductsPage(driver)
    page.add_product("Chicken", 31, 3.6, 0)
    assert page.get_products_count() == 1
```

---

## 📋 Implementation Roadmap

### Week 3: Repository & Service Patterns

**Задачи:**
- [ ] Создать `repositories/` directory
- [ ] Реализовать `ProductRepository`
- [ ] Реализовать `DishRepository`
- [ ] Создать `services/` directory
- [ ] Реализовать `ProductService` (бизнес-логика)
- [ ] Обновить роуты для использования сервисов

**Файлы:**
```
src/
├── repositories/
│   ├── __init__.py
│   ├── base_repository.py
│   ├── product_repository.py
│   └── dish_repository.py
├── services/
│   ├── __init__.py
│   ├── product_service.py
│   └── dish_service.py
```

**Пример кода:**
```python
# repositories/product_repository.py
class ProductRepository:
    def find_all(self): pass
    def find_by_id(self, id): pass
    def save(self, product): pass
    def delete(self, id): pass

# services/product_service.py
class ProductService:
    def __init__(self, repo: ProductRepository):
        self.repo = repo
    
    def create_product(self, data):
        # Валидация
        # Бизнес-логика
        # Сохранение через repo
        pass

# routes/products.py (тонкий контроллер)
@app.route('/api/products', methods=['POST'])
def create_product():
    service = ProductService(ProductRepository(db))
    product = service.create_product(request.json)
    return jsonify(product), 201
```

---

### Week 4: Strategy & Builder Patterns

**Задачи:**
- [ ] Реализовать Strategy для BMR calculations
- [ ] Реализовать Builder для Dish creation
- [ ] Реализовать Chain of Responsibility для validation

**BMR Strategy:**
```python
# src/strategies/bmr_strategies.py
class BMRStrategy(ABC):
    @abstractmethod
    def calculate(self, profile): pass

class MifflinStJeor(BMRStrategy): pass
class HarrisBenedict(BMRStrategy): pass
class KatchMcArdle(BMRStrategy): pass

# src/nutrition_calculator.py
class NutritionCalculator:
    def __init__(self, bmr_strategy: BMRStrategy):
        self.bmr_strategy = bmr_strategy
    
    def calculate_bmr(self, profile):
        return self.bmr_strategy.calculate(profile)
```

---

### Week 5: Facade & Proxy Patterns

**Задачи:**
- [ ] Реализовать NutritionFacade
- [ ] Реализовать CachingProxy для repositories
- [ ] Добавить Decorator для rate limiting

**Nutrition Facade:**
```python
class NutritionFacade:
    def analyze_food(self, food_data):
        # Один метод вместо 10 вызовов
        return {
            'nutrition': self.calculator.calculate(food_data),
            'keto_index': self.keto.analyze(food_data),
            'validation': self.validator.validate(food_data)
        }
```

---

### Week 6: Testing Patterns & Documentation

**Задачи:**
- [ ] Реализовать Test Data Builders
- [ ] Добавить Page Object Pattern для E2E
- [ ] Создать паттерны для integration tests
- [ ] Документировать все паттерны с примерами

**Test Builder:**
```python
# tests/builders/product_builder.py
class ProductBuilder:
    def with_name(self, name): return self
    def high_protein(self): return self
    def keto_friendly(self): return self
    def build(self): return self.product
```

---

## 📚 Learning Materials

### Документация для студентов

**Для каждого паттерна:**
1. **Проблема** - какую задачу решает
2. **Решение** - как паттерн помогает
3. **Пример** - реальный код из Nutricount
4. **Упражнение** - задача для практики
5. **Антипаттерны** - чего избегать

**Структура:**
```
docs/patterns/
├── design-patterns/
│   ├── adapter.md
│   ├── singleton.md
│   ├── factory.md
│   └── ...
├── solid-principles/
│   ├── single-responsibility.md
│   ├── open-closed.md
│   └── ...
├── best-practices/
│   ├── yagni.md
│   ├── kiss.md
│   └── dry.md
└── architectural-patterns/
    ├── layered-architecture.md
    ├── mvc.md
    └── clean-architecture.md
```

---

## ✅ Checklist

### Паттерны проектирования
- [x] Adapter Pattern (реализован)
- [x] Singleton Pattern (реализован)
- [x] Decorator Pattern (реализован)
- [x] Observer Pattern (реализован)
- [ ] Repository Pattern (Week 3)
- [ ] Strategy Pattern (Week 4)
- [ ] Builder Pattern (Week 4)
- [ ] Factory Pattern (улучшить Week 3)
- [ ] Facade Pattern (Week 5)
- [ ] Proxy Pattern (Week 5)
- [ ] Chain of Responsibility (Week 4)
- [ ] Command Pattern (Week 5-6)
- [ ] Template Method (улучшить в тестах)

### SOLID Principles
- [x] Single Responsibility (частично)
- [ ] Open/Closed (улучшить Week 3-4)
- [x] Liskov Substitution (применяется)
- [ ] Interface Segregation (Week 4)
- [ ] Dependency Inversion (Week 3)

### Best Practices
- [x] KISS (применяется)
- [x] YAGNI (применяется)
- [x] DRY (применяется)

### Архитектурные паттерны
- [x] Layered Architecture (базовая)
- [ ] MVC (улучшить Week 3)
- [ ] Clean Architecture (Week 4-5)
- [ ] Repository Pattern (Week 3)
- [ ] Service Layer (Week 3)

### Testing Patterns
- [x] AAA Pattern (применяется)
- [x] Test Fixtures (применяется)
- [x] Mock Objects (применяется)
- [ ] Test Data Builders (Week 6)
- [ ] Page Object Pattern (Week 4)

---

**Version:** 1.0  
**Date:** October 21, 2025  
**Status:** Planning Complete  
**Implementation:** Weeks 3-6  
**Target:** Maximum pattern demonstration with practical applicability
