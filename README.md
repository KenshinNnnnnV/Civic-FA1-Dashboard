> Current package: **v1.1.2 — unified clean-shell renderer on the full v0.9.5 functional base.**

# Civic FA1 Dashboard v1.1.2 — Dashboard-1 production fix

Production Android project for Honda Civic FA1 dashboard.

**Canonical repository:** `KenshinNnnnnV/Civic-FA1-Dashboard` (Dashboard-1).

**Do not upload this package to `Civic-FA1-Dashboard-2`.**

Target device:
- Android head unit, 1280x720 landscape
- UIS8581A, 2 GB RAM
- Honda Civic FA1 2011 / R18A 1.8L
- OBD-II via ELM327 / Vgate (BLE and Bluetooth Classic)

This clean package intentionally contains **no historical design-reference folders, old dashboard images, or previous-version change files**.

Runtime artwork used by the APK is only:
- `app/src/main/res/drawable-nodpi/background_connect.png`
- `app/src/main/res/drawable-nodpi/background_sport.png`
- `app/src/main/res/drawable-nodpi/background_diagnostics.png`
- `app/src/main/res/drawable-nodpi/splash_bg.jpg`

Build through GitHub Actions or with an Android/Gradle environment compatible with compileSdk 34 and Java 17.


## v1.1.2 Master Shell
Static header/navbar geometry lives in the runtime PNG shells. DashboardView draws only dynamic vehicle/OBD data and interaction state.
