# Command Pattern for Undo/Redo Operations

**Pattern Type**: Behavioral  
**Complexity**: Medium  
**Use Case**: Implementing undo/redo functionality in Nutricount  
**Status**: 📋 Design Document (Implementation Planned)

---

## 🎯 Overview

The Command Pattern encapsulates a request as an object, allowing you to parameterize clients with different requests, queue or log requests, and support undoable operations.

### Benefits for Nutricount

- **User Confidence**: Users can undo mistakes without fear
- **Better UX**: Reduce support requests for accidental deletions
- **Professional Feel**: Standard feature in modern applications
- **Data Safety**: Easy recovery from accidental actions

---

## 📋 Use Cases in Nutricount

### Primary Use Cases

1. **Food Logging**
   - Undo adding food entry
   - Undo deleting food entry
   - Undo editing food entry quantity

2. **Product Management**
   - Undo creating product
   - Undo deleting product
   - Undo editing product nutrition values

3. **Dish Management**
   - Undo creating dish
   - Undo deleting dish
   - Undo editing dish ingredients

4. **Daily Log Operations**
   - Undo clearing daily log
   - Undo bulk operations
   - Undo meal time changes

---

## 🏗️ Pattern Structure

### Core Components

```javascript
// Command Interface
class Command {
  execute() {
    throw new Error('execute() must be implemented');
  }
  
  undo() {
    throw new Error('undo() must be implemented');
  }
  
  redo() {
    return this.execute();
  }
  
  getDescription() {
    return 'Command';
  }
}

// Command Manager (Invoker)
class CommandManager {
  constructor(maxHistorySize = 50) {
    this.history = [];
    this.currentIndex = -1;
    this.maxHistorySize = maxHistorySize;
  }
  
  execute(command) {
    // Remove any commands after current index (redo stack)
    this.history.splice(this.currentIndex + 1);
    
    // Execute command
    command.execute();
    
    // Add to history
    this.history.push(command);
    this.currentIndex++;
    
    // Limit history size
    if (this.history.length > this.maxHistorySize) {
      this.history.shift();
      this.currentIndex--;
    }
    
    this.notifyListeners();
  }
  
  undo() {
    if (this.canUndo()) {
      const command = this.history[this.currentIndex];
      command.undo();
      this.currentIndex--;
      this.notifyListeners();
      return true;
    }
    return false;
  }
  
  redo() {
    if (this.canRedo()) {
      this.currentIndex++;
      const command = this.history[this.currentIndex];
      command.redo();
      this.notifyListeners();
      return true;
    }
    return false;
  }
  
  canUndo() {
    return this.currentIndex >= 0;
  }
  
  canRedo() {
    return this.currentIndex < this.history.length - 1;
  }
  
  clear() {
    this.history = [];
    this.currentIndex = -1;
    this.notifyListeners();
  }
  
  getHistory() {
    return this.history.slice(0, this.currentIndex + 1)
      .map(cmd => cmd.getDescription());
  }
  
  notifyListeners() {
    // Update UI to reflect undo/redo availability
    window.dispatchEvent(new CustomEvent('command-history-changed', {
      detail: {
        canUndo: this.canUndo(),
        canRedo: this.canRedo(),
        history: this.getHistory()
      }
    }));
  }
}
```

---

## 💡 Concrete Command Examples

### 1. Add Food Entry Command

```javascript
class AddFoodEntryCommand extends Command {
  constructor(apiAdapter, entryData) {
    super();
    this.apiAdapter = apiAdapter;
    this.entryData = entryData;
    this.addedEntryId = null;
  }
  
  async execute() {
    const result = await this.apiAdapter.addLog(this.entryData);
    this.addedEntryId = result.id;
    
    // Update UI
    window.dispatchEvent(new CustomEvent('log-entry-added', {
      detail: { entry: result }
    }));
    
    return result;
  }
  
  async undo() {
    if (this.addedEntryId) {
      await this.apiAdapter.deleteLog(this.addedEntryId);
      
      // Update UI
      window.dispatchEvent(new CustomEvent('log-entry-removed', {
        detail: { id: this.addedEntryId }
      }));
    }
  }
  
  getDescription() {
    const itemName = this.entryData.item_name || 'Unknown';
    const quantity = this.entryData.quantity || 0;
    return `Add ${quantity}g of ${itemName}`;
  }
}
```

### 2. Delete Food Entry Command

