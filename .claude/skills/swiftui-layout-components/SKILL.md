---
model: sonnet
name: swiftui-layout-components
description: "Build SwiftUI layouts and components: stacks, grids, lists, scroll views, forms, controls, search UI with .searchable, overlays, and adaptive containers. Covers ViewThatFits, Layout protocol, custom containers, iOS 26 Liquid Glass containers, and common layout pitfalls. Use when building list-based UIs, grid layouts, forms, custom scroll behaviour, or adaptive multi-platform layouts."
---

# SwiftUI Layout and Components

Layout patterns and reusable component patterns for SwiftUI targeting iOS 26+ with Swift 6.3. Architecture and state patterns live in `swiftui-patterns`; navigation patterns live in `swiftui-navigation`.

## Contents

- [Stack Fundamentals](#stack-fundamentals)
- [Lists and ForEach](#lists-and-foreach)
- [LazyVGrid / LazyHGrid](#lazyvgrid--lazyhgrid)
- [ScrollView Patterns](#scrollview-patterns)
- [Forms and Controls](#forms-and-controls)
- [Search with .searchable](#search-with-searchable)
- [Overlays and Presentations](#overlays-and-presentations)
- [Adaptive Layouts (ViewThatFits, Layout Protocol)](#adaptive-layouts)
- [iOS 26 Container Patterns](#ios-26-container-patterns)
- [Common Mistakes](#common-mistakes)
- [Review Checklist](#review-checklist)

---

## Stack Fundamentals

Prefer `VStack`/`HStack`/`ZStack` for simple fixed layouts. Use `LazyVStack`/`LazyHStack` only inside `ScrollView` where lazy loading is needed — lazy stacks inside non-scrolling containers waste the lazy infrastructure.

```swift
// Fixed layout — use VStack
VStack(alignment: .leading, spacing: 12) {
    Text(title).font(.headline)
    Text(subtitle).font(.subheadline).foregroundStyle(.secondary)
}

// Scrollable list of variable-height items — use LazyVStack inside ScrollView
ScrollView {
    LazyVStack(spacing: 0, pinnedViews: [.sectionHeaders]) {
        ForEach(sections) { section in
            Section {
                ForEach(section.items) { item in
                    ItemRow(item: item)
                }
            } header: {
                SectionHeader(title: section.title)
            }
        }
    }
}
```

**Spacing:** Always use `spacing:` on the container rather than padding on individual items — it is more predictable and composable.

---

## Lists and ForEach

Use `List` for system-styled, swipe-action, and inset-grouped content. Use `LazyVStack` in a `ScrollView` for fully custom layouts.

```swift
// Standard List with swipe actions
List {
    ForEach(items) { item in
        ItemRow(item: item)
            .swipeActions(edge: .trailing) {
                Button(role: .destructive) {
                    delete(item)
                } label: {
                    Label("Delete", systemImage: "trash")
                }
            }
    }
    .onDelete(perform: deleteItems)
    .onMove(perform: moveItems)
}
.listStyle(.insetGrouped)

// Empty state
.overlay {
    if items.isEmpty {
        ContentUnavailableView(
            "No Items",
            systemImage: "tray",
            description: Text("Add your first item to get started.")
        )
    }
}
```

**`ForEach` identity:** always use a stable `id` from the data model. Never use `\.self` on mutable objects or complex value types — it produces identity churn and broken animations.

```swift
// Correct — stable ID from model
ForEach(items, id: \.id) { item in ... }

// Correct — Identifiable conformance
ForEach(items) { item in ... }

// Avoid — unstable identity
ForEach(items, id: \.self) { item in ... }  // only safe for strings/ints with no duplicates
```

---

## LazyVGrid / LazyHGrid

```swift
// Adaptive grid — fills columns based on available width
let columns = [GridItem(.adaptive(minimum: 160, maximum: 200))]

ScrollView {
    LazyVGrid(columns: columns, spacing: 16) {
        ForEach(items) { item in
            ItemCard(item: item)
        }
    }
    .padding()
}

// Fixed 2-column grid
let twoColumn = [GridItem(.flexible()), GridItem(.flexible())]
```

**When to use:** image galleries, card grids, icon grids. Avoid for list-style content where rows have natural leading-edge alignment — `List` or `LazyVStack` is clearer.

---

## ScrollView Patterns

```swift
// Pull-to-refresh
ScrollView {
    LazyVStack { ... }
}
.refreshable {
    await viewModel.refresh()
}

// Scroll position tracking (iOS 17+)
@State private var scrollPosition: Int?

ScrollView {
    LazyVStack {
        ForEach(items) { item in
            ItemRow(item: item)
                .id(item.id)
        }
    }
    .scrollTargetLayout()
}
.scrollPosition(id: $scrollPosition)

// Scroll-to on programmatic trigger
.onChange(of: targetID) { _, newID in
    withAnimation {
        scrollPosition = newID
    }
}
```

**Safe area:** content in a `ScrollView` should extend under the home indicator using `.safeAreaInset(edge: .bottom)` for sticky footers, not by adding bottom padding to the scroll content.

```swift
ScrollView {
    LazyVStack { ... }
}
.safeAreaInset(edge: .bottom) {
    StickyFooterView()
}
```

---

## Forms and Controls

```swift
Form {
    Section("Account") {
        LabeledContent("Email", value: user.email)

        TextField("Name", text: $name)
            .textContentType(.name)

        Toggle("Notifications", isOn: $notificationsEnabled)
    }

    Section("Danger Zone") {
        Button("Delete Account", role: .destructive) {
            showDeleteConfirmation = true
        }
    }
}
.formStyle(.grouped)
```

**Picker styles:**
- `.segmented` — 2–4 short options, always visible
- `.menu` — many options or long labels
- `.navigationLink` (inside `NavigationStack`) — complex multi-select or sub-page pickers

```swift
Picker("Theme", selection: $theme) {
    ForEach(Theme.allCases) { t in
        Text(t.label).tag(t)
    }
}
.pickerStyle(.menu)
```

---

## Search with .searchable

```swift
struct ItemListView: View {
    @State private var query = ""

    var filtered: [Item] {
        query.isEmpty ? items : items.filter {
            $0.name.localizedCaseInsensitiveContains(query)
        }
    }

    var body: some View {
        List(filtered) { item in
            ItemRow(item: item)
        }
        .searchable(text: $query, prompt: "Search items")
        .searchSuggestions {
            if query.isEmpty {
                ForEach(recentSearches) { s in
                    Label(s.term, systemImage: "clock")
                        .searchCompletion(s.term)
                }
            }
        }
    }
}
```

**Placement:** `.searchable` must be applied to a view inside a `NavigationStack` or `NavigationSplitView` for the search bar to appear in the navigation bar. Applied outside a navigation container, it renders inline.

---

## Overlays and Presentations

```swift
// Contextual overlay (not a sheet — stays in place)
.overlay(alignment: .bottom) {
    if showBanner {
        BannerView(message: bannerMessage)
            .transition(.move(edge: .bottom).combined(with: .opacity))
            .animation(.spring, value: showBanner)
    }
}

// Popover (iPad full-size; falls back to sheet on iPhone)
.popover(isPresented: $showPopover) {
    PopoverContent()
        .presentationCompactAdaptation(.sheet)  // iOS 16.4+
}

// Context menu
.contextMenu {
    Button("Copy", systemImage: "doc.on.doc") { copy(item) }
    Button("Share", systemImage: "square.and.arrow.up") { share(item) }
    Divider()
    Button("Delete", systemImage: "trash", role: .destructive) { delete(item) }
}
```

---

## Adaptive Layouts

### ViewThatFits

Use `ViewThatFits` to pick a layout that fits the available space without geometry readers.

```swift
ViewThatFits(in: .horizontal) {
    // Preferred: full horizontal layout
    HStack {
        PrimaryAction()
        SecondaryAction()
        TertiaryAction()
    }
    // Fallback: compact vertical layout
    VStack {
        PrimaryAction()
        HStack { SecondaryAction(); TertiaryAction() }
    }
    // Last resort: single column
    VStack {
        PrimaryAction()
        SecondaryAction()
        TertiaryAction()
    }
}
```

### Layout Protocol (custom layout)

Use when `Spacer`, `alignment`, and stacks cannot express the layout.

```swift
struct FlowLayout: Layout {
    var spacing: CGFloat = 8

    func sizeThatFits(proposal: ProposedViewSize, subviews: Subviews, cache: inout ()) -> CGSize {
        let width = proposal.width ?? .infinity
        var currentX: CGFloat = 0
        var currentY: CGFloat = 0
        var rowHeight: CGFloat = 0
        var maxX: CGFloat = 0

        for subview in subviews {
            let size = subview.sizeThatFits(.unspecified)
            if currentX + size.width > width, currentX > 0 {
                currentY += rowHeight + spacing
                currentX = 0
                rowHeight = 0
            }
            currentX += size.width + spacing
            rowHeight = max(rowHeight, size.height)
            maxX = max(maxX, currentX)
        }
        return CGSize(width: maxX, height: currentY + rowHeight)
    }

    func placeSubviews(in bounds: CGRect, proposal: ProposedViewSize, subviews: Subviews, cache: inout ()) {
        var currentX = bounds.minX
        var currentY = bounds.minY
        var rowHeight: CGFloat = 0

        for subview in subviews {
            let size = subview.sizeThatFits(.unspecified)
            if currentX + size.width > bounds.maxX, currentX > bounds.minX {
                currentY += rowHeight + spacing
                currentX = bounds.minX
                rowHeight = 0
            }
            subview.place(at: CGPoint(x: currentX, y: currentY), proposal: ProposedViewSize(size))
            currentX += size.width + spacing
            rowHeight = max(rowHeight, size.height)
        }
    }
}

// Usage
FlowLayout(spacing: 8) {
    ForEach(tags) { tag in TagChip(tag: tag) }
}
```

---

## iOS 26 Container Patterns

**Glass containers:** do not add `.background(.regularMaterial)` to `TabView`, toolbar containers, or sidebar `NavigationSplitView` columns — they use Liquid Glass automatically. Custom material on top creates double-blur artifacts.

**Floating panels (iOS 26):** use `.presentationDetents` with `.fraction` for bottom sheets that coexist with the map or content behind.

```swift
.sheet(isPresented: $showPanel) {
    PanelContent()
        .presentationDetents([.fraction(0.4), .large])
        .presentationDragIndicator(.visible)
        .presentationBackgroundInteraction(.enabled(upThrough: .fraction(0.4)))
}
```

---

## Common Mistakes

| Mistake | Impact | Fix |
|---|---|---|
| `LazyVStack` outside `ScrollView` | No lazy loading benefit, all subviews created | Use `VStack` or wrap in `ScrollView` |
| `GeometryReader` for single-axis sizing | Layout thrash, unexpected frame | Use `.frame(maxWidth: .infinity)` or `ViewThatFits` |
| Hard-coded `frame(height: 44)` on list rows | Breaks Dynamic Type | Use `padding(.vertical, 10)` and let content size the row |
| `.padding()` on `ScrollView` content instead of `.contentMargins` | Clips pull-to-refresh indicator | Use `.contentMargins(.horizontal, 16)` (iOS 17+) |
| Nested `ScrollView` same axis | Swipe gesture conflicts | Redesign to a single scrolling container |
| `List` inside a `ScrollView` | List's own scroll geometry conflicts | Use `LazyVStack` instead of `List` inside `ScrollView` |

---

## Review Checklist

- [ ] Lists with possible empty state show `ContentUnavailableView`
- [ ] `ForEach` uses stable, unique IDs
- [ ] `LazyVStack`/`LazyHGrid` is inside a `ScrollView`
- [ ] No hard-coded heights on variable-content views
- [ ] `.searchable` is inside a navigation container
- [ ] Sticky footers use `.safeAreaInset` not bottom padding on scroll content
- [ ] Custom glass containers don't double-apply material backgrounds

---

## References

- [SwiftUI Layout Fundamentals — WWDC 2022](https://developer.apple.com/videos/play/wwdc2022/10056/)
- [Compose custom layouts with SwiftUI — WWDC 2022](https://developer.apple.com/videos/play/wwdc2022/10056/)
- [What's new in SwiftUI — WWDC 2024](https://developer.apple.com/videos/play/wwdc2024/10144/)
