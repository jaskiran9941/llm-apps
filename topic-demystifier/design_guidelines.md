# Design Guidelines: Educational Explanation App

## Design Approach

**Reference-Based Strategy**: Drawing inspiration from educational platforms (Khan Academy's clarity), creative tools (Canva's playfulness), and content platforms (Medium's reading experience). The design prioritizes visual engagement and learning-friendly interfaces.

**Core Principles**:
- Playful yet clear: Fun without sacrificing comprehension
- Visual-first: Images and illustrations drive the experience
- Progressive disclosure: Simple input, rich output
- Frictionless learning: Minimal cognitive load

## Typography System

**Font Families**:
- Primary: 'Nunito' (Google Fonts) - Rounded, friendly headers
- Secondary: 'Inter' (Google Fonts) - Clean, readable body text

**Hierarchy**:
- Hero Headlines: text-5xl md:text-6xl lg:text-7xl, font-bold
- Section Titles: text-3xl md:text-4xl, font-bold
- Subsections: text-xl md:text-2xl, font-semibold
- Body Text: text-base md:text-lg, font-normal, leading-relaxed
- Captions: text-sm, font-medium

## Layout System

**Spacing Primitives**: Use Tailwind units of 3, 4, 6, 8, 12, 16, 20
- Consistent padding: p-6, p-8, p-12
- Section spacing: py-12, py-16, py-20
- Component gaps: gap-4, gap-6, gap-8

**Container Strategy**:
- Input section: max-w-3xl mx-auto
- Output displays: max-w-6xl mx-auto
- Comic panels: max-w-5xl mx-auto

## Component Library

### Hero Section
- Full-width hero (min-h-[70vh])
- Centered content with illustration/animation in background
- Large headline emphasizing "Explain Anything Simply"
- Prominent text input area (direct access to core functionality)
- Alternative: Upload image button with icon
- Trust indicator: "Powered by AI" with subtle badge

### Input Interface
**Dual Input Mode**:
- Tab switcher: "Text" and "Image" modes
- Text area: Large (min-h-[120px]), rounded-2xl, with placeholder "Enter any complex topic..."
- Image upload: Drag-and-drop zone with preview, rounded-2xl border-dashed
- Submit button: Large (px-8 py-4), rounded-full, with arrow icon
- Character count for text (subtle, bottom-right)

### Output Display Sections

**Comic Strip View**:
- Horizontal scrollable container with snap-scroll
- Individual panels: aspect-square or aspect-[4/3], rounded-xl, shadow-lg
- Panel layout: grid-cols-1 md:grid-cols-2 lg:grid-cols-3 with gap-6
- Speech bubbles: Absolute positioned with tail, rounded-2xl
- Panel borders: 4px solid with playful aesthetic
- Navigation: Dots indicator below, prev/next arrows

**Illustration Gallery**:
- Masonry-style grid (using grid or flexbox)
- Cards: rounded-xl, shadow-md, hover:shadow-xl transition
- Image aspect ratios: Mixed (square, portrait, landscape)
- Captions: Below each image, text-sm, text-center

**Slideshow Presentation**:
- Full-width viewer with dark/neutral container
- Slide content: Centered, max-w-4xl
- Large images (h-[400px] md:h-[500px])
- Narration text: Below image, text-lg, leading-relaxed, max-w-2xl mx-auto
- Controls: Bottom bar with play/pause, progress bar, slide counter
- Audio indicator: Waveform animation during playback
- Navigation: Keyboard arrows + on-screen buttons

### Navigation
- Top nav: Sticky, backdrop-blur, shadow-sm
- Logo/Brand: Left-aligned, medium size
- Actions: Right-aligned - "New Explanation" button
- Mobile: Hamburger menu (if needed for future features)

### Card Components
- Rounded corners: rounded-xl or rounded-2xl
- Shadows: shadow-md for elevation, shadow-lg for emphasis
- Padding: p-6 or p-8
- Hover states: transform scale-105, shadow-xl

## Iconography
**Icons via Heroicons CDN** (outline style)
- Input: DocumentTextIcon, PhotoIcon
- Navigation: ChevronLeft, ChevronRight, ArrowRight
- Controls: PlayIcon, PauseIcon, SpeakerWaveIcon
- Features: SparklesIcon, AcademicCapIcon, LightBulbIcon

## Images

**Hero Section**:
- Large hero image: Colorful illustration showing diverse topics being explained (books, science beakers, gears, lightbulbs) in a whimsical style
- Placement: Background with overlay, or split-screen layout (text left, illustration right)
- Style: Flat design illustration, friendly and approachable

**Feature Demonstrations**:
- Screenshot/mockup of comic strip output
- Example illustration grid showing variety
- Slideshow interface preview
- Placement: Throughout landing sections to demonstrate capabilities

**Empty States**:
- Friendly illustrations for "waiting for input" state
- Cute mascot or character suggesting topics to try

## Animation Strategy

**Minimal, Purposeful Animations**:
- Input focus: Subtle scale and glow effect
- Card hover: scale-105 transform
- Slideshow transitions: Fade or slide (duration-300)
- Loading states: Gentle pulse or spinner
- Comic panel reveal: Stagger fade-in (avoid overwhelming)

**Avoid**: Parallax, continuous background animations, excessive motion

## Responsive Behavior

**Breakpoints**:
- Mobile (base): Single column, stacked layout
- Tablet (md): 2-column grids where appropriate
- Desktop (lg): Full multi-column layouts, wider containers

**Key Adaptations**:
- Input section: Full width on mobile, centered card on desktop
- Comic panels: 1 column mobile → 2-3 columns desktop
- Slideshow: Adjust image height, larger touch targets on mobile
- Typography: Scale down 1-2 sizes on mobile

## Accessibility Standards

- Focus indicators: 2px ring offset on all interactive elements
- Form labels: Visible and associated with inputs
- Alt text: Required for all generated images
- Keyboard navigation: Full support for slideshow controls
- Color contrast: Ensure text meets WCAG AA standards
- Screen reader: ARIA labels for custom controls

## User Flow Considerations

1. **Landing**: Immediate access to input (no barriers)
2. **Input**: Clear, inviting interface with examples
3. **Processing**: Loading state with encouraging message
4. **Results**: Tabbed or sectioned output (Comic, Illustrations, Slideshow)
5. **Exploration**: Easy navigation between output types
6. **Iteration**: Quick access to create new explanation

This educational app should feel like a delightful learning companion—visually engaging, easy to use, and focused on making complex topics accessible through beautiful, AI-generated content.