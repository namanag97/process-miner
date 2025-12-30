# AI Coder Guide: How to Build Features

> This guide explains how to use the design system documents when implementing features.

---

## Quick Reference: Document Purposes

| Document | What It Contains | When to Reference |
|----------|------------------|-------------------|
| **DESIGN_SYSTEM.md** | Principles, tokens, component specs | Always — for visual implementation |
| **PATTERNS_AND_RECIPES.md** | Layouts, compositions, interaction patterns | When building pages or complex features |
| **INFORMATION_ARCHITECTURE.md** | Routes, page structure, navigation | When creating new pages or routes |
| **FEATURE_MANIFEST.md** | Feature specs, dependencies, status | Before starting any feature |

---

## Before You Start Coding

### Step 1: Check the Feature Manifest
1. Find the feature in `FEATURE_MANIFEST.md`
2. Verify it's in the current phase
3. Check all dependencies are complete
4. Read the acceptance criteria
5. Note which SDK methods are needed

### Step 2: Review Relevant Patterns
1. Identify the layout pattern (from feature spec)
2. Find that pattern in `PATTERNS_AND_RECIPES.md`
3. Note the composition and spacing

### Step 3: Identify Components Needed
1. List components from feature spec
2. Find each component spec in `DESIGN_SYSTEM.md`
3. Note all states to implement

---

## Implementation Checklist

For every component/page you build:

### Visual Consistency
- [ ] Colors use semantic tokens (e.g., `action-primary` not `#2563EB`)
- [ ] Spacing uses scale values (e.g., `space-4` not `15px`)
- [ ] Typography uses defined styles (e.g., `text-lg` not `font-size: 17px`)
- [ ] Border radius uses tokens (e.g., `radius-md` not `5px`)
- [ ] Shadows use tokens (e.g., `shadow-sm` not custom box-shadow)

### State Coverage
- [ ] Default state
- [ ] Hover state (where applicable)
- [ ] Active/pressed state
- [ ] Focus state (for interactive elements)
- [ ] Disabled state (where applicable)
- [ ] Loading state (for async operations)
- [ ] Error state (for things that can fail)
- [ ] Empty state (for data-driven components)

### Accessibility
- [ ] Focus indicators visible
- [ ] Keyboard navigation works
- [ ] Color contrast meets 4.5:1 minimum
- [ ] Interactive elements have appropriate roles
- [ ] Loading states announced to screen readers

### Responsiveness
- [ ] Works at desktop (1280px+)
- [ ] Works at tablet (768px-1279px)
- [ ] Works at mobile (<768px)

---

## How to Read Component Specs

### Example: Button Component

From `DESIGN_SYSTEM.md`:

```
#### Sizes
| Size | Height | Padding X | Font Size | Icon Size |
|------|--------|-----------|-----------|-----------|
| **sm** | 32px | 12px | 13px | 16px |
| **md** (default) | 36px | 16px | 14px | 18px |
| **lg** | 40px | 20px | 15px | 20px |
```

**This means:**
- There are 3 size variants
- Default is `md` if not specified
- Use these exact values for consistency

### Example: State Matrix

```
| State | Background | Text | Border |
|-------|------------|------|--------|
| **Default** | transparent | neutral-600 | none |
| **Hover** | neutral-200 | neutral-800 | none |
| **Active** | primary-100 | primary-700 | left-3px primary-500 |
```

**This means:**
- Implement ALL these states
- Use these exact token values
- The Active state has a special left border

---

## How to Read Layout Patterns

### Example: Settings Page Pattern

From `PATTERNS_AND_RECIPES.md`:

```
┌─────────────────────────────────────────────────────────┐
│ [Sidebar]│ Page Header                                  │
│          │ ┌─────────────────────────────────────────┐ │
│          │ │ Section 1 Title                         │ │
│          │ │ Description text                        │ │
│          │ │ ┌─────────────────────────────────────┐ │ │
│          │ │ │ Form Fields                         │ │ │
│          │ │ └─────────────────────────────────────┘ │ │
│          │ │              [Cancel] [Save]            │ │
│          │ └─────────────────────────────────────────┘ │
└─────────────────────────────────────────────────────────┘
```

**This tells you:**
- Use Card component for sections
- Each section has its own Save/Cancel
- Max-width: 720px for the content
- Vertical gap: 24px between sections

---

## Common Patterns

### Data Loading Pattern

Always implement this state machine for data-driven views:

```javascript
// States to handle:
// 1. LOADING - show skeleton
// 2. ERROR - show error state with retry
// 3. EMPTY - show empty state component
// 4. SUCCESS - render data
// 5. REFRESHING - show data + loading indicator

const MyComponent = () => {
  if (loading && !data) return <Skeleton />
  if (error) return <ErrorState onRetry={refetch} />
  if (!data || data.length === 0) return <EmptyState />
  
  return (
    <div>
      {refreshing && <LoadingIndicator />}
      {/* render data */}
    </div>
  )
}
```

### Form Pattern

```javascript
// States to handle:
// 1. PRISTINE - Save disabled
// 2. DIRTY - Save enabled, show unsaved indicator
// 3. SUBMITTING - Form disabled, spinner on Save
// 4. SUCCESS - Toast, reset to pristine
// 5. ERROR - Show error, re-enable form

const MyForm = () => {
  const [isDirty, setIsDirty] = useState(false)
  const [isSubmitting, setIsSubmitting] = useState(false)
  
  return (
    <form>
      {/* inputs */}
      <Button 
        disabled={!isDirty || isSubmitting}
        loading={isSubmitting}
      >
        Save
      </Button>
    </form>
  )
}
```

