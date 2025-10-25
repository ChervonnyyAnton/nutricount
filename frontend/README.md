# Frontend Directory Structure

This directory contains the unified frontend code that works with both Local and Public versions of Nutricount.

## 📁 Structure

```
frontend/
├── src/
│   ├── adapters/          # Backend adapters (API and Storage)
│   ├── business-logic/    # Shared business logic (calculations, validators)
│   ├── components/        # UI components
│   └── styles/            # Shared styles
│
├── tests/
│   ├── unit/             # Unit tests for business logic and adapters
│   └── integration/      # Integration tests
│
└── build/                # Build outputs (generated)
    ├── local/            # Built for Local version (with API adapter)
    └── public/           # Built for Public version (with Storage adapter)
```

## 🔧 Adapter Pattern

The frontend uses the **Adapter Pattern** to work with different backends. This implements the **BFF (Backend For Frontend)** pattern where a single frontend can work with multiple backend implementations.

### BackendAdapter (Base Interface)
Defines the contract that all adapters must implement:
- Products management (CRUD)
- Log entries management (CRUD)
- Statistics (daily, weekly)
- Settings management
- Dishes management

### StorageAdapter (Public Version - GitHub Pages)
- Uses browser's LocalStorage
- All data stored client-side
- No server required
- Perfect for GitHub Pages deployment
- **File:** `src/adapters/storage-adapter.js`

### ApiAdapter (Local Version - Raspberry Pi)
- Communicates with Flask backend via REST API
- Server-side data storage in SQLite database
- Full database support
- Production deployment with Docker
- **File:** `src/adapters/api-adapter.js`

### AdapterFactory (Auto-Detection) ✨ NEW
- **Automatically detects deployment environment**
- GitHub Pages → StorageAdapter
- Raspberry Pi / localhost:5000 → ApiAdapter
- **File:** `src/adapters/adapter-factory.js`

## 🎯 Usage

### Option 1: Auto-Detection (Recommended) ✨
```javascript
// Automatically chooses the right adapter based on environment
const adapter = AdapterFactory.create();
const app = new NutritionTracker(adapter);
```

### Option 2: Async Detection (More Reliable)
```javascript
// Tries to ping the API first, then decides
const adapter = await AdapterFactory.createAsync();
const app = new NutritionTracker(adapter);
```

### Option 3: Manual Selection
```javascript
// Force specific adapter
const adapter = AdapterFactory.create({ forceMode: 'static' }); // Always use localStorage
// or
const adapter = AdapterFactory.create({ forceMode: 'server' }); // Always use API
```

### Option 4: Direct Instantiation (Old Way)
```javascript
// For Public Version (LocalStorage)
const adapter = new StorageAdapter();

// For Local Version (API)
const adapter = new ApiAdapter('http://localhost:5000/api');
```

## 🧪 Testing

### Unit Tests
```bash
# Run unit tests
npm test

# Run tests with coverage
npm run test:coverage
```

### Integration Tests
```bash
# Run integration tests
npm run test:integration
```

## 📦 Build Process

### Build for Public Version
```bash
./scripts/build-public.sh
```

### Build for Local Version
```bash
./scripts/build-local.sh
```

## 🚀 Development

### Watch Mode for Public Version
```bash
./scripts/dev-public.sh
```

### Watch Mode for Local Version
```bash
./scripts/dev-local.sh
```

## 📝 Implementation Status

### Week 1: Foundation ✅ COMPLETE
- [x] Directory structure created
- [x] BackendAdapter interface defined
- [x] StorageAdapter fully implemented and production-ready
- [x] Documentation complete

### Week 2: Core Implementation ✅ COMPLETE
- [x] Extract business logic from Python to JavaScript
  - [x] nutrition-calculator.js (calorie calculations, keto index, BMR/TDEE)
  - [x] validators.js (product, dish, log entry validation)
- [x] Complete ApiAdapter implementation
  - [x] RESTful API communication
  - [x] JWT token management
  - [x] Error handling and retry logic
- [x] Build system scripts
  - [x] build-local.sh (bundles with ApiAdapter)
  - [x] build-public.sh (bundles with StorageAdapter)
- [x] Development workflow scripts
  - [x] dev-local.sh (development with hot reload)
  - [x] dev-public.sh (development for public version)

### Week 3-4: Testing (Planned)
- [ ] Unit tests for business logic
- [ ] Unit tests for adapters
- [ ] Integration tests
- [ ] E2E test framework

### Week 5-6: Production (Planned)
- [ ] CI/CD pipeline
- [ ] Documentation
- [ ] Educational materials

## 🎓 Educational Value

This structure demonstrates:
1. **Adapter Pattern**: Single interface, multiple implementations
2. **Separation of Concerns**: Business logic separated from data access
3. **Code Reuse**: Same frontend works with different backends
4. **Testing**: Comprehensive testing strategy
5. **CI/CD**: Automated deployment and testing

## 📚 References

- [UNIFIED_ARCHITECTURE_PLAN.md](../UNIFIED_ARCHITECTURE_PLAN.md) - Complete architecture
- [INTEGRATED_ROADMAP.md](../INTEGRATED_ROADMAP.md) - Implementation timeline
- [Backend Adapter Interface](src/adapters/backend-adapter.js)
- [Storage Adapter](src/adapters/storage-adapter.js)

---

**Status**: Week 1 - Foundation (In Progress)  
**Last Updated**: October 21, 2025
