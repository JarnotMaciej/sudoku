# Design System Documentation
Inspired by Remarkable's minimalist and sophisticated design approach.

## Overview
This design system provides a comprehensive set of components, styles, and patterns that reflect the clean, minimalist aesthetic of Remarkable. It emphasizes readability, usability, and sophistication through careful use of typography, spacing, and interaction design.

## Getting Started

1. Link the CSS files in your HTML:
```html
<link rel="stylesheet" href="styles/components.css">
```

The components.css file automatically imports the design tokens.

## Design Tokens

### Colors
- `--color-primary-black`: #000000 - Primary text and key elements
- `--color-primary-white`: #FFFFFF - Background and contrast
- `--color-gray-100`: #F5F5F5 - Secondary backgrounds
- `--color-gray-200`: #E0E0E0 - Borders and dividers
- `--color-accent`: #1A73E8 - Call to actions and interactive elements

### Typography
```css
/* Font Family */
--font-family-primary: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, Helvetica, Arial, sans-serif;

/* Font Sizes */
--font-size-h1: 3rem      /* 48px */
--font-size-h2: 2.25rem   /* 36px */
--font-size-h3: 1.5rem    /* 24px */
--font-size-body: 1rem    /* 16px */
--font-size-small: 0.875rem /* 14px */
```

### Spacing
The spacing system uses a base unit of 8px:
- `--spacing-xs`: 0.5rem (8px)
- `--spacing-sm`: 1rem (16px)
- `--spacing-md`: 1.5rem (24px)
- `--spacing-lg`: 2rem (32px)
- `--spacing-xl`: 3rem (48px)
- `--spacing-xxl`: 4rem (64px)

## Components

### Buttons
Three button variants are available:

1. Primary Button
```html
<a href="#" class="button button--primary">Primary Button</a>
```

2. Secondary Button
```html
<a href="#" class="button button--secondary">Secondary Button</a>
```

3. Text Button
```html
<a href="#" class="button button--text">Text Button</a>
```

### Cards
Cards provide a container for related content:
```html
<div class="card">
    <h3>Card Title</h3>
    <p>Card content</p>
    <a href="#" class="button button--primary">Call to Action</a>
</div>
```

### Grid System
The grid system uses CSS Grid with 12 columns by default:
```html
<div class="container">
    <div class="grid">
        <!-- Grid content -->
    </div>
</div>
```

## Responsive Design

The system includes breakpoints for different screen sizes:
- Desktop: 1024px and above
- Tablet: 768px to 1023px
- Mobile: Below 768px

The grid system and typography automatically adjust for different screen sizes.

## Best Practices

1. Typography
- Use heading levels (h1, h2, h3) semantically
- Maintain proper hierarchy in content
- Keep line lengths comfortable for reading (around 60-75 characters)

2. Spacing
- Use the provided spacing variables consistently
- Maintain rhythm in layouts using the spacing scale
- Add proper whitespace around content sections

3. Colors
- Use the primary black for main content
- Apply accent colors sparingly for emphasis
- Maintain sufficient contrast for accessibility

4. Components
- Keep card content concise and focused
- Use appropriate button styles based on action importance
- Follow grid system for consistent layouts

## Browser Support
The design system supports modern browsers including:
- Chrome (latest)
- Firefox (latest)
- Safari (latest)
- Edge (latest)

## Demo
View index.html for a complete demonstration of all components and styles.
