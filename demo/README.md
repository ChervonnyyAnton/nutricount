# 🥗 Nutrition Tracker - Demo Version

**Standalone Single Page Application for public demonstration**

## 🌐 Live Demo

**[Try it now: https://chervonnyyanton.github.io/nutricount/](https://chervonnyyanton.github.io/nutricount/)**

No installation required! Works on all devices (desktop, tablet, phone).

## 🎯 Overview

This is a browser-only demo version of the Nutrition Tracker application. It provides the same functionality as the main application but stores all data locally in your browser using LocalStorage. Perfect for public demonstrations and mobile devices.

## ✨ Features

### Core Features
- ✅ **Product Management** - Add, view, and delete nutrition products
- ✅ **Daily Food Logging** - Track meals throughout the day
- ✅ **Statistics Dashboard** - View daily nutrition totals
- ✅ **Keto Index Calculation** - Automatic keto-friendliness rating
- ✅ **Dark/Light Theme** - Toggle between themes
- ✅ **Mobile Optimized** - Responsive design for all screen sizes
- ✅ **Offline Support** - Works without internet connection
- ✅ **No Server Required** - All data stored locally

### Technical Features
- 📱 Mobile-first responsive design
- 🎨 Dark/Light theme support
- 💾 LocalStorage persistence
- 🔒 Privacy-focused (no server, no tracking)
- ♿ WCAG 2.2 accessibility compliant
- 📊 Real-time nutrition calculations
- 🚀 Fast and lightweight

## 🚀 Quick Start

### Option 1: Open Directly
1. Download `index.html` 
2. Open it in any modern web browser
3. Start tracking your nutrition!

### Option 2: Deploy to Web
Upload `index.html` to any web host (GitHub Pages, Netlify, Vercel, etc.)

### Option 3: Local Development
```bash
# Using Python
python -m http.server 8000

# Using Node.js
npx serve .

# Using PHP
php -S localhost:8000

# Then open http://localhost:8000/demo/
```

## 📱 Mobile Optimized

The demo is specifically optimized for mobile devices:

- ✅ Touch-friendly controls
- ✅ Responsive layout
- ✅ Large tap targets
- ✅ Mobile keyboard support
- ✅ Viewport optimized
- ✅ Minimal data usage (CDN only for Bootstrap)

## 🔐 Privacy & Data

### Data Storage
- All data stored in browser's LocalStorage
- No server communication
- No cookies or tracking
- No external APIs (except Bootstrap CDN)

### Data Persistence
- Data persists between sessions
- Survives browser restarts
- Specific to your browser and device
- Can be cleared with "Clear Data" button

### Data Limits
- LocalStorage limit: ~5-10MB (browser dependent)
- Enough for thousands of products and log entries
- No practical limitations for personal use

## 💡 Usage Guide

### Adding Products
1. Go to **Products** tab
2. Fill in product details:
   - Name (required)
   - Category
   - Calories per 100g (required)
   - Protein, Fat, Carbs (required)
3. Click **Add Product**
4. Product appears in the table with auto-calculated Keto Index

### Logging Meals
1. Go to **Daily Log** tab
2. Select date
3. Choose product from dropdown
4. Enter quantity in grams
5. Select meal time
6. Click **Add to Log**
7. Entry appears in the log table

### Viewing Statistics
1. Go to **Statistics** tab
2. Select date to view
3. View daily totals:
   - Total Calories
   - Total Protein
   - Total Fat
   - Total Carbs
4. See meal count and summary

### Sample Data
Click **Load Sample Data** to populate the app with example products:
- Chicken Breast
- Salmon
- Eggs
- Avocado
- Broccoli
- Almonds
- Spinach
- Blueberries

## 🎨 Theme Support

### Switching Themes
- Click 🌓 button in header
- Toggles between light and dark themes
- Preference saved automatically
- Applies immediately

### Custom Themes
Edit CSS variables in the HTML file:
```css
:root {
    --bg-primary: #ffffff;
    --text-primary: #212529;
    /* etc. */
}

[data-theme="dark"] {
    --bg-primary: #212529;
    --text-primary: #ffffff;
    /* etc. */
}
```

## 🔄 Differences from Main App

### Included Features
- ✅ Product management (add, delete, view)
- ✅ Daily food logging
- ✅ Statistics (daily view)
- ✅ Keto index calculation
- ✅ Theme switching
- ✅ Data persistence

### Not Included (Yet)
- ❌ Dish/Recipe management
- ❌ Weekly statistics
- ❌ Profile management
- ❌ Fasting tracker
- ❌ User authentication
- ❌ Data export/import
- ❌ Advanced analytics
- ❌ Backend synchronization

### Coming Soon
- 🔜 Dish/Recipe support
- 🔜 Weekly statistics
- 🔜 Data export to JSON
- 🔜 IndexedDB for larger datasets
- 🔜 PWA with service worker
- 🔜 Offline mode enhancements

## 🌐 Browser Compatibility

### Supported Browsers
- ✅ Chrome/Edge 90+
- ✅ Firefox 88+
- ✅ Safari 14+
- ✅ Mobile Safari (iOS 14+)
- ✅ Chrome Mobile (Android 9+)
- ✅ Samsung Internet 14+

### Requirements
- JavaScript enabled
- LocalStorage enabled
- Modern CSS support (CSS Variables, Flexbox, Grid)

## 📦 Technical Stack

### Frontend
- HTML5 (semantic markup)
- CSS3 (modern features, CSS Variables)
- Vanilla JavaScript (ES6+)
- Bootstrap 5.3.0 (via CDN)

### Architecture
- Single HTML file (standalone)
- Class-based JavaScript
- LocalStorage for persistence
- No build process required
- No dependencies (except Bootstrap CDN)

### Code Organization
```javascript
// Data Layer
LocalDataStore - Handles LocalStorage operations

// Business Logic
NutritionCalculator - Nutrition calculations

// UI Layer  
UIManager - Toast notifications and formatting
NutritionTrackerDemo - Main application class
```

## 🔧 Customization

### Modifying Sample Data
Edit the `loadSampleProducts()` method:
```javascript
const sampleProducts = [
    { name: 'Your Product', category: 'meat', calories: 100, protein: 20, fat: 5, carbs: 0 },
    // Add more products
];
```

### Adding Categories
Edit the category dropdown in HTML:
```html
<select class="form-select" id="productCategory">
    <option value="your_category">Your Category</option>
    <!-- Add more options -->
</select>
```

### Changing Keto Thresholds
Edit `NutritionCalculator.getKetoRating()`:
```javascript
static getKetoRating(ketoIndex) {
    if (ketoIndex >= 2.0) return 'Excellent';  // Change thresholds
    // ...
}
```

## 📈 Performance

### Metrics
- **Load Time**: <1 second (first load, with CDN)
- **Time to Interactive**: <2 seconds
- **File Size**: ~37KB (minified HTML)
- **Bootstrap CDN**: ~20KB CSS + ~60KB JS (cached)
- **Total**: ~120KB first load, <40KB cached

### Optimization Tips
1. Host Bootstrap locally for faster offline mode
2. Minify HTML for production
3. Enable gzip compression on web server
4. Use service worker for true offline support
5. Consider IndexedDB for large datasets

## 🐛 Troubleshooting

### Data Not Persisting
- Check LocalStorage is enabled in browser
- Verify not in private/incognito mode
- Check browser storage limits
- Try clearing cache and reloading

### Bootstrap Not Loading
- Check internet connection (CDN)
- Use local Bootstrap copy for offline
- Verify CDN URL is accessible
- Check browser console for errors

### Mobile Issues
- Ensure viewport meta tag is present
- Test in multiple mobile browsers
- Check touch event handling
- Verify responsive breakpoints

## 📝 License

Same license as main Nutricount project.

## 🤝 Contributing

To improve the demo:
1. Edit `demo/index.html`
2. Test in multiple browsers/devices
3. Submit PR to main repository
4. Follow existing code style

## 📞 Support

For issues or questions:
- Main Repository: [ChervonnyyAnton/nutricount](https://github.com/ChervonnyyAnton/nutricount)
- Demo-specific issues: Create issue with `[demo]` prefix

## 🎯 Use Cases

### Perfect For
- 👥 Public demonstrations
- 📱 Mobile testing
- 🎓 Educational purposes
- 🚀 Quick prototypes
- 📊 Personal use without server
- 🔒 Privacy-focused users

### Not Suitable For
- 👥 Multi-user scenarios
- 🔄 Data synchronization needs
- 📈 Large-scale analytics
- 🏢 Enterprise deployment
- 💾 Backup requirements

## 🔮 Roadmap

### v1.1 (Next)
- [ ] Add dish/recipe support
- [ ] Implement data export (JSON)
- [ ] Add weekly statistics view
- [ ] Improve mobile UX

### v1.2 (Future)
- [ ] PWA with service worker
- [ ] IndexedDB migration
- [ ] Advanced search/filter
- [ ] Charts and visualizations

### v2.0 (Long-term)
- [ ] Sync with main app
- [ ] Cloud backup option
- [ ] Social features
- [ ] Multi-language support

---

**Demo Version**: 1.0  
**Last Updated**: October 21, 2025  
**Status**: Production Ready ✅
