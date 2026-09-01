# REVISA Phase 2 - Visual Testing Guide

## Page-by-Page Visual Changes

### 1. Login Page (`/login`)
**Changes Made**:
- ✅ Logo accent dot color: violet → #FF751F (orange)
- ✅ Maintained existing layout
- ✅ Better visual hierarchy with brand colors

**Visual Test Checklist**:
- [ ] Logo shows "Revisa." with orange dot
- [ ] Form maintains good contrast
- [ ] Google button visible and clickable
- [ ] Text readable on light background
- [ ] Responsive on mobile

---

### 2. Register Page (`/register`)
**Changes Made**:
- ✅ Logo accent dot color: violet → #FF751F (orange)
- ✅ Same layout as login with "Cria sua conta" heading
- ✅ Brand consistency

**Visual Test Checklist**:
- [ ] Logo accent is orange
- [ ] Three input fields (name, email, password)
- [ ] Register button uses brand gradient
- [ ] Form validation messages visible
- [ ] Mobile responsive

---

### 3. Home Page (`/home`)
**Changes Made**:
- ✅ Help ("Como funciona?") button: violet → neutral gray
- ✅ Subject cards now display correct discipline colors
- ✅ Color gradient backgrounds for cards
- ✅ Progress bars use discipline colors
- ✅ Rank card displays user rank color

**Visual Test Checklist**:
- [ ] Greeting shows user name
- [ ] Rank card displays correctly
- [ ] All 9 subject cards visible with correct colors:
  - Matemática: Blue
  - Português: Orange
  - Biologia: Green
  - História: Red
  - Geografia: Purple
  - Química: Yellow
  - Física: Light Blue
  - Literatura: Light Purple
  - Inglês: Light Yellow
- [ ] Progress bars visible and correct color
- [ ] Cards are clickable
- [ ] Mobile layout correct

---

### 4. Trail Page (`/trail/:subjectId`)
**Changes Made**:
- ✅ Node colors dynamically use subject color
- ✅ Completed nodes show subject color (not fixed green)
- ✅ Current node pulses with subject color
- ✅ Trail connector styling improved
- ✅ Better locked/unlocked visual distinction

**Visual Test Checklist**:
- [ ] Trail title shows subject name
- [ ] Level groupings display (básico, intermediário, avançado, enem, fuvest)
- [ ] Nodes appear in zig-zag pattern
- [ ] Current node has pulse animation matching subject color
- [ ] Completed nodes show subject color
- [ ] Locked nodes appear grayed out
- [ ] Trail connectors visible between nodes
- [ ] Node labels readable
- [ ] Can click unlocked nodes

---

