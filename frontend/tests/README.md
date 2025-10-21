# Frontend Tests

Comprehensive test suite for Nutricount frontend business logic and adapters.

## 📁 Structure

```
frontend/tests/
├── unit/                          # Unit tests for isolated components
│   ├── nutrition-calculator.test.js   # Nutrition calculation tests
│   └── validators.test.js             # Validation function tests
├── integration/                   # Integration tests (planned)
│   ├── api-adapter.test.js           # API adapter with backend
│   └── storage-adapter.test.js       # Storage adapter with LocalStorage
└── README.md                      # This file
```

## 🧪 Running Tests

### Prerequisites

```bash
cd frontend
npm install
```

### Run All Tests

```bash
npm test
```

### Watch Mode (for development)

```bash
npm run test:watch
```

### Coverage Report

```bash
npm run test:coverage
```

This generates a coverage report in `frontend/coverage/` directory.

## ✅ Test Coverage

### Current Status

- **nutrition-calculator.js**: ~95% coverage (target: 90%+)
  - All core functions tested
  - Edge cases covered
  - Formula validation included

- **validators.js**: ~90% coverage (target: 90%+)
  - Product validation complete
  - Dish validation complete
  - Log entry validation complete
  - Edge cases covered

### Coverage Goals

- **Critical modules**: 90%+ coverage
- **Adapters**: 85%+ coverage
- **UI components**: 70%+ coverage (when added)

## 📋 Test Types

### Unit Tests

Test individual functions in isolation:

```javascript
test('should calculate calories correctly', () => {
    expect(calculateCaloriesFromMacros(10, 10, 10)).toBe(130);
});
```

**Benefits:**
- Fast execution
- Easy to debug
- Good for testing logic

### Integration Tests (Planned)

Test components working together:

```javascript
test('should save product via API', async () => {
    const adapter = new ApiAdapter();
    const product = await adapter.createProduct({ name: 'Test' });
    expect(product.id).toBeDefined();
});
```

**Benefits:**
- Test real interactions
- Catch integration issues
- Validate API contracts

### End-to-End Tests (Planned)

Test complete user workflows:

```javascript
test('should log meal and calculate totals', async () => {
    // 1. Create product
    // 2. Log entry
    // 3. Check daily stats
    // 4. Verify calculations
});
```

## 🎯 Testing Best Practices

### 1. Test Naming

Use descriptive test names that explain what is being tested:

```javascript
// ❌ Bad
test('test 1', () => { ... });

// ✅ Good
test('should calculate BMR for male using Mifflin-St Jeor', () => { ... });
```

### 2. Arrange-Act-Assert Pattern

Structure tests clearly:

```javascript
test('should validate product data', () => {
    // Arrange
    const data = { name: 'Test', protein: 20, fats: 10, carbs: 5 };
    
    // Act
    const result = validateProductData(data);
    
    // Assert
    expect(result.valid).toBe(true);
});
```

### 3. Test One Thing

Each test should verify one specific behavior:

```javascript
// ❌ Bad - testing multiple things
test('should work', () => {
    expect(func1()).toBe(true);
    expect(func2()).toBe(false);
    expect(func3()).toBe(10);
});

// ✅ Good - separate tests
test('should return true for valid input', () => {
    expect(func1()).toBe(true);
});

test('should return false for invalid input', () => {
    expect(func2()).toBe(false);
});
```

### 4. Use Descriptive Assertions

```javascript
// ❌ Bad
expect(result).toBeTruthy();

// ✅ Good
expect(result.valid).toBe(true);
expect(result.errors).toHaveLength(0);
```

### 5. Test Edge Cases

```javascript
test('should handle zero values', () => {
    expect(calculateCaloriesFromMacros(0, 0, 0)).toBe(0);
});

test('should not go below zero for net carbs', () => {
    expect(calculateNetCarbs(10, 15)).toBe(0);
});
```

## 🔧 Adding New Tests

### For New Functions

1. Create test file in appropriate directory
2. Import the function to test
3. Write test cases covering:
   - Happy path (normal usage)
   - Edge cases (boundary values)
   - Error cases (invalid input)
   - Integration scenarios

Example:

```javascript
const { newFunction } = require('../../src/new-module');

describe('New Module', () => {
    describe('newFunction', () => {
        test('should handle normal input', () => {
            // Test implementation
        });
        
        test('should handle edge cases', () => {
            // Test implementation
        });
        
        test('should throw error for invalid input', () => {
            // Test implementation
        });
    });
});
```

### For Adapters

Mock external dependencies:

```javascript
// Mock localStorage
const localStorageMock = {
    getItem: jest.fn(),
    setItem: jest.fn(),
    removeItem: jest.fn()
};
global.localStorage = localStorageMock;

// Mock fetch API
global.fetch = jest.fn(() =>
    Promise.resolve({
        json: () => Promise.resolve({ data: mockData })
    })
);
```

## 📊 Coverage Reports

### View Coverage in Terminal

```bash
npm run test:coverage
```

Output shows:

```
File                | % Stmts | % Branch | % Funcs | % Lines
--------------------|---------|----------|---------|--------
nutrition-calc.js   |   95.5  |   92.3   |  100.0  |  95.2
validators.js       |   90.2  |   88.7   |   95.0  |  89.8
```

### View Detailed HTML Report

```bash
npm run test:coverage
open coverage/lcov-report/index.html
```

This shows line-by-line coverage with visual indicators.

## 🐛 Debugging Tests

### Run Specific Test

```bash
npm test -- nutrition-calculator
```

### Run Single Test

```bash
npm test -- -t "should calculate BMR"
```

### Debug with Node Inspector

```bash
node --inspect-brk node_modules/.bin/jest --runInBand
```

Then open Chrome DevTools (chrome://inspect).

## 🚀 Continuous Integration

Tests run automatically on:

- Push to any branch
- Pull request creation/update
- Scheduled nightly builds

See `.github/workflows/test.yml` for CI configuration.

## 📚 Resources

- [Jest Documentation](https://jestjs.io/)
- [Testing Best Practices](https://kentcdodds.com/blog/common-mistakes-with-react-testing-library)
- [Project Testing Guide](../../PROJECT_SETUP.md#testing-guidelines)

## ✨ Contributing

When adding new features:

1. Write tests first (TDD)
2. Ensure tests pass
3. Check coverage (aim for 90%+)
4. Run linting
5. Update documentation

## 📝 Test Checklist

Before submitting PR:

- [ ] All tests pass
- [ ] Coverage meets targets (90%+)
- [ ] No console errors/warnings
- [ ] Tests follow naming conventions
- [ ] Edge cases covered
- [ ] Documentation updated

---

**Last Updated**: October 21, 2025  
**Test Count**: 56 tests (nutrition-calculator: 30, validators: 26)  
**Coverage**: 92% average
