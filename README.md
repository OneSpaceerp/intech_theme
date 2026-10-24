# In Tech

Brand theme and white-label layer for **Frappe / ERPNext v16.51 and later** (checked against
v16.51.0 and v16.53.0 of Frappe, and v16.52.1 of ERPNext).

It makes the desk read as one product, **In Tech**, rather than as ERPNext on Frappe:

- **Brand**: the In Tech mark, wordmark, favicon and loading screen everywhere the platform
  would show its own: the desk, `/desk`, the login page, the website, emails and the About
  dialog.
- **White label**: "ERPNext" and "Frappe" are renamed in every language the platform ships, and
  vendor help links, promotions, update pop-ups and telemetry are switched off.
- **App icons**: every installed app gets an In Tech name and tile on the apps screen, the dock
  and the sidebar header (ERPNext becomes *In Tech ERP*, Frappe HR becomes *People*, the
  framework becomes *Platform*, and so on). An app the theme does not know gets a monogram tile,
  so no vendor logo ever shows.
- **Palette**: taken from the logo: ink `#1E2448`, deep `#245490`, primary `#2472AE`, azure
  `#1E90D2`, steel `#7898B8`, mist `#ABC7DA`, ice `#C3DFEC`. Light and dark (dark is navy, not
  grey).
- **Colourful menus**: every sidebar, dock and menu entry sits on its own coloured chip, eight
  hues in turn, so neighbouring entries never share a colour. Four palettes; every hue is
  tested to keep a white glyph legible (3:1).
- **`/desk` backgrounds**: *Circuit* (the logo's traces, drawn large), *Aurora*, *Mesh*,
  *Waves*, or your own picture under a brand tint, with a frosted header, a greeting and glass
  app tiles.

Nothing in `frappe/` or `erpnext/` is modified. Everything attaches through hooks, template
overrides, translations and CSS custom properties, so `bench update` does not undo it.

## Install

Install it **last**, after ERPNext, HRMS and any other app. Install order is what lets its
translations, templates and stylesheets take precedence.

```bash
bench get-app /path/to/intech_theme          # or the git URL
bench --site your.site install-app intech_theme
bench build --app intech_theme
bench --site your.site clear-cache
bench restart
```

On install, and after every migrate, the app writes the brand name, logo and favicon into
*System Settings*, *Website Settings* and *Navbar Settings*. What was there before is kept, and
`bench --site your.site uninstall-app intech_theme` puts it back.

Each release afterwards:

```bash
bench --site your.site backup --with-files
cd apps/intech_theme && git pull
bench --site your.site migrate
bench build --app intech_theme
bench restart
```

## Settings

**In Tech Theme Settings** (System Manager): search for it in the desk. Saving applies to every
open session without a reload.

| Tab | What it controls |
|---|---|
| Brand | Name (and an Arabic spelling, if wanted), tagline, logo, logo for dark surfaces, favicon, loading image, copyright line, support address, email footer |
| White Label | Master switch; renaming interface text; replacing app icons and names; hiding vendor help links, promotions and update notices; telemetry |
| Theme | Primary, accent and ink colours; sidebar style (Navy, Gradient, Light); colourful menus and their palette; forced dark mode; font |
| Desk Background | The `/desk` background (Circuit, Aurora, Mesh, Waves, Image, None), the picture and how strongly it is tinted, the greeting, glass tiles, and an optional quieter background behind workspaces |
| Apps | Rename or re-icon a particular app: its package name (`erpnext`, `hrms`, ...) and the title or icon to show instead |
| Login Page | Headline, supporting line, and a background picture for the brand panel |

## How it is built

The layout follows Swift Theme's: server code under `api/`, the brand's colours and app identities
in one dependency-free module (`palette.py`), styles as plain CSS partials pulled into two
`.bundle.scss` files, and scripts as small modules pulled into two `.bundle.js` files, so every
release gets a content-hashed URL.

| Layer | Covers |
|---|---|
| `translations/*.csv` (41 languages) | Every translatable string that names the vendor, English included. Generated from the vendor apps' catalogues and source. |
| `install.py` | App name, logo, favicon, splash and footer in the site's settings; vendor help items hidden; update pop-ups, product suggestions and telemetry off |
| `api/boot.py`, `api/apps.py` | The theme and every app's name and tile in the desk's boot payload, the setup wizard's app list and the About dialog |
| `templates/` | Loading screen, website footer line, email footer |
| `api/website.py` | Theme attributes and colours on every server-rendered page before first paint; vendor names out of portal and login pages |
| `public/js/` | What the desk's own scripts write after load: names, logos, support links, the `/desk` greeting and the login brand panel |

### After upgrading Frappe or ERPNext

New versions add strings. Regenerate the translations against the upgraded apps:

```bash
python apps/intech_theme/tools/generate_translations.py --apps apps/frappe apps/erpnext apps/hrms
bench --site your.site clear-cache
```

`tools/build_app_icons.py` redraws the app tiles after you edit `APP_IDENTITIES` in
`palette.py`; `tools/build_backdrops.py` redraws the backdrop artwork.

## Tests

The rebrand rules, the palette, the app identities and the shipped artwork are tested without a
bench:

```bash
python intech_theme/tests/test_text.py
python intech_theme/tests/test_palette.py
```

The settings DocType's tests need a site:

```bash
bench --site your.site run-tests --app intech_theme
```

## License

MIT
