# Hero photos

The hero (`src/components/HeroTryOn.astro`) shows a phone with a plain photo that wipes
to its try-on, then the look's pieces float out around it. It plays for two people in
turn, in the order of the `scenes` list: scene 2 (boho) first, then scene 1 (old money).
Until the photos are here, it shows drawn stand-ins.

| File name        | What                                                    |
| :--------------- | :------------------------------------------------------ |
| `scene-1-before` | Old money look's person, everyday clothes (shown second) |
| `scene-1-after`  | The same photo tried on in the app, wearing a look      |
| `scene-2-before` | Boho look's person, everyday clothes (shown first)      |
| `scene-2-after`  | Their try-on                                            |

Use `.jpg`, `.png` or `.webp`. Full-body portraits, head to shoes, with the person in
the middle. The phone screen is tall (about 1 : 2.17), so the sides get cropped. The
before and after must be framed the same, so the wipe only changes the clothes. Try-ons
from the app keep the original framing.

After adding photos, update each scene's `pieces` in `HeroTryOn.astro`: title, brand,
price, the shop's thumbnail (in `src/assets/look/` or a new folder) and `at`, the spot
on the photo where the piece is worn, in percent of the screen.

Only use photos of people who agreed to appear on the site.
