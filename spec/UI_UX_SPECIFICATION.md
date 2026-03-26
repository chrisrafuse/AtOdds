# UI_UX_SPECIFICATION.md
## AtOdds Web Dashboard UI/UX Specification
Version: 1.0  
Author: Chris Rafuse  
Last Updated: March 26, 2026

---

# 1. OVERVIEW

## 1.1 Purpose
Define the user interface and user experience requirements for the AtOdds web dashboard, a vanilla JavaScript application for analyzing betting odds and detecting market opportunities.

## 1.2 Design Philosophy
- **Clarity First**: Information hierarchy optimized for quick decision-making
- **Performance**: Fast load times, smooth interactions
- **Accessibility**: WCAG 2.1 AA compliant
- **Responsiveness**: Mobile-first, works on all screen sizes
- **Progressive**: Works without JavaScript for basic functionality
- **Professional**: Clean, modern aesthetic suitable for financial analysis

## 1.3 Target Users
- **Primary**: Sports betting analysts and traders
- **Secondary**: Casual bettors seeking value
- **Technical Level**: Varied (beginner to expert)

---

# 2. VISUAL DESIGN

## 2.1 Color Palette

### Primary Colors
```css
--cr-primary: #2563eb;        /* Blue - Primary actions, links */
--cr-primary-hover: #1d4ed8;  /* Darker blue - Hover states */
--cr-primary-light: #dbeafe;  /* Light blue - Backgrounds */
```

### Semantic Colors
```css
--cr-success: #10b981;        /* Green - Arbitrage, positive findings */
--cr-warning: #f59e0b;        /* Amber - Value edges, caution */
--cr-danger: #ef4444;         /* Red - Errors, critical alerts */
--cr-info: #3b82f6;           /* Blue - Informational messages */
--cr-neutral: #6b7280;        /* Gray - Neutral elements */
```

### Background Colors
```css
--cr-bg-primary: #ffffff;     /* White - Main background */
--cr-bg-secondary: #f9fafb;   /* Light gray - Secondary background */
--cr-bg-tertiary: #f3f4f6;    /* Lighter gray - Cards, panels */
--cr-bg-dark: #111827;        /* Dark - Dark mode primary */
```

### Text Colors
```css
--cr-text-primary: #111827;   /* Almost black - Primary text */
--cr-text-secondary: #6b7280; /* Gray - Secondary text */
--cr-text-tertiary: #9ca3af;  /* Light gray - Tertiary text */
--cr-text-inverse: #ffffff;   /* White - Text on dark backgrounds */
```

### Border Colors
```css
--cr-border: #e5e7eb;         /* Light gray - Default borders */
--cr-border-hover: #d1d5db;   /* Medium gray - Hover borders */
--cr-border-focus: #2563eb;   /* Blue - Focus borders */
```

## 2.2 Typography

### Font Family
```css
--cr-font-sans: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, 
                "Helvetica Neue", Arial, sans-serif;
--cr-font-mono: "SF Mono", Monaco, "Cascadia Code", "Roboto Mono", 
                Consolas, monospace;
```

### Font Sizes
```css
--cr-text-xs: 0.75rem;    /* 12px - Small labels */
--cr-text-sm: 0.875rem;   /* 14px - Secondary text */
--cr-text-base: 1rem;     /* 16px - Body text */
--cr-text-lg: 1.125rem;   /* 18px - Large text */
--cr-text-xl: 1.25rem;    /* 20px - Headings */
--cr-text-2xl: 1.5rem;    /* 24px - Large headings */
--cr-text-3xl: 1.875rem;  /* 30px - Page titles */
```

### Font Weights
```css
--cr-font-normal: 400;
--cr-font-medium: 500;
--cr-font-semibold: 600;
--cr-font-bold: 700;
```

### Line Heights
```css
--cr-leading-tight: 1.25;
--cr-leading-normal: 1.5;
--cr-leading-relaxed: 1.75;
```

## 2.3 Spacing System
```css
--cr-space-1: 0.25rem;   /* 4px */
--cr-space-2: 0.5rem;    /* 8px */
--cr-space-3: 0.75rem;   /* 12px */
--cr-space-4: 1rem;      /* 16px */
--cr-space-5: 1.25rem;   /* 20px */
--cr-space-6: 1.5rem;    /* 24px */
--cr-space-8: 2rem;      /* 32px */
--cr-space-10: 2.5rem;   /* 40px */
--cr-space-12: 3rem;     /* 48px */
--cr-space-16: 4rem;     /* 64px */
```

