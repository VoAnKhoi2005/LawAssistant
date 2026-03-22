# Design System Strategy: The Intellectual Architect

## 1. Overview & Creative North Star
The "Creative North Star" for this design system is **The Intellectual Architect**. In the legal and knowledge management space, users aren't just looking for data; they are seeking clarity within complexity. This system moves away from the "cluttered spreadsheet" aesthetic toward a high-end, editorial experience that feels as authoritative as a leather-bound brief and as modern as a high-court glass atrium.

We break the "template" look by rejecting rigid borders and standard grids. Instead, we use **Intentional Asymmetry**—where metadata sidebars are offset and primary content areas use generous, breathing white space. By overlapping "glass" layers and using high-contrast typography scales (Manrope for structure, Inter for data), we create a sense of deep organizational thought rather than mere data entry.

---

## 2. Colors & Surface Philosophy
The palette is rooted in deep structural blues (`primary: #525f71`) and charcoal neutrals (`on_surface: #31323a`), providing a sober, trustworthy foundation.

*   **The "No-Line" Rule:** 1px solid borders are strictly prohibited for sectioning. Structural boundaries must be defined solely by background color shifts. For example, a navigation sidebar should use `surface_container_low`, while the main workspace sits on `surface`.
*   **Surface Hierarchy & Nesting:** Treat the UI as stacked sheets of fine paper. 
    *   **Level 0:** `surface` (The base desk).
    *   **Level 1:** `surface_container_low` (Large structural regions).
    *   **Level 2:** `surface_container` (Content cards or data clusters).
    *   **Level 3:** `surface_container_highest` (Active selection or focused metadata).
*   **The Glass & Gradient Rule:** For floating elements like "Quick Action" menus or "Graph Overlays," use a Glassmorphism effect: `surface_container_lowest` at 80% opacity with a `24px` backdrop blur. Main CTAs should utilize a subtle linear gradient from `primary` to `primary_dim` to create a "machined" satin finish.

---

## 3. Typography
The typography strategy pairings reflect a "Courtroom Authority meets Modern Tech" vibe.

*   **Display & Headlines (Manrope):** We use Manrope for all headers (`display-lg` to `headline-sm`). Its geometric yet approachable curves provide a modern architectural feel. Use `headline-md` (1.75rem) for case titles to command attention.
*   **Body & Labels (Inter):** Inter is our workhorse for high-density legal text. 
    *   **Legal Text:** Use `body-md` (0.875rem) for standard document reading.
    *   **Data Labels:** Use `label-md` (0.75rem) with `on_surface_variant` for metadata labels to ensure they are distinct from the primary content.
*   **Hierarchy through Scale:** Create drama by pairing a `display-sm` title with a `label-sm` metadata tag. This high-contrast scale ratio (3:1 or higher) signals editorial intent.

---

## 4. Elevation & Depth
We reject the "drop shadow" of 2010. Depth is now atmospheric.

*   **Tonal Layering:** Instead of shadows, use `surface_container_low` (0.9rem padding) to wrap a `surface_container_lowest` card. The subtle shift from a cool grey-white to a pure white creates a "soft lift."
*   **Ambient Shadows:** If a metadata sidebar must float, use a shadow with a 40px blur and 4% opacity, tinted with `primary_dim`. It should look like a soft glow, not a dark edge.
*   **The Ghost Border Fallback:** For complex data tables where cells must be distinct, use a "Ghost Border": `outline_variant` at 15% opacity. It provides a subconscious guide without cluttering the visual field.

---

## 5. Components & Data Structures

### Data Tables (The "Legal Ledger")
*   **No Dividers:** Rows are separated by `spacing-4` vertical space. 
*   **Hover State:** On hover, a row should transition to `surface_container_high` with a `lg` (0.5rem) corner radius.
*   **Header:** Table headers must use `label-md` in all-caps with `0.05em` letter spacing for an authoritative "Archive" look.

### Tree Views (Knowledge Hierarchy)
*   **Indentation:** Use `spacing-4` for each nesting level.
*   **Active State:** The selected node uses `secondary_container` background with `on_secondary_container` text. 
*   **Connecting Lines:** Never use solid lines. Use a `1px` dotted line with `outline_variant` at 20% opacity.

### Graph Visualization Containers
*   **The "Atrium" Effect:** Graph containers must use `surface_container_lowest` with a subtle `primary_container` inner glow. 
*   **Nodes:** Use `primary` for standard nodes and `tertiary` (#7a5a00) for "Flagged" or "Critical" nodes.

### Metadata Sidebars
*   **Asymmetric Layout:** These should be fixed to the right, using `surface_container_low`. 
*   **Input Fields:** Use "Underline Only" inputs for a cleaner editorial look. The active state should transform the underline into a `2px` `primary` bar.

---

## 6. Do’s and Don’ts

### Do:
*   **Use the Spacing Scale religiously.** `spacing-8` (1.75rem) should be your default "gutter" between major sections to maintain an "organized" feel.
*   **Layer your surfaces.** Use `surface_container` for a card and `surface_container_highest` for a button inside that card.
*   **Embrace white space.** A legal document is easier to read when it isn't "boxed in."

### Don’t:
*   **Don't use 100% black.** Always use `on_background` or `on_surface` for text to maintain the "charcoal" professional tone.
*   **Don't use standard "Alert Red."** Use the curated `error` (#9e3f4e) which is a sophisticated burgundy, fitting for a professional environment.
*   **Don't use sharp corners.** Stick to the `md` (0.375rem) roundedness for most components; it feels modern yet structured. Only use `none` for top-level layout containers.

---

## 7. Interaction Design
*   **The "Ink Flow" Transition:** When a user expands a tree view or a data row, use a `200ms` "Ease-in-out" curve. It should feel like ink spreading—smooth and intentional.
*   **Status Indicators:** Instead of bright green dots, use `tertiary_fixed` for "In Progress" and a subtle `on_surface_variant` for "Archived." Keep the colors muted to maintain the authoritative atmosphere.