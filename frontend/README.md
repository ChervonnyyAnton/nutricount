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

The frontend uses the Adapter Pattern to work with different backends:

### BackendAdapter (Base Interface)
Defines the contract that all adapters must implement:
- Products management (CRUD)
- Log entries management (CRUD)
- Statistics (daily, weekly)
- Settings management
- Dishes management

### StorageAdapter (Public Version)
- Uses browser's LocalStorage
- All data stored client-side
- No server required
- Perfect for GitHub Pages deployment

### ApiAdapter (Local Version) - Coming Soon
- Communicates with Flask backend via REST API
- Server-side data storage
- Full database support
- Production deployment with Docker

## 🎯 Usage

### For Public Version (LocalStorage)
```javascript
// Use StorageAdapter
const adapter = new StorageAdapter();
const app = new NutritionTracker(adapter);
```

### For Local Version (API)
```javascript
// Use ApiAdapter
const adapter = new ApiAdapter('http://localhost:5000/api');
const app = new NutritionTracker(adapter);
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
- [ ] Extract business logic from Python to JavaScript (Week 2)
- [ ] Create ApiAdapter (Week 2)
- [ ] Add unit tests for adapters (Week 2)

### Week 2: Core Implementation (Planned)
- [ ] Complete ApiAdapter implementation
- [ ] Build system scripts
- [ ] Development workflow scripts
- [ ] Integration with existing frontend

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
