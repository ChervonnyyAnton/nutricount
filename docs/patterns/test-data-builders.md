# Test Data Builders Pattern

**Pattern Type**: Creational (Testing)  
**Complexity**: Low-Medium  
**Use Case**: Creating test data with readable, maintainable code  
**Status**: 📋 Design Document (Implementation Planned)

---

## 🎯 Overview

The Test Data Builder pattern provides a fluent interface for constructing test data objects. Instead of using constructors or object literals with many parameters, builders make test setup more readable and maintainable.

### Benefits for Nutricount Tests

- **Readable Tests**: Clear intent of test data
- **Maintainable**: Easy to update when models change
- **Reusable**: Share builders across test files
- **Flexible**: Easy to create variations
- **Type-Safe**: Better IDE autocomplete and validation

---

## 📋 Problems Solved

### Without Builders (Current State)

```javascript
// ❌ Hard to read, easy to make mistakes
test('should calculate product nutrition', () => {
  const product = {
    id: 1,
    name: 'Test Product',
    calories: 100,
    protein: 20,
    fat: 5,
    carbs: 10,
    fiber: 3,
    sugar: 2,
    saturated_fat: 1.5,
    trans_fat: 0,
    cholesterol: 0,
    sodium: 50,
    potassium: 100,
    vitamin_a: 0,
    vitamin_c: 0,
    calcium: 0,
    iron: 0,
    category: 'Test',
    serving_size: 100,
    serving_unit: 'g',
    brand: 'Test Brand'
  };
  
  // Test logic
});

// ❌ Lots of duplication
test('should validate high protein product', () => {
  const product = {
    id: 2,
    name: 'High Protein Product',
    calories: 150,
    protein: 30,  // Only this is different!
    fat: 5,
    carbs: 10,
    // ... 15+ more fields
  };
});
```

### With Builders (Proposed)

```javascript
// ✅ Clear, readable, maintainable
test('should calculate product nutrition', () => {
  const product = new ProductBuilder()
    .withName('Test Product')
    .withNutrition({ calories: 100, protein: 20 })
    .build();
  
  // Test logic
});

// ✅ Easy variations with defaults
test('should validate high protein product', () => {
  const product = new ProductBuilder()
    .withHighProtein()
    .build();
});
```

---

## 🏗️ Builder Implementation

### Base Builder Pattern

```javascript
class Builder {
  constructor(defaults = {}) {
    this.data = { ...defaults };
  }
  
  with(key, value) {
    this.data[key] = value;
    return this;
  }
  
  build() {
    return { ...this.data };
  }
  
  reset() {
    this.data = {};
    return this;
  }
}
```

### ProductBuilder

