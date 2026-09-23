#!/usr/bin/env python3
from pathlib import Path
import re, struct, sys

ROOT = Path(__file__).resolve().parents[1]
JAVA = ROOT / 'app/src/main/java/com/civicfa1/dashboard/DashboardView.java'
MAIN = ROOT / 'app/src/main/java/com/civicfa1/dashboard/MainActivity.java'
GRADLE = ROOT / 'app/build.gradle'
RES = ROOT / 'app/src/main/res/drawable-nodpi'

errors=[]
def fail(msg): errors.append(msg)

def png_size(path):
    data=path.read_bytes()[:24]
    if len(data)<24 or data[:8] != b'\x89PNG\r\n\x1a\n': return None
    return struct.unpack('>II', data[16:24])

s=JAVA.read_text(encoding='utf-8')
main=MAIN.read_text(encoding='utf-8')
gradle=GRADLE.read_text(encoding='utf-8')

if 'refPatch' in s: fail('refPatch legacy patch renderer is present')
if 'drawReferenceHeaderOverlay' in s: fail('legacy mode-specific header overlay is present')
if 'drawUnifiedHeader(canvas);' in s: fail('runtime replacement header is active; master shell must own header')
if 'drawBottomNavigation(canvas);' in s: fail('runtime replacement navbar is active; master shell must own navbar')
if 'drawHeaderStateOverlay(canvas);' not in s: fail('dynamic OBD header state overlay is not active')
if 'modeBodyScale()' not in s: fail('mode body normalization is missing')
if 'toModeSourceY(y)' not in s: fail('touch/body transform mapping is missing')
if 'if (y >= NAV_TOP && y <= NAV_BOTTOM)' not in s: fail('touch navigation is not using one shared geometry')
if 'private static final float NAV_TOP = 625f;' not in s: fail('NAV_TOP must be 625')
if 'private static final float NAV_BOTTOM = 705f;' not in s: fail('NAV_BOTTOM must be 705')
if 'new DashboardView(this)' not in main: fail('MainActivity is not using DashboardView')
if 'versionCode 29' not in gradle: fail('versionCode is not 29')
if 'versionName "1.1.2"' not in gradle: fail('versionName is not 1.1.2')

for name in ('background_connect.png','background_sport.png','background_diagnostics.png'):
    p=RES/name
    if not p.exists(): fail(f'missing {name}')
    elif png_size(p)!=(1280,720): fail(f'{name} is not 1280x720: {png_size(p)}')

# Runtime must not paint large rectangular masks over the background before the mode overlays.
on_draw=s[s.find('@Override protected void onDraw'):s.find('private void drawBackground')]
if 'drawUnifiedHeader' in on_draw or 'drawBottomNavigation' in on_draw:
    fail('onDraw still invokes replacement static chrome')

if errors:
    for e in errors: print('VERIFY FAILED:', e, file=sys.stderr)
    sys.exit(1)
print('V1_1_2_MASTER_SHELL_INVARIANTS_PASS')