## 2.4 Border Radius
```css
--cr-radius-sm: 0.25rem;   /* 4px - Small elements */
--cr-radius-md: 0.375rem;  /* 6px - Default */
--cr-radius-lg: 0.5rem;    /* 8px - Cards, panels */
--cr-radius-xl: 0.75rem;   /* 12px - Large elements */
--cr-radius-full: 9999px;  /* Fully rounded */
```

## 2.5 Shadows
```css
--cr-shadow-sm: 0 1px 2px 0 rgba(0, 0, 0, 0.05);
--cr-shadow-md: 0 4px 6px -1px rgba(0, 0, 0, 0.1);
--cr-shadow-lg: 0 10px 15px -3px rgba(0, 0, 0, 0.1);
--cr-shadow-xl: 0 20px 25px -5px rgba(0, 0, 0, 0.1);
```

---

# 3. LAYOUT STRUCTURE

## 3.1 Grid System
- **Container Max Width**: 1280px
- **Gutter**: 24px (desktop), 16px (mobile)
- **Columns**: 12-column grid
- **Breakpoints**:
  - Mobile: 0-640px
  - Tablet: 641-1024px
  - Desktop: 1025px+

## 3.2 Page Layout
```
┌─────────────────────────────────────────────┐
│ Header (64px height)                        │
│ Logo | Navigation | Actions                 │
├─────────────────────────────────────────────┤
│ Main Content Area                           │
│ ┌─────────────────┐ ┌───────────────────┐  │
│ │ Left Panel      │ │ Right Panel       │  │
│ │ (Upload/Control)│ │ (Chat/Help)       │  │
│ │                 │ │                   │  │
│ └─────────────────┘ └───────────────────┘  │
│ ┌─────────────────────────────────────────┐ │
│ │ Results Area                            │ │
│ │ Summary Cards | Findings Table          │ │
│ │ Charts | Detailed Views                 │ │
│ └─────────────────────────────────────────┘ │
├─────────────────────────────────────────────┤
│ Footer (48px height)                        │
│ Links | Version | Status                    │
└─────────────────────────────────────────────┘
```

## 3.3 Responsive Behavior

### Desktop (1025px+)
- Three-column layout
- Side panels visible
- Full data tables
- Expanded charts

### Tablet (641-1024px)
- Two-column layout
- Collapsible side panels
- Scrollable tables
- Responsive charts

### Mobile (0-640px)
- Single-column layout
- Stacked sections
- Hamburger menu
- Touch-optimized controls
- Simplified tables (cards)

---

# 4. COMPONENTS

## 4.1 Header Component

### Structure
```html
<header class="cr-header">
  <div class="cr-header-logo">
    <img src="logo.svg" alt="AtOdds">
    <span class="cr-header-title">AtOdds</span>
  </div>
  <nav class="cr-header-nav">
    <a href="#analyze">Analyze</a>
    <a href="#results">Results</a>
    <a href="#chat">Chat</a>
  </nav>
  <div class="cr-header-actions">
    <button class="cr-btn cr-btn-primary">Upload Data</button>
  </div>
</header>
```

### Specifications
- **Height**: 64px
- **Background**: White with bottom border
- **Logo**: 32px height
- **Sticky**: Fixed to top on scroll
- **Shadow**: Appears on scroll

## 4.2 Button Component

### Variants
```html
<!-- Primary -->
<button class="cr-btn cr-btn-primary">Analyze</button>

<!-- Secondary -->
<button class="cr-btn cr-btn-secondary">Cancel</button>

<!-- Success -->
<button class="cr-btn cr-btn-success">Confirm</button>

<!-- Danger -->
<button class="cr-btn cr-btn-danger">Delete</button>

<!-- Ghost -->
<button class="cr-btn cr-btn-ghost">Learn More</button>

<!-- Icon Button -->
<button class="cr-btn cr-btn-icon">
  <svg>...</svg>
</button>
```