```javascript
class DeleteFoodEntryCommand extends Command {
  constructor(apiAdapter, entryId) {
    super();
    this.apiAdapter = apiAdapter;
    this.entryId = entryId;
    this.deletedEntry = null;
  }
  
  async execute() {
    // Backup entry before deletion
    this.deletedEntry = await this.apiAdapter.getLog(this.entryId);
    await this.apiAdapter.deleteLog(this.entryId);
    
    // Update UI
    window.dispatchEvent(new CustomEvent('log-entry-removed', {
      detail: { id: this.entryId }
    }));
  }
  
  async undo() {
    if (this.deletedEntry) {
      const result = await this.apiAdapter.addLog(this.deletedEntry);
      this.entryId = result.id;
      
      // Update UI
      window.dispatchEvent(new CustomEvent('log-entry-added', {
        detail: { entry: result }
      }));
    }
  }
  
  getDescription() {
    const itemName = this.deletedEntry?.item_name || 'Unknown';
    return `Delete ${itemName}`;
  }
}
```

### 3. Edit Food Entry Command

```javascript
class EditFoodEntryCommand extends Command {
  constructor(apiAdapter, entryId, newData) {
    super();
    this.apiAdapter = apiAdapter;
    this.entryId = entryId;
    this.newData = newData;
    this.oldData = null;
  }
  
  async execute() {
    // Backup current state
    this.oldData = await this.apiAdapter.getLog(this.entryId);
    
    // Update entry
    await this.apiAdapter.updateLog(this.entryId, this.newData);
    
    // Update UI
    window.dispatchEvent(new CustomEvent('log-entry-updated', {
      detail: { id: this.entryId, data: this.newData }
    }));
  }
  
  async undo() {
    if (this.oldData) {
      await this.apiAdapter.updateLog(this.entryId, this.oldData);
      
      // Update UI
      window.dispatchEvent(new CustomEvent('log-entry-updated', {
        detail: { id: this.entryId, data: this.oldData }
      }));
    }
  }
  
  getDescription() {
    const itemName = this.newData?.item_name || this.oldData?.item_name || 'Unknown';
    return `Edit ${itemName}`;
  }
}
```

### 4. Create Product Command

```javascript
class CreateProductCommand extends Command {
  constructor(apiAdapter, productData) {
    super();
    this.apiAdapter = apiAdapter;
    this.productData = productData;
    this.createdProductId = null;
  }
  
  async execute() {
    const result = await this.apiAdapter.createProduct(this.productData);
    this.createdProductId = result.id;
    
    // Update UI
    window.dispatchEvent(new CustomEvent('product-created', {
      detail: { product: result }
    }));
    
    return result;
  }
  
  async undo() {
    if (this.createdProductId) {
      await this.apiAdapter.deleteProduct(this.createdProductId);
      
      // Update UI
      window.dispatchEvent(new CustomEvent('product-deleted', {
        detail: { id: this.createdProductId }
      }));
    }
  }
  
  getDescription() {
    return `Create product "${this.productData.name}"`;
  }
}
```

---

## 🎨 UI Integration

### Undo/Redo Buttons

```javascript
// Initialize command manager
const commandManager = new CommandManager();

// Listen for history changes
window.addEventListener('command-history-changed', (event) => {
  const { canUndo, canRedo, history } = event.detail;
  
  // Update undo button
  const undoBtn = document.getElementById('undo-btn');
  undoBtn.disabled = !canUndo;
  undoBtn.title = canUndo ? `Undo: ${history[history.length - 1]}` : 'Nothing to undo';
  
  // Update redo button
  const redoBtn = document.getElementById('redo-btn');
  redoBtn.disabled = !canRedo;
});

// Undo button handler
document.getElementById('undo-btn').addEventListener('click', () => {
  commandManager.undo();
});

// Redo button handler
document.getElementById('redo-btn').addEventListener('click', () => {
  commandManager.redo();
});

// Keyboard shortcuts
document.addEventListener('keydown', (event) => {
  // Ctrl+Z or Cmd+Z for undo
  if ((event.ctrlKey || event.metaKey) && event.key === 'z' && !event.shiftKey) {
    event.preventDefault();
    commandManager.undo();
  }
  
  // Ctrl+Shift+Z or Cmd+Shift+Z for redo
  if ((event.ctrlKey || event.metaKey) && event.key === 'z' && event.shiftKey) {
    event.preventDefault();
    commandManager.redo();
  }
  
  // Ctrl+Y or Cmd+Y for redo (Windows style)
  if ((event.ctrlKey || event.metaKey) && event.key === 'y') {
    event.preventDefault();
    commandManager.redo();
  }
});
```

### Toast Notifications

