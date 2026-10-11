# 04: Home-screen install (PWA manifest and icons)

**What to build:** Adding the app to the home screen on Android or iOS
yields a proper "Cookbook" icon in the orange branding, and launching it
opens full-screen without browser chrome.

**Blocked by:** 01 (static files pipeline must be settled first).

**Status:** done

- [x] Web app manifest (name "Cookbook", standalone display, theme/background colors matching the orange palette) served as a static file and linked from the base template
- [x] Icon PNGs committed at 192x192 and 512x512 (maskable-friendly: the pot mark on an orange rounded background; generate with Pillow in a one-off script, committing the PNGs and the script)
- [x] `apple-touch-icon` (180x180 PNG) linked for iOS
- [x] `collectstatic` picks all of it up; manifest URL returns valid JSON referencing resolvable icon paths
- [x] Test: manifest endpoint serves JSON whose icon entries point at existing static files
- [x] Existing tests still pass