### States
- **Default**: Base styling
- **Hover**: Darker background, slight lift
- **Active**: Pressed appearance
- **Disabled**: Reduced opacity, no pointer
- **Loading**: Spinner icon, disabled state

### Specifications
- **Height**: 40px (default), 32px (small), 48px (large)
- **Padding**: 12px 24px (default)
- **Border Radius**: 6px
- **Font Weight**: 500
- **Transition**: 150ms ease

## 4.3 Card Component

### Structure
```html
<div class="cr-card">
  <div class="cr-card-header">
    <h3 class="cr-card-title">Title</h3>
    <div class="cr-card-actions">...</div>
  </div>
  <div class="cr-card-body">
    Content
  </div>
  <div class="cr-card-footer">
    Footer content
  </div>
</div>
```

### Specifications
- **Background**: White
- **Border**: 1px solid --cr-border
- **Border Radius**: 8px
- **Padding**: 24px
- **Shadow**: --cr-shadow-sm
- **Hover**: Slight shadow increase

## 4.4 Summary Card (Metric)

### Structure
```html
<div class="cr-metric-card">
  <div class="cr-metric-icon">🎯</div>
  <div class="cr-metric-content">
    <div class="cr-metric-label">Total Findings</div>
    <div class="cr-metric-value">12</div>
    <div class="cr-metric-change">+3 from last</div>
  </div>
</div>
```

### Specifications
- **Size**: 200px × 120px (desktop)
- **Layout**: Flexbox, icon + content
- **Icon Size**: 48px
- **Value Font**: 2xl, bold
- **Hover**: Subtle scale (1.02)

## 4.5 Table Component

### Structure
```html
<table class="cr-table">
  <thead>
    <tr>
      <th>Type</th>
      <th>Event</th>
      <th>Confidence</th>
      <th>Actions</th>
    </tr>
  </thead>
  <tbody>
    <tr>
      <td><span class="cr-badge cr-badge-success">Arbitrage</span></td>
      <td>Lakers vs Celtics</td>
      <td>95%</td>
      <td><button class="cr-btn-icon">...</button></td>
    </tr>
  </tbody>
</table>
```

### Specifications
- **Header**: Bold, background --cr-bg-secondary
- **Row Height**: 48px
- **Border**: Bottom border on rows
- **Hover**: Background highlight
- **Striped**: Optional alternating rows
- **Responsive**: Horizontal scroll on mobile

## 4.6 Badge Component

### Variants
```html
<span class="cr-badge cr-badge-success">Arbitrage</span>
<span class="cr-badge cr-badge-warning">Value Edge</span>
<span class="cr-badge cr-badge-danger">Outlier</span>
<span class="cr-badge cr-badge-info">Stale Line</span>
```

### Specifications
- **Height**: 24px
- **Padding**: 4px 12px
- **Border Radius**: 12px (pill shape)
- **Font Size**: 12px
- **Font Weight**: 500

## 4.7 Input Component

### Structure
```html
<div class="cr-input-group">
  <label class="cr-label">Label</label>
  <input type="text" class="cr-input" placeholder="Enter value">
  <span class="cr-input-help">Helper text</span>
</div>
```

### Specifications
- **Height**: 40px
- **Padding**: 8px 12px
- **Border**: 1px solid --cr-border
- **Border Radius**: 6px
- **Focus**: Blue border, shadow
- **Error**: Red border
- **Disabled**: Gray background

## 4.8 File Upload Component

### Structure
```html
<div class="cr-upload-zone">
  <div class="cr-upload-icon">📁</div>
  <div class="cr-upload-text">
    <p>Drag and drop JSON file here</p>
    <p class="cr-upload-subtext">or click to browse</p>
  </div>
  <input type="file" class="cr-upload-input" accept=".json">
</div>
```

### Specifications
- **Size**: Full width, 200px height
- **Border**: 2px dashed --cr-border
- **Border Radius**: 8px
- **Hover**: Border color change
- **Drag Over**: Background highlight
- **Icon Size**: 64px

## 4.9 Modal Component