### Toast Usage

```javascript
// Use for action feedback:
toast.success('Settings saved')
toast.error('Failed to save. Please try again.')
toast.info('Processing your file...')
toast.warning('This action cannot be undone')
```

---

## File Structure Convention

```
src/
├── components/
│   ├── ui/                    # Design system components
│   │   ├── Button/
│   │   │   ├── Button.tsx
│   │   │   ├── Button.styles.ts
│   │   │   └── index.ts
│   │   ├── Input/
│   │   ├── Card/
│   │   └── ...
│   │
│   ├── layout/                # Layout components
│   │   ├── AppShell/
│   │   ├── Sidebar/
│   │   ├── PageHeader/
│   │   └── ...
│   │
│   └── features/              # Feature-specific components
│       ├── settings/
│       ├── notifications/
│       ├── logs/
│       └── ...
│
├── pages/                     # Page components (routes)
│   ├── Home.tsx
│   ├── settings/
│   │   ├── Profile.tsx
│   │   ├── Preferences.tsx
│   │   └── Notifications.tsx
│   ├── logs/
│   └── ...
│
├── hooks/                     # Custom hooks
├── utils/                     # Utility functions
├── services/                  # API/SDK integration
└── styles/
    └── tokens.css            # Design tokens as CSS variables
```

---

## Naming Conventions

### Components
- PascalCase: `Button`, `PageHeader`, `NotificationList`
- Descriptive: `UserProfileForm` not `Form1`

### CSS Classes (if using Tailwind or similar)
- Follow design token names where possible
- Use semantic names: `text-primary` not `text-gray-800`

### Props
- Boolean: `isLoading`, `isDisabled`, `hasError`
- Handlers: `onSubmit`, `onClick`, `onChange`
- Variants: `variant="primary"`, `size="md"`

---

## Quality Checklist

Before submitting any feature:

### Functionality
- [ ] All acceptance criteria met
- [ ] Works with mock data
- [ ] Error states handled
- [ ] Loading states implemented

### Design System Compliance
- [ ] Uses correct tokens (no magic numbers)
- [ ] All component states implemented
- [ ] Follows specified layout pattern
- [ ] Typography hierarchy correct

### Code Quality
- [ ] Components are reusable
- [ ] No hardcoded values
- [ ] Props are typed
- [ ] Code is readable

### Testing (if applicable)
- [ ] Key interactions work
- [ ] Edge cases handled
- [ ] Responsive at all breakpoints

---

## When Specs Are Unclear

If you encounter ambiguity:

1. **Check the Principles** (DESIGN_SYSTEM.md Section 1)
   - Principles guide judgment calls
   
2. **Look for Similar Patterns**
   - Find similar component/page in the docs
   - Follow established patterns

3. **Default Conservative**
   - Simpler is better
   - Follow existing patterns over innovation
   
4. **Note the Ambiguity**
   - Add a comment: `// TODO: Clarify spec for X`
   - Flag in PR for review

---

## Example: Building Settings Profile Page

### Step 1: Check Feature Manifest
Feature: **F1.2: Settings - Profile**
- Status: Not Started
- Dependencies: F0.1 (App Shell), F1.6 (Toast)
- Components: Page Header, Tabs, Card, Input, Avatar, Button

### Step 2: Check Layout Pattern
Pattern: **Settings Page (1.6)** from PATTERNS_AND_RECIPES.md
- Max-width: 720px
- Sections as cards
- Independent save per section

### Step 3: Check Component Specs
From DESIGN_SYSTEM.md:
- **Input**: Height 36px, padding 12px/8px, border-radius 6px
- **Button**: Primary variant for Save, Secondary for Cancel
- **Card**: padding 16px, border-radius 8px

### Step 4: Implement

```tsx
// pages/settings/Profile.tsx

const ProfileSettings = () => {
  const { toast } = useToast()
  const [formState, setFormState] = useState({...})
  
  return (
    <div className="max-w-[720px]">
      <PageHeader title="Settings" />
      
      <SettingsTabs activeTab="profile" />
      
      <Card className="mt-6">
        <CardHeader>
          <CardTitle>Profile Information</CardTitle>
        </CardHeader>
        <CardContent>
          <AvatarUpload 
            src={formState.avatar}
            onChange={handleAvatarChange}
          />
          
          <Input
            label="Full Name"
            value={formState.name}
            onChange={handleNameChange}
          />
          
          <Input
            label="Email"
            value={formState.email}
            disabled
            helperText="Email cannot be changed"
          />
        </CardContent>
        <CardFooter className="flex justify-end gap-2">
          <Button variant="secondary" onClick={handleCancel}>
            Cancel
          </Button>
          <Button 
            variant="primary" 
            onClick={handleSave}
            disabled={!isDirty}
            loading={isSubmitting}
          >
            Save Changes
          </Button>
        </CardFooter>
      </Card>
    </div>
  )
}
```

---

## Summary

1. **Always check Feature Manifest first** — know what you're building
2. **Follow the layout patterns** — consistency matters
3. **Use design tokens** — no magic numbers
4. **Implement all states** — loading, error, empty
5. **Follow naming conventions** — predictable code
6. **When unclear, check principles** — they guide decisions

---

*End of AI Coder Guide*