```javascript
class ProductBuilder extends Builder {
  constructor() {
    super({
      id: null,
      name: 'Test Product',
      calories: 100,
      protein: 10,
      fat: 5,
      carbs: 10,
      fiber: 2,
      sugar: 1,
      saturated_fat: 1,
      trans_fat: 0,
      cholesterol: 0,
      sodium: 50,
      potassium: 100,
      vitamin_a: 0,
      vitamin_c: 0,
      calcium: 0,
      iron: 0,
      category: 'Test Category',
      serving_size: 100,
      serving_unit: 'g',
      brand: 'Test Brand',
      barcode: null,
      notes: '',
      created_at: new Date().toISOString(),
      updated_at: new Date().toISOString()
    });
    this.nextId = 1;
  }
  
  // Chainable setters
  withId(id) {
    this.data.id = id;
    return this;
  }
  
  withAutoId() {
    this.data.id = this.nextId++;
    return this;
  }
  
  withName(name) {
    this.data.name = name;
    return this;
  }
  
  withBrand(brand) {
    this.data.brand = brand;
    return this;
  }
  
  withCategory(category) {
    this.data.category = category;
    return this;
  }
  
  withServingSize(size, unit = 'g') {
    this.data.serving_size = size;
    this.data.serving_unit = unit;
    return this;
  }
  
  withNutrition({ calories, protein, fat, carbs, fiber, sugar }) {
    if (calories !== undefined) this.data.calories = calories;
    if (protein !== undefined) this.data.protein = protein;
    if (fat !== undefined) this.data.fat = fat;
    if (carbs !== undefined) this.data.carbs = carbs;
    if (fiber !== undefined) this.data.fiber = fiber;
    if (sugar !== undefined) this.data.sugar = sugar;
    return this;
  }
  
  withMicronutrients({ sodium, potassium, vitamin_a, vitamin_c, calcium, iron }) {
    if (sodium !== undefined) this.data.sodium = sodium;
    if (potassium !== undefined) this.data.potassium = potassium;
    if (vitamin_a !== undefined) this.data.vitamin_a = vitamin_a;
    if (vitamin_c !== undefined) this.data.vitamin_c = vitamin_c;
    if (calcium !== undefined) this.data.calcium = calcium;
    if (iron !== undefined) this.data.iron = iron;
    return this;
  }
  
  // Preset configurations
  withHighProtein() {
    return this.withNutrition({
      calories: 200,
      protein: 40,
      fat: 5,
      carbs: 5
    });
  }
  
  withLowCarb() {
    return this.withNutrition({
      calories: 150,
      protein: 20,
      fat: 10,
      carbs: 2
    });
  }
  
  withKeto() {
    return this.withNutrition({
      calories: 250,
      protein: 15,
      fat: 20,
      carbs: 3,
      fiber: 1
    });
  }
  
  withZeroCalories() {
    return this.withNutrition({
      calories: 0,
      protein: 0,
      fat: 0,
      carbs: 0
    });
  }
  
  // Category presets
  asMeat() {
    return this
      .withCategory('Meat')
      .withHighProtein()
      .withServingSize(100, 'g');
  }
  
  asVegetable() {
    return this
      .withCategory('Vegetables')
      .withLowCarb()
      .withServingSize(100, 'g');
  }
  
  asDairy() {
    return this
      .withCategory('Dairy')
      .withServingSize(100, 'ml');
  }
  
  // Build variations
  buildMany(count) {
    return Array.from({ length: count }, (_, i) => {
      this.withAutoId();
      this.withName(`${this.data.name} ${i + 1}`);
      return this.build();
    });
  }
}
```

### DishBuilder

```javascript
class DishBuilder extends Builder {
  constructor() {
    super({
      id: null,
      name: 'Test Dish',
      ingredients: [],
      preparation_method: 'standard',
      edible_portion: 1.0,
      total_weight: 0,
      notes: '',
      created_at: new Date().toISOString(),
      updated_at: new Date().toISOString()
    });
    this.nextId = 1;
  }
  
  withId(id) {
    this.data.id = id;
    return this;
  }
  
  withAutoId() {
    this.data.id = this.nextId++;
    return this;
  }
  
  withName(name) {
    this.data.name = name;
    return this;
  }
  
  withIngredient(productId, quantity) {
    this.data.ingredients.push({
      product_id: productId,
      quantity: quantity
    });
    this.data.total_weight += quantity;
    return this;
  }
  
  withIngredients(ingredients) {
    this.data.ingredients = ingredients;
    this.data.total_weight = ingredients.reduce(
      (sum, ing) => sum + ing.quantity, 
      0
    );
    return this;
  }
  
  withPreparationMethod(method) {
    this.data.preparation_method = method;
    return this;
  }
  
  withEdiblePortion(portion) {
    this.data.edible_portion = portion;
    return this;
  }
  
  // Preset dishes
  asSimpleSalad() {
    return this
      .withName('Simple Salad')
      .withIngredients([
        { product_id: 1, quantity: 100 },
        { product_id: 2, quantity: 50 }
      ])
      .withPreparationMethod('raw');
  }
  
  asComplexRecipe() {
    return this
      .withName('Complex Recipe')
      .withIngredients([
        { product_id: 1, quantity: 200 },
        { product_id: 2, quantity: 100 },
        { product_id: 3, quantity: 50 },
        { product_id: 4, quantity: 30 }
      ])
      .withPreparationMethod('cooked')
      .withEdiblePortion(0.8);
  }
}
```

### LogEntryBuilder