### Structure
```html
<div class="cr-modal-overlay">
  <div class="cr-modal">
    <div class="cr-modal-header">
      <h2 class="cr-modal-title">Title</h2>
      <button class="cr-modal-close">×</button>
    </div>
    <div class="cr-modal-body">
      Content
    </div>
    <div class="cr-modal-footer">
      <button class="cr-btn cr-btn-secondary">Cancel</button>
      <button class="cr-btn cr-btn-primary">Confirm</button>
    </div>
  </div>
</div>
```

### Specifications
- **Overlay**: Semi-transparent black (rgba(0,0,0,0.5))
- **Modal Width**: 600px (max)
- **Modal Padding**: 24px
- **Animation**: Fade in + scale
- **Close**: Click overlay or X button
- **Focus Trap**: Tab cycles within modal

## 4.10 Toast Notification

### Structure
```html
<div class="cr-toast cr-toast-success">
  <div class="cr-toast-icon">✓</div>
  <div class="cr-toast-content">
    <div class="cr-toast-title">Success</div>
    <div class="cr-toast-message">Analysis completed</div>
  </div>
  <button class="cr-toast-close">×</button>
</div>
```

### Specifications
- **Position**: Top-right corner
- **Width**: 400px (max)
- **Duration**: 5 seconds (auto-dismiss)
- **Animation**: Slide in from right
- **Stack**: Multiple toasts stack vertically
- **Types**: Success, error, warning, info

## 4.11 Loading Spinner

### Structure
```html
<div class="cr-spinner">
  <div class="cr-spinner-circle"></div>
</div>
```

### Specifications
- **Size**: 40px (default), 24px (small), 64px (large)
- **Color**: Primary blue
- **Animation**: Smooth rotation
- **Inline**: Can be used in buttons

## 4.12 Chart Container

### Structure
```html
<div class="cr-chart-container">
  <div class="cr-chart-header">
    <h3 class="cr-chart-title">Findings by Type</h3>
    <div class="cr-chart-legend">...</div>
  </div>
  <div class="cr-chart-body">
    <canvas id="chart"></canvas>
  </div>
</div>
```

### Specifications
- **Aspect Ratio**: 16:9 (default)
- **Responsive**: Scales with container
- **Padding**: 16px
- **Background**: White
- **Border**: 1px solid --cr-border

---

# 5. USER FLOWS

## 5.1 Upload and Analyze Flow

1. **Landing**: User arrives at dashboard
2. **Upload**: User drags JSON file to upload zone
3. **Validation**: File is validated (visual feedback)
4. **Analysis**: User clicks "Analyze" button
5. **Loading**: Loading indicator appears
6. **Results**: Results display in summary cards
7. **Explore**: User explores findings in table
8. **Detail**: User clicks finding for detail view
9. **Chat**: User asks questions in chat panel

### Visual States
- **Empty State**: Upload prompt, sample data button
- **Uploading**: Progress indicator
- **Validating**: Validation spinner
- **Analyzing**: Full-screen loading overlay
- **Results**: Summary cards + findings table
- **Error**: Error message with retry option

## 5.2 Chat Interaction Flow

1. **Start**: User clicks chat icon
2. **Panel**: Chat panel slides in from right
3. **Quick Questions**: User sees suggested questions
4. **Ask**: User types or clicks question
5. **Loading**: Typing indicator appears
6. **Response**: Answer displays with sources
7. **Follow-up**: User asks follow-up questions
8. **Close**: User closes chat panel

---

# 6. INTERACTIONS

## 6.1 Hover States
- **Buttons**: Background darkens, slight lift (2px)
- **Cards**: Shadow increases
- **Table Rows**: Background highlight
- **Links**: Underline appears
- **Icons**: Color change

## 6.2 Focus States
- **Inputs**: Blue border, shadow
- **Buttons**: Blue outline (2px offset)
- **Links**: Blue outline
- **Cards**: Blue border

## 6.3 Active States
- **Buttons**: Pressed appearance (scale 0.98)
- **Links**: Color darkens
- **Tabs**: Underline indicator

## 6.4 Loading States
- **Buttons**: Spinner replaces text, disabled
- **Cards**: Skeleton loading animation
- **Tables**: Shimmer effect on rows
- **Charts**: Loading placeholder

## 6.5 Transitions
```css
/* Default transition */
transition: all 150ms ease;

/* Hover transitions */
transition: transform 200ms ease, box-shadow 200ms ease;

/* Modal animations */
animation: fadeIn 200ms ease;

/* Toast animations */
animation: slideInRight 300ms ease;
```

