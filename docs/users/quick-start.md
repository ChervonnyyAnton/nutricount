# 🚀 Quick Start Guide - Nutricount

Welcome to Nutricount! This guide will help you get started with tracking your nutrition and achieving your health goals.

## 📱 What is Nutricount?

Nutricount is a **privacy-focused nutrition tracking application** designed for:
- 🥑 **Keto Diet Followers** - Track net carbs, macros, and keto index
- ⏰ **Intermittent Fasting** - Monitor fasting sessions and progress
- 🎯 **Health Conscious Users** - Complete nutrition tracking with detailed analytics
- 🔒 **Privacy Advocates** - Self-hosted or browser-only mode (no data leaves your device)

---

## 🎯 Getting Started in 5 Minutes

### Option 1: Browser-Only Demo (Easiest)
Perfect for trying out Nutricount without installation:

1. **Open the Demo**
   - Visit: [Demo Version](https://chervonnyyanton.github.io/nutricount/demo/)
   - Or open `demo/index.html` in your browser
   
2. **Start Tracking**
   - Add your first product
   - Log your meal
   - View your daily statistics

**Data Storage**: All data stays in your browser (LocalStorage)
**No Account Needed**: Start using immediately

### Option 2: Self-Hosted (Full Features)
For complete control and backend features:

**Prerequisites**:
- Docker installed
- 30 minutes setup time

**Quick Setup**:
```bash
# 1. Clone repository
git clone https://github.com/ChervonnyyAnton/nutricount.git
cd nutricount

# 2. Configure
cp .env.example .env
nano .env  # Edit your settings

# 3. Start application
docker-compose up -d

# 4. Access
# Open http://localhost:80 in your browser
```

**Default Login** (change immediately):
- Username: `admin`
- Password: `admin123`

---

## 📊 Basic Features

### 1. Product Management
Track foods with complete nutritional information:

**Adding a Product**:
1. Click **Products** tab
2. Click **Add Product** button
3. Enter details:
   - Name (required)
   - Calories per 100g
   - Protein, Fats, Carbs (grams)
   - Optional: Fiber, sugar, vitamins
4. Click **Save**

**Tip**: The app calculates keto index automatically!

### 2. Daily Logging
Record what you eat throughout the day:

**Logging a Meal**:
1. Click **Daily Log** tab
2. Click **Add Entry** button
3. Select:
   - Product or Dish
   - Quantity (grams)
   - Meal time (breakfast, lunch, dinner, snack)
4. Click **Save**

**Real-time Updates**: Watch your daily totals update automatically!

### 3. Statistics & Analytics
Monitor your progress:

**Daily View**:
- Total calories
- Macros breakdown (protein, fats, carbs)
- Keto index score
- Net carbs (for keto)

**Weekly Trends**:
- 7-day overview
- Average daily intake
- Progress charts

### 4. Intermittent Fasting
Track your fasting sessions:

**Starting a Fast**:
1. Click **Fasting** tab
2. Choose fasting type:
   - 16:8 (16 hours fasting, 8 hours eating)
   - 18:6 (18 hours fasting, 6 hours eating)
   - 20:4 (20 hours fasting, 4 hours eating)
   - OMAD (One Meal A Day)
   - Custom
3. Click **Start Fasting**
4. Monitor your progress in real-time

**Ending a Fast**:
- Click **End Fasting** when your fasting window is complete
- View session statistics and history

---

## 🥑 Keto Diet Guide

### Understanding Keto Index
Nutricount calculates a **Keto Index** for each food:

- **90-100**: Excellent for keto (high fat, very low carbs)
- **70-89**: Good for keto (moderate fat, low carbs)
- **50-69**: Moderate (use sparingly)
- **Below 50**: Not ideal for keto (high carbs)

**Formula**:
```
Keto Index = (fat% × 1.0) + (protein% × 0.5) - (carbs% × 2.0)
```

### Net Carbs Calculation
For keto followers, net carbs matter most:

```
Net Carbs = Total Carbs - Fiber
```

Nutricount displays net carbs prominently in all views.

### Keto-Friendly Features
- 🎯 Filter products by keto index
- 📊 Track net carbs daily
- 🔢 Monitor ketogenic ratio (fat:protein:carbs)
- ✅ Visual indicators for keto-friendly foods

---

## ⏰ Intermittent Fasting Guide

### Fasting Types Explained

**16:8 (Most Popular)**
- Fast: 16 hours
- Eating window: 8 hours
- Example: Fast 8 PM - 12 PM, eat 12 PM - 8 PM

**18:6 (Moderate)**
- Fast: 18 hours
- Eating window: 6 hours
- Example: Fast 7 PM - 1 PM, eat 1 PM - 7 PM

**20:4 (Advanced)**
- Fast: 20 hours
- Eating window: 4 hours
- For experienced fasters

**OMAD (One Meal A Day)**
- Fast: 23 hours
- Eating window: 1 hour
- Most restrictive

### Fasting Tips
1. **Start Gradually**: Begin with 16:8 before moving to longer fasts
2. **Stay Hydrated**: Drink water, tea, or black coffee during fasting
3. **Track Progress**: Use Nutricount to monitor fasting duration and patterns
4. **Listen to Your Body**: Stop if you feel unwell
5. **Break Fast Properly**: Start with a light, nutritious meal

### Fasting Statistics
Nutricount tracks:
- Total fasting sessions completed
- Average fasting duration
- Longest fast achieved
- Current streak (consecutive days)
- Success rate

---

## 🍽️ Creating Dishes

For meals you prepare regularly:

**Creating a Dish**:
1. Click **Dishes** tab
2. Click **Add Dish** button
3. Enter dish name
4. Add ingredients:
   - Select product
   - Enter quantity used
   - Click **Add Ingredient**
5. Repeat for all ingredients
6. Click **Save Dish**

**Benefits**:
- Log complex meals quickly
- Automatic nutrition calculation
- Recipe management
- Consistent tracking

---

## 📈 Understanding Your Statistics

### Daily Dashboard
Your main overview shows:

**Calories**
- Target vs. consumed
- Remaining for the day
- Progress bar

**Macros Distribution**
- Protein: X grams (X%)
- Fats: X grams (X%)
- Carbs: X grams (X%)
- Pie chart visualization

**Keto Metrics** (if using keto mode)
- Net carbs consumed
- Ketogenic ratio
- Daily keto index average

### Weekly Trends
Track patterns over 7 days:
- Average daily calories
- Macro consistency
- Best and worst days
- Fasting adherence (if applicable)

### Goals & Targets
Set and track:
- Daily calorie goal
- Macro targets (percentages or grams)
- Net carbs limit (for keto)
- Fasting schedule

---

## ⚙️ Settings & Customization

### Profile Settings
Configure your personal information:

1. Click **Settings** (gear icon)
2. Enter profile data:
   - Age, height, weight
   - Activity level
   - Goals (lose/maintain/gain weight)
3. Set dietary preferences:
   - Standard tracking
   - Keto mode
   - Custom macros
4. Save changes

### Display Preferences
Customize your experience:
- **Theme**: Light or Dark mode
- **Units**: Metric or Imperial
- **Language**: Multiple languages supported
- **Date Format**: DD/MM/YYYY or MM/DD/YYYY

### Notifications
Enable reminders for:
- Meal logging
- Fasting start/end times
- Daily goal check-ins
- Weekly progress updates

---

## 🔒 Privacy & Data

### Browser-Only Mode (Demo)
- ✅ All data stored in your browser
- ✅ No account required
- ✅ No data sent to servers
- ✅ 100% private
- ⚠️ Data cleared if you clear browser cache

**Export Your Data**:
1. Click **Settings** → **Export Data**
2. Save JSON file to your computer
3. Import later if needed

### Self-Hosted Mode
- ✅ Full control of your data
- ✅ Database runs on your device/server
- ✅ Optional cloud sync (if configured)
- ✅ Automated backups

**Data Location**: `nutricount/data/` directory

---

## 🆘 Troubleshooting

### Common Issues

**Q: My data disappeared!**
A: In browser-only mode, clearing cache removes data. Use **Export Data** regularly. In self-hosted mode, check backups in `data/backups/`.

**Q: Calculations seem wrong**
A: Ensure products have accurate nutritional values per 100g. Check that quantities are entered in grams.

**Q: Fasting timer not working**
A: Refresh the page. Enable JavaScript if disabled. Check browser console for errors.

**Q: Can't add products**
A: Verify all required fields (name, calories) are filled. Check for network errors in self-hosted mode.

**Q: How do I reset my password?** (Self-hosted)
A: Use admin panel or run: `docker-compose exec app flask reset-password`

### Getting Help
1. **Documentation**: Check [README.md](../../README.md)
2. **GitHub Issues**: Report bugs at [GitHub](https://github.com/ChervonnyyAnton/nutricount/issues)
3. **Community**: Join discussions (link TBD)

---

## 📱 Mobile Usage

### Progressive Web App (PWA)
Nutricount works great on mobile:

**Installing on Mobile**:
1. Open Nutricount in mobile browser
2. **Android**: Tap menu → "Add to Home Screen"
3. **iOS**: Tap share → "Add to Home Screen"
4. App icon appears on home screen

**Mobile Features**:
- ✅ Full offline support
- ✅ Responsive design
- ✅ Touch-optimized interface
- ✅ Fast and lightweight

---

## 🎯 Best Practices

### For Accurate Tracking
1. **Weigh Your Food**: Use a kitchen scale for precision
2. **Log Immediately**: Record meals right after eating
3. **Be Consistent**: Track every day for best results
4. **Review Weekly**: Check trends every Sunday
5. **Update Products**: Keep product database accurate

### For Keto Success
1. **Track Net Carbs**: Focus on net carbs, not total
2. **High Fat Priority**: Aim for 70-80% fat calories
3. **Moderate Protein**: 15-25% protein is ideal
4. **Low Carbs**: Stay under 20-50g net carbs/day
5. **Use Keto Index**: Choose foods rated 70+

### For Intermittent Fasting
1. **Start Easy**: Begin with 12:12 or 14:10
2. **Stay Consistent**: Fast at the same times daily
3. **Break Fast Wisely**: Start with light, nutritious meal
4. **Track Everything**: Log all fasting sessions
5. **Listen to Body**: Don't force it if unwell

---

## 🚀 Next Steps

### Beginner (Week 1)
- [ ] Add 10 favorite products
- [ ] Log meals for 7 days
- [ ] Review daily statistics
- [ ] Set up profile and goals

### Intermediate (Week 2-4)
- [ ] Create 5 common dishes
- [ ] Try intermittent fasting (16:8)
- [ ] Analyze weekly trends
- [ ] Adjust goals based on progress

### Advanced (Month 2+)
- [ ] Experiment with different fasting protocols
- [ ] Fine-tune macro ratios
- [ ] Export and analyze data
- [ ] Contribute to the project (if technical)

---

## 📚 Additional Resources

### Nutrition Education
- [USDA FoodData Central](https://fdc.nal.usda.gov/) - Accurate nutritional data
- [r/keto](https://reddit.com/r/keto) - Keto diet community
- [r/intermittentfasting](https://reddit.com/r/intermittentfasting) - IF community

### Nutricount Resources
- [User Guide](README.md) - Complete user documentation
- [Keto Guide](keto-guide.md) - Detailed keto diet information
- [Fasting Guide](fasting-guide.md) - Comprehensive fasting guide
- [FAQ](faq.md) - Frequently asked questions

### For Developers
- [Setup Guide](../../PROJECT_SETUP.md) - Local development setup
- [Architecture](../../ARCHITECTURE.md) - System design
- [Contributing](../../CONTRIBUTING.md) - How to contribute

---

## ✉️ Feedback & Support

**Love Nutricount?**
- ⭐ Star us on [GitHub](https://github.com/ChervonnyyAnton/nutricount)
- 📣 Share with friends
- 💬 Join the community

**Found a Bug?**
- 🐛 Report on [GitHub Issues](https://github.com/ChervonnyyAnton/nutricount/issues)

**Have Ideas?**
- 💡 Suggest features in [Discussions](https://github.com/ChervonnyyAnton/nutricount/discussions)

---

**Ready to start tracking?** 🎉

**Browser Demo**: [Open Demo](https://chervonnyyanton.github.io/nutricount/demo/)  
**Self-Hosted**: See [Setup Guide](../../PROJECT_SETUP.md)

**Stay healthy, stay consistent!** 💪

---

**Last Updated**: October 22, 2025  
**Version**: 2.0  
**License**: MIT