```javascript
class LogEntryBuilder extends Builder {
  constructor() {
    super({
      id: null,
      date: new Date().toISOString().split('T')[0],
      item_type: 'product',
      item_id: 1,
      item_name: 'Test Item',
      quantity: 100,
      meal_time: 'breakfast',
      notes: '',
      created_at: new Date().toISOString()
    });
    this.nextId = 1;
  }
  
  withId(id) {
    this.data.id = id;
    return this;
  }
  
  withAutoId() {
    this.data.id = this.nextId++;
    return this;
  }
  
  withDate(date) {
    this.data.date = date;
    return this;
  }
  
  withToday() {
    this.data.date = new Date().toISOString().split('T')[0];
    return this;
  }
  
  withYesterday() {
    const yesterday = new Date();
    yesterday.setDate(yesterday.getDate() - 1);
    this.data.date = yesterday.toISOString().split('T')[0];
    return this;
  }
  
  withProduct(productId, productName = 'Test Product') {
    this.data.item_type = 'product';
    this.data.item_id = productId;
    this.data.item_name = productName;
    return this;
  }
  
  withDish(dishId, dishName = 'Test Dish') {
    this.data.item_type = 'dish';
    this.data.item_id = dishId;
    this.data.item_name = dishName;
    return this;
  }
  
  withQuantity(quantity) {
    this.data.quantity = quantity;
    return this;
  }
  
  withMealTime(mealTime) {
    this.data.meal_time = mealTime;
    return this;
  }
  
  asBreakfast() {
    return this.withMealTime('breakfast');
  }
  
  asLunch() {
    return this.withMealTime('lunch');
  }
  
  asDinner() {
    return this.withMealTime('dinner');
  }
  
  asSnack() {
    return this.withMealTime('snack');
  }
}
```

### FastingSessionBuilder

```javascript
class FastingSessionBuilder extends Builder {
  constructor() {
    super({
      id: null,
      user_id: 1,
      fasting_type: '16:8',
      start_time: new Date().toISOString(),
      end_time: null,
      duration_hours: 0,
      target_hours: 16,
      status: 'active',
      notes: '',
      created_at: new Date().toISOString()
    });
    this.nextId = 1;
  }
  
  withId(id) {
    this.data.id = id;
    return this;
  }
  
  withAutoId() {
    this.data.id = this.nextId++;
    return this;
  }
  
  withType(type) {
    this.data.fasting_type = type;
    const targetHours = {
      '16:8': 16,
      '18:6': 18,
      '20:4': 20,
      'OMAD': 23
    };
    this.data.target_hours = targetHours[type] || 16;
    return this;
  }
  
  withStartTime(startTime) {
    this.data.start_time = startTime;
    return this;
  }
  
  withEndTime(endTime) {
    this.data.end_time = endTime;
    if (endTime) {
      this.data.status = 'completed';
      const start = new Date(this.data.start_time);
      const end = new Date(endTime);
      this.data.duration_hours = (end - start) / (1000 * 60 * 60);
    }
    return this;
  }
  
  asActive() {
    this.data.status = 'active';
    this.data.end_time = null;
    return this;
  }
  
  asCompleted(durationHours = 16) {
    this.data.status = 'completed';
    const start = new Date(this.data.start_time);
    const end = new Date(start.getTime() + durationHours * 60 * 60 * 1000);
    this.data.end_time = end.toISOString();
    this.data.duration_hours = durationHours;
    return this;
  }
  
  asCancelled() {
    this.data.status = 'cancelled';
    return this;
  }
}
```

---

## 💡 Usage Examples

### Basic Test Setup

```javascript
describe('Product Nutrition Calculator', () => {
  test('should calculate calories correctly', () => {
    const product = new ProductBuilder()
      .withName('Chicken Breast')
      .withNutrition({ calories: 165, protein: 31, fat: 3.6, carbs: 0 })
      .build();
    
    const result = calculateNutrition(product, 100);
    
    expect(result.calories).toBe(165);
  });
});
```

### Multiple Test Cases

```javascript
describe('Keto Index Calculator', () => {
  test.each([
    ['High Fat', new ProductBuilder().withKeto().build(), 'Excellent'],
    ['High Protein', new ProductBuilder().withHighProtein().build(), 'Good'],
    ['High Carb', new ProductBuilder().withNutrition({ carbs: 50 }).build(), 'Poor']
  ])('should rate %s as %s', (name, product, expectedRating) => {
    const rating = calculateKetoRating(product);
    expect(rating).toBe(expectedRating);
  });
});
```

### Complex Test Scenarios