```javascript
function showUndoNotification(commandDescription) {
  const toast = document.createElement('div');
  toast.className = 'toast toast-undo';
  toast.innerHTML = `
    <div class="toast-content">
      <span>${commandDescription}</span>
      <button class="btn-link" onclick="commandManager.undo()">Undo</button>
    </div>
  `;
  
  document.body.appendChild(toast);
  
  setTimeout(() => {
    toast.remove();
  }, 5000);
}

// Show notification after commands
commandManager.execute = (function(originalExecute) {
  return function(command) {
    originalExecute.call(this, command);
    showUndoNotification(command.getDescription());
  };
})(commandManager.execute);
```

---

## 🔧 Implementation Checklist

### Phase 1: Foundation (4 hours)
- [ ] Create `Command` base class
- [ ] Implement `CommandManager` with history
- [ ] Add keyboard shortcuts (Ctrl+Z, Ctrl+Y)
- [ ] Create UI buttons (Undo/Redo)
- [ ] Add unit tests for CommandManager

### Phase 2: Food Logging Commands (3 hours)
- [ ] Implement `AddFoodEntryCommand`
- [ ] Implement `DeleteFoodEntryCommand`
- [ ] Implement `EditFoodEntryCommand`
- [ ] Add integration tests
- [ ] Update logging UI

### Phase 3: Product Commands (2 hours)
- [ ] Implement `CreateProductCommand`
- [ ] Implement `DeleteProductCommand`
- [ ] Implement `EditProductCommand`
- [ ] Add integration tests

### Phase 4: Dish Commands (2 hours)
- [ ] Implement `CreateDishCommand`
- [ ] Implement `DeleteDishCommand`
- [ ] Implement `EditDishCommand`
- [ ] Add integration tests

### Phase 5: Polish (1 hour)
- [ ] Add toast notifications
- [ ] Implement command history panel (optional)
- [ ] Add command descriptions
- [ ] Performance testing
- [ ] User acceptance testing

**Total Estimated Time**: 12 hours

---

## 📊 Testing Strategy

### Unit Tests

```javascript
describe('CommandManager', () => {
  let commandManager;
  let mockCommand;
  
  beforeEach(() => {
    commandManager = new CommandManager();
    mockCommand = {
      execute: jest.fn(),
      undo: jest.fn(),
      redo: jest.fn(),
      getDescription: jest.fn(() => 'Mock Command')
    };
  });
  
  test('executes command and adds to history', () => {
    commandManager.execute(mockCommand);
    
    expect(mockCommand.execute).toHaveBeenCalled();
    expect(commandManager.canUndo()).toBe(true);
    expect(commandManager.canRedo()).toBe(false);
  });
  
  test('undo removes command from history', () => {
    commandManager.execute(mockCommand);
    commandManager.undo();
    
    expect(mockCommand.undo).toHaveBeenCalled();
    expect(commandManager.canUndo()).toBe(false);
    expect(commandManager.canRedo()).toBe(true);
  });
  
  test('redo re-executes command', () => {
    commandManager.execute(mockCommand);
    commandManager.undo();
    commandManager.redo();
    
    expect(mockCommand.redo).toHaveBeenCalled();
    expect(commandManager.canUndo()).toBe(true);
    expect(commandManager.canRedo()).toBe(false);
  });
  
  test('respects max history size', () => {
    const smallManager = new CommandManager(3);
    
    for (let i = 0; i < 5; i++) {
      smallManager.execute(mockCommand);
    }
    
    expect(smallManager.history.length).toBe(3);
  });
});
```

### Integration Tests

```javascript
describe('AddFoodEntryCommand Integration', () => {
  let apiAdapter;
  let command;
  
  beforeEach(() => {
    apiAdapter = new ApiAdapter();
    const entryData = {
      item_type: 'product',
      item_id: 1,
      quantity: 100,
      date: '2025-10-25'
    };
    command = new AddFoodEntryCommand(apiAdapter, entryData);
  });
  
  test('adds entry and can be undone', async () => {
    // Execute
    await command.execute();
    expect(command.addedEntryId).toBeDefined();
    
    // Verify entry exists
    const logs = await apiAdapter.getLogs('2025-10-25');
    expect(logs.some(log => log.id === command.addedEntryId)).toBe(true);
    
    // Undo
    await command.undo();
    
    // Verify entry removed
    const logsAfterUndo = await apiAdapter.getLogs('2025-10-25');
    expect(logsAfterUndo.some(log => log.id === command.addedEntryId)).toBe(false);
  });
});
```

---

## 🎓 Best Practices

### 1. Atomic Operations
Each command should represent a single atomic operation that can be cleanly undone.

