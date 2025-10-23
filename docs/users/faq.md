# ❓ Frequently Asked Questions (FAQ)

**Last Updated:** October 23, 2025  
**Comprehensive answers to common questions about Nutricount**

## 📋 Table of Contents

1. [General Questions](#general-questions)
2. [Getting Started](#getting-started)
3. [Tracking & Logging](#tracking--logging)
4. [Keto Diet](#keto-diet)
5. [Intermittent Fasting](#intermittent-fasting)
6. [Technical Issues](#technical-issues)
7. [Privacy & Data](#privacy--data)
8. [Features & Functionality](#features--functionality)

---

## 🎯 General Questions

### Q: What is Nutricount?

**A**: Nutricount is a privacy-focused nutrition tracking application designed for:
- Keto diet followers (track net carbs, macros, keto index)
- Intermittent fasting practitioners (monitor fasting sessions)
- Health-conscious users (complete nutrition tracking)
- Privacy advocates (self-hosted or browser-only mode)

Available as a browser demo (no installation) or self-hosted for full features.

### Q: Is Nutricount free?

**A**: Yes! Nutricount is **100% free and open source** under the MIT license. No subscriptions, no ads, no hidden costs.

- **Demo version**: Completely free, use immediately in browser
- **Self-hosted**: Free, requires your own server/computer

### Q: Do I need to create an account?

**A**: Depends on which version you use:

- **Browser Demo**: No account needed, data stored locally in your browser
- **Self-hosted**: Yes, you create your own account during setup

### Q: What makes Nutricount different from other apps?

**A**: Key differentiators:
- 🔒 **Privacy-first**: Your data, your control
- 🆓 **100% Free**: No subscriptions or premium tiers
- 🥑 **Keto-optimized**: Built-in keto index, net carbs tracking
- ⏰ **Fasting integration**: Comprehensive IF tracking
- 💻 **Self-hostable**: Run on your own server
- 📱 **PWA support**: Install as mobile app
- 🌐 **Open source**: Transparent, community-driven

---

## 🚀 Getting Started

### Q: How do I start using Nutricount?

**A**: Two options:

**Option 1 - Browser Demo (Easiest)**:
1. Visit [https://chervonnyyanton.github.io/nutricount/](https://chervonnyyanton.github.io/nutricount/)
2. Start adding products and logging meals immediately
3. No installation or signup required

**Option 2 - Self-Hosted (Full Features)**:
1. Follow [setup guide](../../PROJECT_SETUP.md)
2. Requires Docker and 30 minutes setup time
3. Full control and backend features

### Q: Do I need technical knowledge to use Nutricount?

**A**: 
- **Browser Demo**: No technical knowledge needed at all
- **Self-Hosted**: Basic command-line knowledge helpful but not required (we have step-by-step guides)

### Q: Can I use Nutricount on my phone?

**A**: Yes! Nutricount works great on mobile devices:
- Fully responsive design
- Install as Progressive Web App (PWA)
- Touch-optimized interface
- Works offline after first load

**To install on mobile**:
- **Android**: Menu → "Add to Home Screen"
- **iOS**: Share → "Add to Home Screen"

### Q: What's the difference between demo and self-hosted?

| Feature | Browser Demo | Self-Hosted |
|---------|--------------|-------------|
| Installation | None needed | Docker setup |
| Data Storage | Browser only | Database |
| Account Required | No | Yes |
| Offline Support | Yes | Yes |
| Data Backup | Manual export | Automatic |
| Multi-device Sync | No | Yes (optional) |
| Advanced Features | Limited | All |

---

## 📊 Tracking & Logging

### Q: How do I add a food product?

**A**:
1. Click **Products** tab
2. Click **Add Product** button
3. Enter:
   - Name (required)
   - Calories per 100g
   - Macros: Protein, Fats, Carbs (grams per 100g)
   - Optional: Fiber, sugar, etc.
4. Click **Save**

The app automatically calculates keto index!

### Q: How do I log a meal?

**A**:
1. Click **Daily Log** tab
2. Click **Add Entry** button
3. Select:
   - Product or Dish
   - Quantity (in grams)
   - Meal time (breakfast, lunch, dinner, snack)
4. Click **Save**

Your daily totals update automatically!

### Q: Can I create meals/recipes?

**A**: Yes! Use the **Dishes** feature:
1. Click **Dishes** tab
2. Click **Add Dish** button
3. Enter dish name
4. Add ingredients (select product + quantity)
5. Save dish

Then log the entire dish in one click!

### Q: Do I need to weigh my food?

**A**: **Highly recommended** for accuracy:
- Use a kitchen scale (digital preferred)
- Weigh in grams
- Log exact amount

**Without a scale**: Use rough estimates, but expect less accurate results.

### Q: How do I find nutritional information for foods?

**A**: Best sources:
- [USDA FoodData Central](https://fdc.nal.usda.gov/) - Most accurate
- Food package labels
- MyFitnessPal database (verify accuracy)
- Nutritionix database

**Tip**: Save common foods in Nutricount for quick logging later.

### Q: Can I edit or delete logged entries?

**A**: Yes:
- **Edit**: Click entry → Modify → Save
- **Delete**: Click entry → Delete → Confirm

### Q: How far back can I view my logs?

**A**:
- **Daily View**: Today's logs
- **Weekly View**: Last 7 days
- **History**: All time (depends on version)

---

## 🥑 Keto Diet

### Q: What is the keto index in Nutricount?

**A**: The keto index is a proprietary score (0-100) that indicates how keto-friendly a food is:

- **90-100**: Excellent for keto (high fat, very low carbs)
- **70-89**: Good for keto (moderate fat, low carbs)
- **50-69**: Moderate (use sparingly)
- **Below 50**: Not ideal for keto (high carbs or low fat)

**Formula**: Takes into account fat %, protein %, and carb % of food.

### Q: How does Nutricount calculate net carbs?

**A**:
```
Net Carbs = Total Carbs - Fiber
```

Net carbs are displayed prominently throughout the app. They're what matters most for keto.

### Q: What are good keto macros?

**A**: Typical keto ratios:
- **Fat**: 70-80% of calories
- **Protein**: 15-25% of calories
- **Carbs**: 5-10% of calories (20-50g net carbs/day)

**Nutricount calculates personalized macros** based on your:
- Age, height, weight
- Activity level
- Goals (lose/maintain/gain weight)

Set up in **Settings** → **Profile**.

### Q: How do I stay in ketosis using Nutricount?

**A**: Track these daily:
1. **Net Carbs**: Stay under 20-50g/day
2. **Keto Index**: Aim for average above 70
3. **Macros**: Hit your fat/protein targets
4. **Ketogenic Ratio**: Nutricount calculates automatically

The app will show you if you're on track!

### Q: Can I use Nutricount if I'm not doing keto?

**A**: **Absolutely!** Nutricount works for any diet:
- Standard calorie tracking
- Macro tracking (any ratios)
- General nutrition monitoring
- Weight management

Just don't worry about the keto-specific features.

---

## ⏰ Intermittent Fasting

### Q: How do I track my fasting with Nutricount?

**A**:
1. Go to **Fasting** tab
2. Choose fasting type (16:8, 18:6, 20:4, OMAD, Custom)
3. Click **Start Fasting**
4. Monitor real-time progress
5. Click **End Fasting** when done

The app tracks duration, shows milestones, and saves statistics!

### Q: What fasting protocols does Nutricount support?

**A**: All major IF protocols:
- **16:8** (16-hour fast, 8-hour eating window)
- **18:6** (18-hour fast, 6-hour window)
- **20:4** (20-hour fast, 4-hour window)
- **OMAD** (One Meal A Day - 23:1)
- **Custom** (set your own duration)

Plus alternate day fasting (ADF) and 5:2 diet tracking.

### Q: Can I pause my fast?

**A**: Yes! If you need to eat something (medical reasons, feeling unwell):
1. Click **Pause** button
2. Timer stops
3. Resume later by clicking **Resume**
4. Or **End** to complete the session early

**No judgment!** Listen to your body.

### Q: What breaks a fast in Nutricount?

**A**: 
**Technically**: Anything with calories breaks a fast.

**Nutricount logs it as broken if you**:
- Log food during fasting window
- Manually end/cancel the fast

**Won't break fast**:
- Black coffee, tea
- Water
- Tracking these doesn't affect your fast

### Q: What fasting statistics does Nutricount track?

**A**: Comprehensive stats:
- Total fasting sessions completed
- Success rate (%)
- Average fasting duration
- Longest fast achieved
- Current streak (consecutive days)
- Total hours fasted
- Weekly patterns
- Monthly trends

View in **Fasting** tab → **Statistics**.

### Q: Can I combine keto and fasting in Nutricount?

**A**: **Yes!** They work great together:
- Track both simultaneously
- Keto makes fasting easier (fewer hunger)
- Fasting enhances ketosis
- All metrics in one app

Many users do 16:8 IF + keto diet successfully!

---

## 🔧 Technical Issues

### Q: My data disappeared! What happened?

**A**: Depends on version:

**Browser Demo**:
- Data stored in browser LocalStorage
- Cleared if you clear browser cache/history
- **Solution**: Use **Export Data** regularly (Settings → Export)

**Self-Hosted**:
- Data in database (shouldn't disappear)
- Check backups in `data/backups/` directory
- **Solution**: Restore from backup

**Prevention**: 
- Export data weekly (browser version)
- Enable automatic backups (self-hosted)

### Q: The app isn't loading / showing errors

**A**: Troubleshooting steps:

1. **Refresh the page** (Ctrl+R or Cmd+R)
2. **Clear browser cache**:
   - Chrome: Ctrl+Shift+Delete
   - Firefox: Ctrl+Shift+Delete
3. **Check JavaScript is enabled**
4. **Try different browser** (Chrome, Firefox, Safari)
5. **Check browser console** for errors (F12)

**Self-hosted**: Check Docker containers are running:
```bash
docker-compose ps
docker-compose logs
```

### Q: Calculations seem wrong / numbers don't add up

**A**: Common causes:

1. **Product data entered incorrectly**:
   - Ensure nutrition per 100g (not per serving)
   - Check for typos in numbers
   - Verify against USDA database

2. **Quantity logged wrong**:
   - Log in grams, not servings
   - Check decimal points

3. **Rounding differences**:
   - Normal for small amounts
   - Check source data matches

**Fix**: Edit product → Correct values → Re-log meal

### Q: Fasting timer not working

**A**: Try:
1. **Refresh the page**
2. **Check time zone settings** (device vs. app)
3. **Enable JavaScript**
4. **Check browser console** (F12) for errors
5. **Try different browser**

If problem persists, report on [GitHub Issues](https://github.com/ChervonnyyAnton/nutricount/issues).

### Q: Can't log into self-hosted version

**A**: Check:
1. **Username/password correct?**
2. **Caps Lock off?**
3. **Account created?** Run setup script again
4. **Check server logs**:
   ```bash
   docker-compose logs nutrition-tracker
   ```
5. **Reset password** (if you remember username):
   ```bash
   docker-compose exec app flask reset-password
   ```

### Q: How do I reset my password? (Self-hosted)

**A**:
```bash
cd nutricount
docker-compose exec app flask reset-password
# Follow prompts
```

Or access admin panel (Ctrl+Alt+A) if logged in as admin.

---

## 🔒 Privacy & Data

### Q: Where is my data stored?

**A**: 

**Browser Demo**:
- Stored in your browser's LocalStorage
- Never sent to any server
- 100% private and local

**Self-Hosted**:
- Stored in SQLite database on your server/computer
- Location: `nutricount/data/nutrition.db`
- Full control, no external sharing

### Q: Is my data shared with anyone?

**A**: **No, never!**

- Browser demo: Data never leaves your device
- Self-hosted: Data stays on your server
- No analytics or tracking
- No third-party services
- Open source (verify yourself!)

### Q: How do I export my data?

**A**:
1. Click **Settings** (gear icon)
2. Go to **Data Management** section
3. Click **Export Data**
4. Save JSON file to computer

**Use cases**:
- Backup your data
- Switch devices
- Analyze in Excel/Python
- Share with nutritionist

### Q: How do I import data?

**A**:
1. Settings → Data Management
2. Click **Import Data**
3. Select previously exported JSON file
4. Confirm import

**Note**: Imports merge with existing data (doesn't overwrite).

### Q: What if I clear my browser cache?

**A**: 

**Browser Demo**: 
- **All data will be lost!**
- **Solution**: Export data regularly

**Self-Hosted**:
- No effect (data in database, not cache)

### Q: Can I sync data across devices?

**A**:

**Browser Demo**: No built-in sync
- Workaround: Export from device A, import to device B

**Self-Hosted**: Yes! (if configured)
- Access same server from multiple devices
- Automatic sync via database
- Requires network access to server

---

## 🎯 Features & Functionality

### Q: Can I set goals/targets?

**A**: Yes! In **Settings** → **Profile**:
- Daily calorie goal
- Macro targets (percentages or grams)
- Net carbs limit
- Fasting schedule
- Weight goal

The app tracks progress vs. goals daily.

### Q: Does Nutricount calculate my calorie needs?

**A**: Yes! Based on:
- Age, height, weight
- Sex
- Activity level
- Goal (lose/maintain/gain weight)

Go to **Settings** → **Profile** → **Calculate Macros**

### Q: Can I track water intake?

**A**: Not currently a dedicated feature, but you can:
- Add "Water" as a product (0 calories)
- Log water as entries throughout day

**Future feature**: Dedicated water tracking planned!

### Q: Can I track vitamins/minerals?

**A**: Limited support:
- Some products allow entering micronutrients
- Not prominently displayed
- Focus is on macronutrients

**Future feature**: Enhanced micronutrient tracking planned!

### Q: Is there a barcode scanner?

**A**: Not currently available.

**Workaround**:
- Search product online (USDA database)
- Add to Nutricount manually
- Save for future use

**Future feature**: Barcode scanning is on roadmap!

### Q: Can I share meals/recipes with others?

**A**: Not directly in-app, but you can:
1. Export your dish as JSON
2. Share file with friends
3. They import into their Nutricount

**Future feature**: Built-in sharing planned!

### Q: Does Nutricount work offline?

**A**: Yes! (with limitations)

**Browser Demo**:
- Works offline after first load
- PWA caching enabled
- All features available offline

**Self-Hosted**:
- Works offline if server on local network
- Remote server needs internet connection

### Q: Can I change themes/appearance?

**A**: Yes! Settings → Appearance:
- Light mode
- Dark mode (default)
- Multiple color themes
- Font size adjustment

### Q: What languages does Nutricount support?

**A**: Currently: **English only**

**Future feature**: Multi-language support planned!
- Community translations welcome
- See [CONTRIBUTING.md](../../CONTRIBUTING.md)

---

## 🆘 Getting More Help

### Q: I have a question not answered here

**A**: Additional resources:

1. **Documentation**:
   - [Quick Start Guide](quick-start.md)
   - [Keto Guide](keto-guide.md)
   - [Fasting Guide](fasting-guide.md)
   - [Setup Guide](../../PROJECT_SETUP.md)

2. **Community**:
   - [GitHub Discussions](https://github.com/ChervonnyyAnton/nutricount/discussions) (coming soon)
   - [GitHub Issues](https://github.com/ChervonnyyAnton/nutricount/issues) (bug reports)

3. **Source Code**:
   - [GitHub Repository](https://github.com/ChervonnyyAnton/nutricount)
   - Read the code (it's open source!)

### Q: I found a bug, how do I report it?

**A**: 
1. Check [existing issues](https://github.com/ChervonnyyAnton/nutricount/issues)
2. If new, create an issue:
   - Describe the problem
   - Steps to reproduce
   - Expected vs. actual behavior
   - Screenshots (if applicable)
   - Browser/device info

### Q: I want to request a feature

**A**:
1. Check if [already requested](https://github.com/ChervonnyyAnton/nutricount/issues)
2. Open new issue with "Feature Request" label
3. Describe:
   - What you want
   - Why it's useful
   - How it should work

Or contribute it yourself! (See [CONTRIBUTING.md](../../CONTRIBUTING.md))

### Q: Can I contribute to Nutricount?

**A**: **Yes, please!** We welcome:
- 🐛 Bug fixes
- ✨ New features
- 📝 Documentation improvements
- 🌍 Translations
- 🎨 UI/UX enhancements
- 🧪 Testing

See [CONTRIBUTING.md](../../CONTRIBUTING.md) for guidelines.

---

## 💡 Tips & Best Practices

### Q: What's the best way to use Nutricount?

**A**: Recommended workflow:

**Morning**:
1. Check yesterday's stats (learn from data)
2. Plan today's meals (stay on track)
3. Start fasting timer (if doing IF)

**Throughout Day**:
1. Log meals immediately after eating (don't forget!)
2. Check macro progress (adjust dinner if needed)
3. Monitor fasting timer (if applicable)

**Evening**:
1. Review daily totals (celebrate wins!)
2. Plan tomorrow's meals (prepare for success)
3. Export data weekly (backup!)

**Weekly**:
1. Review trends (what's working?)
2. Adjust goals (if needed)
3. Meal prep (save time)

**Consistency is key!** Track every day for best results.

### Q: How can I make tracking easier?

**A**: Time-saving tips:

1. **Save common foods**: Add once, log quickly later
2. **Create dishes**: Log complex meals in one click
3. **Use similar feature**: Copy yesterday's breakfast
4. **Meal prep**: Cook in bulk, log once
5. **Set reminders**: Phone alarm for logging
6. **Track immediately**: Don't wait, do it now
7. **Keep it simple**: Don't obsess over tiny amounts

### Q: Any tips for beginners?

**A**: Start right:

**Week 1**:
- Focus on consistency (log every day)
- Don't worry about perfection
- Learn the app features
- Explore product database

**Week 2**:
- Start hitting macro targets
- Experiment with dishes
- Try different meal timings
- Find what works for you

**Week 3+**:
- Review trends weekly
- Adjust goals based on progress
- Get more precise with logging
- Help others get started!

**Remember**: Progress, not perfection!

---

**Still have questions?**  
Ask in [GitHub Discussions](https://github.com/ChervonnyyAnton/nutricount/discussions) (coming soon)!

---

**Last Updated**: October 23, 2025  
**Version**: 1.0  
**Need to report an issue?** [GitHub Issues](https://github.com/ChervonnyyAnton/nutricount/issues)