```javascript
describe('Daily Log Statistics', () => {
  test('should calculate daily totals correctly', () => {
    // Create products
    const chicken = new ProductBuilder()
      .withId(1)
      .withName('Chicken')
      .asMeat()
      .build();
    
    const broccoli = new ProductBuilder()
      .withId(2)
      .withName('Broccoli')
      .asVegetable()
      .build();
    
    // Create log entries
    const breakfast = new LogEntryBuilder()
      .withProduct(1, 'Chicken')
      .withQuantity(150)
      .asBreakfast()
      .build();
    
    const lunch = new LogEntryBuilder()
      .withProduct(2, 'Broccoli')
      .withQuantity(200)
      .asLunch()
      .build();
    
    const stats = calculateDailyStats([breakfast, lunch], [chicken, broccoli]);
    
    expect(stats.total_calories).toBeGreaterThan(0);
    expect(stats.total_protein).toBeGreaterThan(0);
  });
});
```

### Integration Test Data

```javascript
describe('Fasting Feature Integration', () => {
  let testData;
  
  beforeEach(() => {
    testData = {
      user: new UserBuilder().build(),
      sessions: [
        new FastingSessionBuilder()
          .withType('16:8')
          .asCompleted(16.5)
          .build(),
        new FastingSessionBuilder()
          .withType('18:6')
          .asCompleted(18.2)
          .build(),
        new FastingSessionBuilder()
          .withType('16:8')
          .asActive()
          .build()
      ]
    };
  });
  
  test('should calculate average fasting duration', () => {
    const avg = calculateAverageDuration(testData.sessions);
    expect(avg).toBeCloseTo(17.35, 1);
  });
});
```

---

## 🔧 Implementation Checklist

### Phase 1: Core Builders (3 hours)
- [ ] Create base `Builder` class
- [ ] Implement `ProductBuilder` with all methods
- [ ] Implement `DishBuilder` with all methods
- [ ] Add JSDoc documentation
- [ ] Create example usage file

### Phase 2: Additional Builders (2 hours)
- [ ] Implement `LogEntryBuilder`
- [ ] Implement `FastingSessionBuilder`
- [ ] Implement `UserBuilder` (if needed)
- [ ] Add preset configurations

### Phase 3: Integration (2 hours)
- [ ] Create `tests/builders/` directory
- [ ] Migrate 10-20 existing tests to use builders
- [ ] Add builder examples to test documentation
- [ ] Create test data factories

### Phase 4: Polish (1 hour)
- [ ] Add TypeScript definitions (if using TS)
- [ ] Performance optimization
- [ ] Add more presets based on common patterns
- [ ] Code review and refinement

**Total Estimated Time**: 8 hours

---

## 📊 Testing the Builders

```javascript
describe('ProductBuilder', () => {
  test('should create product with defaults', () => {
    const product = new ProductBuilder().build();
    
    expect(product.name).toBe('Test Product');
    expect(product.calories).toBe(100);
    expect(product.protein).toBe(10);
  });
  
  test('should override defaults', () => {
    const product = new ProductBuilder()
      .withName('Custom Product')
      .withNutrition({ calories: 200 })
      .build();
    
    expect(product.name).toBe('Custom Product');
    expect(product.calories).toBe(200);
    expect(product.protein).toBe(10); // Default unchanged
  });
  
  test('should apply preset configurations', () => {
    const product = new ProductBuilder()
      .withKeto()
      .build();
    
    expect(product.fat).toBeGreaterThan(product.carbs);
  });
  
  test('should build multiple products', () => {
    const products = new ProductBuilder().buildMany(5);
    
    expect(products).toHaveLength(5);
    expect(products[0].id).toBe(1);
    expect(products[4].id).toBe(5);
  });
});
```

---

## 🎓 Best Practices

### 1. Sensible Defaults
Choose defaults that make most tests simple.

```javascript
// ✅ Good: Defaults work for most tests
class ProductBuilder {
  constructor() {
    super({
      calories: 100,  // Reasonable default
      protein: 10,     // Reasonable default
      name: 'Test Product'  // Clear it's test data
    });
  }
}

// ❌ Bad: Too many null/undefined defaults
class BadProductBuilder {
  constructor() {
    super({
      calories: null,  // Forces every test to set this
      protein: undefined
    });
  }
}
```

### 2. Fluent Interface
Return `this` from all setter methods for chaining.

```javascript
// ✅ Good: Chainable
withName(name) {
  this.data.name = name;
  return this;  // Enable chaining
}

// ❌ Bad: Not chainable
withName(name) {
  this.data.name = name;
  // No return
}
```