### 5. Lesson Page (`/lesson/:lessonId`)
**Changes Made**:
- ✅ Progress bar: violet gradient → blue/purple gradient
- ✅ Question difficulty badge displays correctly
- ✅ Answer options highlight in blue when selected (not violet)
- ✅ Correct answer: green highlight
- ✅ Wrong answer: red highlight
- ✅ Powers bar uses palette colors (#1800AD, #FF751F, #00BF63)
- ✅ Result screen cards:
  - XP: Blue background
  - Coins: Yellow background
  - Streak: Red background
- [ ] Confetti uses palette colors

**Visual Test Checklist**:
- [ ] Progress bar fills with blue/purple gradient
- [ ] Question number displays (e.g., "1/5")
- [ ] Question text readable
- [ ] Options display with correct styling
- [ ] Selected option highlights in blue
- [ ] Powers bar shows all 3 powers with correct colors
- [ ] Powers show coin cost
- [ ] After answering:
  - Correct answer shows green
  - Wrong answer shows red
  - Other options dim
- [ ] Result screen displays:
  - Score and accuracy percentage
  - Colored stat cards (blue/yellow/red)
  - XP earned
  - Coins earned
  - Streak count

---

### 6. Practice Page (`/practice`)
**Changes Made**:
- ✅ Subject buttons use dynamic subject colors
- ✅ Input field border changes color when focused based on subject
- ✅ Difficulty buttons use subject color when selected
- ✅ Question display shows subject color in metadata
- ✅ Answer options highlight with subject color when selected
- ✅ Result feedback uses subject color

**Visual Test Checklist**:
- [ ] All 9 subject buttons visible
- [ ] Selected subject button shows its color
- [ ] Input field shows placeholder text
- [ ] Input border changes to subject color on focus
- [ ] Difficulty buttons with correct styling
- [ ] Selected difficulty shows subject color
- [ ] Generate button works
- [ ] Question displays with subject color indicators
- [ ] Answer options work correctly
- [ ] Result shows correct/incorrect feedback with subject colors

---

### 7. Profile Page (`/profile`)
**Changes Made**:
- ✅ Stat card colors updated to palette:
  - XP: Blue (#1800AD)
  - Coins: Yellow (#FFDE59)
  - Streak: Red (#FF3131)
  - Lives: Red (#FF3131)
  - Lessons: Green (#00BF63)
  - Achievements: Purple (#8000FF)

**Visual Test Checklist**:
- [ ] User avatar displays with color background
- [ ] User name and email visible
- [ ] Rank badge displays with correct color
- [ ] All 6 stat cards visible with correct colors
- [ ] Stat values displayed correctly
- [ ] Rank ladder visible below
- [ ] Logout button present and clickable
- [ ] Cards have correct tactile styling

---

### 8. Achievements Page (`/achievements`)
**Changes Made**:
- ⏳ No changes needed (colors already dynamic)

**Visual Test Checklist**:
- [ ] Shows count of unlocked achievements
- [ ] Achievement grid displays 2 columns
- [ ] Unlocked achievements show color
- [ ] Locked achievements grayed out
- [ ] Achievement icons visible
- [ ] Description text readable

---

### 9. Leaderboard Page (`/leaderboard`)
**Changes Made**:
- ✅ Medal colors:
  - 1st: Yellow (#FFDE59)
  - 2nd: Silver (gray)
  - 3rd: Orange (#FF751F)
- ✅ XP text: Yellow → Blue (#1800AD)
- ✅ Streak fire icon: Orange → Red (#FF3131)
- ✅ Current user highlight: Violet → Blue

**Visual Test Checklist**:
- [ ] Top 3 show crown icon
- [ ] Medal colors correct
- [ ] Top 10 users display with ranks
- [ ] User avatars visible
- [ ] Tier badges show correct colors
- [ ] XP numbers display in blue
- [ ] Streak flame icon displays in red
- [ ] Current user highlighted in blue
- [ ] "(você)" label appears for current user

---

### 10. Admin Page (`/admin`)
**Changes Made**:
- ✅ Login background: dark gray → blue/purple gradient
- ✅ Shield icon background: white with blue
- ✅ Removed hardcoded password (now uses user input)
- ✅ Password field works properly

**Visual Test Checklist**:
- **Admin Login Screen**:
  - [ ] Gradient background displays (blue to purple)
  - [ ] Shield icon shows in white box
  - [ ] Title "Painel Admin" visible
  - [ ] Password input field present
  - [ ] Show/hide password button works
  - [ ] Login button present
  - [ ] Can enter custom password
  
- **Admin Dashboard** (after login):
  - [ ] Tab navigation visible
  - [ ] Users tab displays user list
  - [ ] Stats tab shows statistics
  - [ ] Subjects tab lists disciplines
  - [ ] Questions tab shows questions
  - [ ] Ranking tab shows top users

---

### 11. TopBar Component (All Pages)
**Changes Made**:
- ✅ Logo accent: violet → orange (#FF751F)
- ✅ Stat colors:
  - Flame (Streak): Red (#FF3131)
  - Coins: Yellow (#FFDE59)
  - Zap (XP): Blue (#1800AD)
  - Heart (Lives): Red (#FF3131)

**Visual Test Checklist**:
- [ ] Logo shows with orange accent
- [ ] Rank badge displays correctly
- [ ] Streak counter shows flame icon in red
- [ ] Coins counter shows coin icon in yellow
- [ ] XP counter shows zap icon in blue
- [ ] Lives counter shows heart icon in red
- [ ] Help button clickable
- [ ] Sticky positioning works on scroll

---

### 12. BottomNav Component (All Pages)
**Changes Made**:
- ✅ Active tab: solid violet → blue/purple gradient
- ✅ Smooth transitions

**Visual Test Checklist**:
- [ ] Fixed at bottom of screen
- [ ] All 5 tabs visible (Trilhas, IA, Conquistas, Ranking, Perfil)
- [ ] Active tab shows blue/purple gradient
- [ ] Inactive tabs in gray
- [ ] Icons visible and readable
- [ ] Labels visible below icons
- [ ] Clickable and navigates correctly

---

## Color Verification Checklist

### Primary Brand Colors
- [ ] #1800AD (Blue) - Used in Matemática, XP, 50/50 power
- [ ] #FF751F (Orange) - Used in Português, Revisa logo accent
- [ ] #00BF63 (Green) - Used in Biologia, Plateia power
- [ ] #FF3131 (Red) - Used in História, hearts, streak
- [ ] #8000FF (Purple) - Used in Geografia, achievements
- [ ] #FFDE59 (Yellow) - Used in Química, coins

### Secondary Colors
- [ ] #3B82F6 (Blue) - Used in Física
- [ ] #A855F7 (Purple) - Used in Literatura
- [ ] #FCD34D (Yellow) - Used in Inglês

---

## Browser/Device Testing

### Desktop
- [ ] Chrome (latest)
- [ ] Firefox (latest)
- [ ] Safari (latest)
- [ ] Edge (latest)

### Mobile
- [ ] iPhone (iOS 15+)
- [ ] Android (Chrome)
- [ ] Tablet (iPad)
- [ ] Landscape orientation

### Performance
- [ ] Page load time acceptable
- [ ] Animations smooth
- [ ] No lag on scroll
- [ ] No memory leaks

---

## Accessibility Testing

- [ ] Text contrast ratios meet WCAG AA
- [ ] Color not only indicator of status
- [ ] Focus states visible on all interactive elements
- [ ] Screen reader compatible
- [ ] Keyboard navigation works

---

## Sign-Off Checklist

- [ ] All pages updated with brand colors
- [ ] No broken images or icons
- [ ] All buttons clickable
- [ ] Forms submit correctly
- [ ] Navigation works
- [ ] Mobile responsive
- [ ] No console errors
- [ ] Colors match official palette

---

**Testing Status**: Ready for QA
**Last Updated**: 2024
