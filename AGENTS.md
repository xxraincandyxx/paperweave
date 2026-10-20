# PaperWeave UI Rules

For UI tasks, preserve the PDF pipeline, model configuration and export contracts.
Use the existing vanilla HTML/CSS/JS stack; do not add dependencies for styling.
Keep PaperWeave branding and its offline single-file HTML capability.

## Direction
Scientific Editorial × Swiss Modernism: a restrained research reading tool.
Use paper, page numbers, citations, annotations and indexes as the visual language.
Do not introduce robots, AI sparkles, decorative diagrams or marketing filler.

## Avoid
- Decorative gradients, glass, glow and oversized navigation.
- Nested cards, card grids, excessive rounded pills and arbitrary shadows.
- Frames around every section or wide Chinese letter spacing.
- Multiple competing accent colors, tiny low-contrast captions and visual clutter.

## System
- Follow an 8px spacing rhythm; content width is at most 1240px.
- Use four type levels: display, heading, body and caption.
- Serif display typography; readable sans-serif UI; monospace only for references.
- Neutral canvas #F6F7F9, white surface, ink #13233F and muted #626F83 (AA on the canvas).
- Cobalt #3158F5 is the primary accent; orange #E66A42 only marks annotations.
- Prefer whitespace and alignment; use fine rules only where they clarify grouping.
- Use obvious frames primarily on interactive controls.
- Never load fonts, styles, scripts or icons from a CDN in exported HTML.

## Interaction
- Retain existing DOM IDs, API routes, data schemas and download names.
- Use native controls, visible :focus-visible and meaningful accessible names.
- Keep mobile touch targets at least 44px; mobile form text is at least 16px.
- Preserve loading, empty, error and unverified-evidence states.
- Visual improvements must not imply stronger verification than the pipeline provides.

## Verification
- Render actual upload and exported pages before and after editing.
- Check desktop at 1440px and mobile at 390px, including long file names.
- Check contrast, wrapping, alignment, keyboard focus and horizontal overflow.
- Recheck search, evidence pages, zoom, collapse, both map views and four exports.
- Verify file:// offline rendering and reopening a downloaded HTML copy.
- Consult https://vercel.com/design/guidelines for UI quality review.