### 3. Preset Methods
Create meaningful presets for common scenarios.

```javascript
// ✅ Good: Express intent clearly
const product = new ProductBuilder()
  .withKeto()
  .build();

// ❌ Bad: Unclear intent
const product = new ProductBuilder()
  .withNutrition({ fat: 20, carbs: 3 })
  .build();
```

### 4. Immutable Build
Don't reuse builder instance after build().

```javascript
// ✅ Good: New builder for each test
test('test 1', () => {
  const product = new ProductBuilder().build();
});

test('test 2', () => {
  const product = new ProductBuilder().build();
});

// ❌ Bad: Reusing builder (state pollution)
const builder = new ProductBuilder();
test('test 1', () => {
  const product = builder.build();
});
test('test 2', () => {
  const product = builder.build(); // May have state from test 1
});
```

### 5. Factory Functions
Create factory functions for complex builder combinations.

```javascript
function createKetoMeal() {
  return {
    mainCourse: new ProductBuilder()
      .withName('Steak')
      .asMeat()
      .withKeto()
      .build(),
    
    side: new ProductBuilder()
      .withName('Broccoli')
      .asVegetable()
      .build(),
    
    logs: [
      new LogEntryBuilder()
        .withProduct(1, 'Steak')
        .withQuantity(200)
        .asDinner()
        .build(),
      new LogEntryBuilder()
        .withProduct(2, 'Broccoli')
        .withQuantity(150)
        .asDinner()
        .build()
    ]
  };
}

// Usage
test('keto meal calculation', () => {
  const meal = createKetoMeal();
  // Test with complex data
});
```

---

## 🚀 Migration Strategy

### Step 1: Identify Target Tests
Find tests with complex setup code:

```bash
grep -r "id: [0-9]" tests/ | wc -l  # Count inline objects
```

### Step 2: Create Builders
Start with most-used entities (Products, Dishes).

### Step 3: Gradual Migration
Migrate 2-3 test files at a time:

```javascript
// Before
test('old test', () => {
  const product = { id: 1, name: 'Test', calories: 100, /* ... */ };
  // ...
});

// After
test('migrated test', () => {
  const product = new ProductBuilder().build();
  // ...
});
```

### Step 4: Document Patterns
Add examples to test documentation.

### Step 5: Maintain Consistency
Use builders in all new tests.

---

## 📖 Additional Resources

### Pattern References
- [Test Data Builders](http://www.natpryce.com/articles/000714.html) - Original article
- [Growing Object-Oriented Software](https://www.growing-object-oriented-software.com/) - Book chapter
- [Builder Pattern](https://refactoring.guru/design-patterns/builder) - Refactoring Guru

### Related Patterns
- **Object Mother**: Pre-built test objects
- **Factory Pattern**: Creating complex objects
- **Fixture Factory**: Database fixture generation

### Tools
- [Factory Bot (Ruby)](https://github.com/thoughtbot/factory_bot)
- [Faker.js](https://github.com/faker-js/faker) - Generate fake data
- [Chance.js](https://chancejs.com/) - Random generator helpers

---

## 💭 Anti-Patterns to Avoid

### 1. Over-Engineering
```javascript
// ❌ Too complex for simple tests
class ProductBuilder {
  withAdvancedNutritionCalculation() { /* 50 lines */ }
  withDynamicMacroBalancing() { /* 30 lines */ }
  // ...
}

// ✅ Keep it simple
class ProductBuilder {
  withNutrition({ calories, protein, fat, carbs }) { /* 5 lines */ }
}
```

### 2. Mutable Builders
```javascript
// ❌ Mutable (state pollution)
build() {
  return this.data;  // Returns reference
}

// ✅ Immutable
build() {
  return { ...this.data };  // Returns copy
}
```

### 3. Testing Builders
```javascript
// ❌ Don't test the builders themselves (they're test utilities)
describe('ProductBuilder', () => {
  test('withName sets name', () => { /* ... */ });
});

// ✅ Use builders, don't test them
describe('Product calculations', () => {
  test('calculates nutrition', () => {
    const product = new ProductBuilder().build();
    // Test actual logic
  });
});
```

---

**Status**: 📋 Design Document  
**Next Steps**: Implementation Phase 1 (Core Builders)  
**Priority**: Medium (Test infrastructure improvement)  
**Dependencies**: None  
**Estimated ROI**: High (significant test readability improvement)