```javascript
// ❌ BAD: Multiple unrelated operations
class BadCommand extends Command {
  async execute() {
    await this.addProduct();
    await this.updateSettings();
    await this.sendNotification();
  }
}

// ✅ GOOD: Single atomic operation
class GoodCommand extends Command {
  async execute() {
    await this.addProduct();
  }
}
```

### 2. State Backup
Always backup the old state before making changes.

```javascript
class EditCommand extends Command {
  async execute() {
    // ✅ Backup old state first
    this.oldState = await this.getData();
    
    // Then make changes
    await this.updateData(this.newState);
  }
  
  async undo() {
    // Restore old state
    await this.updateData(this.oldState);
  }
}
```

### 3. Descriptive Names
Provide clear descriptions for command history.

```javascript
class Command {
  getDescription() {
    // ✅ Clear, specific description
    return `Add 100g of Chicken Breast to breakfast`;
    
    // ❌ Vague description
    // return 'Add food';
  }
}
```

### 4. Error Handling
Handle errors gracefully in execute and undo.

```javascript
class SafeCommand extends Command {
  async execute() {
    try {
      await this.performOperation();
    } catch (error) {
      console.error('Command execution failed:', error);
      throw error;
    }
  }
  
  async undo() {
    try {
      await this.revertOperation();
    } catch (error) {
      console.error('Command undo failed:', error);
      // Notify user of undo failure
      this.notifyUndoFailure(error);
    }
  }
}
```

### 5. Memory Management
Limit history size to prevent memory issues.

```javascript
const commandManager = new CommandManager(50); // Keep last 50 commands

// Consider clearing history on page navigation
window.addEventListener('beforeunload', () => {
  commandManager.clear();
});
```

---

## 📖 Additional Resources

### Design Pattern References
- [Gang of Four: Command Pattern](https://en.wikipedia.org/wiki/Command_pattern)
- [Refactoring Guru: Command](https://refactoring.guru/design-patterns/command)
- [JavaScript Design Patterns](https://www.dofactory.com/javascript/design-patterns/command)

### Implementation Examples
- [VS Code Undo/Redo](https://github.com/microsoft/vscode)
- [Redux Action Pattern](https://redux.js.org/tutorials/fundamentals/part-3-state-actions-reducers)
- [Photoshop History Panel](https://helpx.adobe.com/photoshop/using/undo-history.html)

### Related Patterns
- **Memento Pattern**: For saving and restoring object state
- **Chain of Responsibility**: For command processing pipeline
- **Composite Pattern**: For macro commands (multiple commands as one)

---

## 🚀 Future Enhancements

### Macro Commands
Group multiple commands into a single undoable operation.

```javascript
class MacroCommand extends Command {
  constructor(commands) {
    super();
    this.commands = commands;
  }
  
  async execute() {
    for (const command of this.commands) {
      await command.execute();
    }
  }
  
  async undo() {
    // Undo in reverse order
    for (let i = this.commands.length - 1; i >= 0; i--) {
      await this.commands[i].undo();
    }
  }
  
  getDescription() {
    return `${this.commands.length} operations`;
  }
}
```

### Persistent History
Save command history to localStorage for recovery after page reload.

```javascript
class PersistentCommandManager extends CommandManager {
  constructor() {
    super();
    this.loadHistory();
  }
  
  execute(command) {
    super.execute(command);
    this.saveHistory();
  }
  
  saveHistory() {
    const historyData = this.history.map(cmd => cmd.serialize());
    localStorage.setItem('command-history', JSON.stringify(historyData));
  }
  
  loadHistory() {
    const historyData = localStorage.getItem('command-history');
    if (historyData) {
      this.history = JSON.parse(historyData).map(data => 
        Command.deserialize(data)
      );
    }
  }
}
```

### Visual History Panel
Show command history as a visual timeline.

```javascript
function renderHistoryPanel(commandManager) {
  const panel = document.getElementById('history-panel');
  const history = commandManager.getHistory();
  
  panel.innerHTML = history.map((desc, index) => `
    <div class="history-item ${index === commandManager.currentIndex ? 'active' : ''}">
      <span class="history-icon">↻</span>
      <span class="history-description">${desc}</span>
      <button onclick="commandManager.undoTo(${index})">↶</button>
    </div>
  `).join('');
}
```

---

**Status**: 📋 Design Document  
**Next Steps**: Implementation Phase 1 (Foundation)  
**Priority**: Medium (Optional enhancement)  
**Dependencies**: None  
**Estimated ROI**: High (significant UX improvement)
