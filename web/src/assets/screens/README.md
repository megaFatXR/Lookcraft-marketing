# App screens for the landing page

Each phone frame on the home page shows a placeholder until a screenshot with its
name is here. Add the file and rebuild: nothing else to change. Use full-size
iPhone screenshots (portrait, like 1320×2868), as `.png`, `.jpg` or `.webp`.
Astro resizes them for the web.

| File name        | Where                        | Screen to show                                                                    |
| :--------------- | :--------------------------- | :-------------------------------------------------------------------------------- |
| `hero`           | Top of the page              | A finished try-on on the look page: the shopper wearing a whole look              |
| `step-concept`   | How it works, step 2         | The top of a concept as first opened (no looks crafted yet, no developer details): its name, palette, description, "Craft your looks" and the first row. A card zooms in on it (see below) |
| `step-try-on`    | How it works, step 3         | The look page with its try-on, top of the screen. A card shows its pieces to buy (see below) |

Step 1 of How it works is drawn (`src/components/BriefSources.astro`), so it needs
no screenshot.

Step 2 (`src/components/ConceptCallout.astro`) puts a card over the phone with two of
the concept's rows, Top and Bottom, drawn in the site's code from the concept "Navy City
Look", with the shops' thumbnails in `src/assets/concept/`. The coral outline on the phone
is placed in screen percentages around the Top row: move it (`.zoom`) if you replace
`step-concept` with a screen laid out differently. The current shot was edited from a
Debug build: developer lines, the reference thumbnail and "Looks crafted" taken out, the description rewritten, the screen ended after the first row, the heading and button
renamed to what the app shows before a look exists.

Keep the photos to people who agreed to appear, and don't show real account
details, emails or balances you'd rather not publish.

Step 3 (`src/components/LookCallout.astro`) puts a card over the phone with the look's
"Buy the pieces" list, drawn in the site's code from Look 1 of "Navy City Look", with the
shops' thumbnails in `src/assets/look/`. Keep the list in step with the try-on shown.