---

# 7. ACCESSIBILITY

## 7.1 WCAG 2.1 AA Compliance

### Color Contrast
- **Text**: Minimum 4.5:1 ratio
- **Large Text**: Minimum 3:1 ratio
- **UI Components**: Minimum 3:1 ratio

### Keyboard Navigation
- **Tab Order**: Logical flow
- **Focus Indicators**: Visible on all interactive elements
- **Skip Links**: Skip to main content
- **Keyboard Shortcuts**: Documented and accessible

### Screen Readers
- **ARIA Labels**: All interactive elements
- **ARIA Live Regions**: Dynamic content updates
- **Alt Text**: All images and icons
- **Semantic HTML**: Proper heading hierarchy

### Forms
- **Labels**: Associated with inputs
- **Error Messages**: Clear and descriptive
- **Required Fields**: Indicated visually and programmatically
- **Help Text**: Available for complex inputs

## 7.2 Accessibility Features
- **High Contrast Mode**: Support for OS high contrast
- **Reduced Motion**: Respect prefers-reduced-motion
- **Text Scaling**: Support up to 200% zoom
- **Touch Targets**: Minimum 44×44px

---

# 8. RESPONSIVE DESIGN

## 8.1 Mobile Optimizations

### Layout
- Single-column layout
- Stacked sections
- Full-width cards
- Collapsible panels

### Navigation
- Hamburger menu
- Bottom navigation bar (optional)
- Swipe gestures

### Tables
- Horizontal scroll
- Card view alternative
- Simplified columns

### Charts
- Responsive sizing
- Touch-friendly tooltips
- Simplified legends

### Forms
- Full-width inputs
- Larger touch targets
- Native mobile keyboards

## 8.2 Tablet Optimizations

### Layout
- Two-column layout
- Collapsible sidebars
- Adaptive cards

### Navigation
- Hybrid menu (icons + text)
- Persistent navigation

### Tables
- Scrollable with fixed headers
- Responsive columns

---

# 9. PERFORMANCE

## 9.1 Loading Strategy
- **Critical CSS**: Inline above-the-fold styles
- **Lazy Loading**: Images and charts below fold
- **Code Splitting**: Load modules on demand
- **Caching**: Service worker for static assets

## 9.2 Optimization Targets
- **First Contentful Paint**: < 1s
- **Time to Interactive**: < 2s
- **Largest Contentful Paint**: < 2.5s
- **Cumulative Layout Shift**: < 0.1
- **First Input Delay**: < 100ms

---

# 10. EMPTY STATES

## 10.1 No Data Uploaded
```
┌─────────────────────────────┐
│         📊                  │
│   No Data Loaded            │
│                             │
│   Upload a JSON file or     │
│   try our sample data       │
│                             │
│   [Upload File]             │
│   [Load Sample]             │
└─────────────────────────────┘
```

## 10.2 No Findings
```
┌─────────────────────────────┐
│         ✓                   │
│   Analysis Complete         │
│                             │
│   No opportunities found    │
│   in this dataset           │
│                             │
│   [Analyze New Data]        │
└─────────────────────────────┘
```

## 10.3 Error State
```
┌─────────────────────────────┐
│         ⚠️                  │
│   Analysis Failed           │
│                             │
│   Error: Invalid data       │
│   format                    │
│                             │
│   [Try Again] [Get Help]    │
└─────────────────────────────┘
```

---

# 11. MICRO-INTERACTIONS

## 11.1 Success Animations
- **Checkmark**: Animated checkmark on success
- **Confetti**: Subtle celebration for arbitrage found
- **Progress**: Smooth progress bar animations

## 11.2 Feedback Animations
- **Button Click**: Ripple effect
- **Card Hover**: Subtle lift
- **Toast**: Slide in from edge
- **Modal**: Fade + scale in

## 11.3 Loading Animations
- **Spinner**: Smooth rotation
- **Skeleton**: Shimmer effect
- **Progress**: Indeterminate bar
- **Pulse**: Breathing animation

---

**Document Version**: 1.0  
**Last Updated**: March 26, 2026  
**Maintained By**: AtOdds Design Team
