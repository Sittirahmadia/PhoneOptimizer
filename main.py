"""
Android Phone Optimizer — Kivy APK
Non-root | Requires WRITE_SETTINGS (auto-prompt) +
          WRITE_SECURE_SETTINGS (one-time ADB grant)
"""

from kivy.app import App
from kivy.uix.screenmanager import ScreenManager, Screen, SlideTransition
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.gridlayout import GridLayout
from kivy.uix.scrollview import ScrollView
from kivy.uix.label import Label
from kivy.uix.button import Button
from kivy.uix.slider import Slider
from kivy.uix.popup import Popup
from kivy.uix.widget import Widget
from kivy.graphics import Color, RoundedRectangle, Rectangle
from kivy.core.window import Window
from kivy.metrics import dp
from kivy.clock import Clock
from kivy.utils import platform

import threading

# ── Platform check ─────────────────────────────────────────────────────────
IS_ANDROID = platform == "android"

if IS_ANDROID:
    from jnius import autoclass, cast
    from android.permissions import request_permissions, Permission, check_permission

    # Java classes
    Settings        = autoclass("android.provider.Settings")
    ContentResolver = autoclass("android.content.ContentResolver")
    PythonActivity  = autoclass("org.kivy.android.PythonActivity")
    Intent          = autoclass("android.content.Intent")
    Uri             = autoclass("android.net.Uri")
    Build           = autoclass("android.os.Build")

    def get_resolver():
        return PythonActivity.mActivity.getContentResolver()

    def get_context():
        return PythonActivity.mActivity

# ── Colors ──────────────────────────────────────────────────────────────────
BG       = (0.05, 0.06, 0.08, 1)
CARD     = (0.09, 0.11, 0.14, 1)
ACCENT   = (0.0,  0.78, 1.0,  1)
ACCENT2  = (0.0,  1.0,  0.62, 1)
WARNING  = (1.0,  0.67, 0.0,  1)
DANGER   = (1.0,  0.28, 0.34, 1)
TEXT     = (0.91, 0.94, 0.99, 1)
MUTED    = (0.35, 0.42, 0.50, 1)
SUCCESS  = (0.0,  1.0,  0.62, 1)

# hex helpers for markup
def hex_c(rgba): return "#{:02x}{:02x}{:02x}".format(*[int(c*255) for c in rgba[:3]])

A_HEX  = hex_c(ACCENT)
A2_HEX = hex_c(ACCENT2)
W_HEX  = hex_c(WARNING)
D_HEX  = hex_c(DANGER)
T_HEX  = hex_c(TEXT)
M_HEX  = hex_c(MUTED)
S_HEX  = hex_c(SUCCESS)

# ── UI Helpers ──────────────────────────────────────────────────────────────
Window.clearcolor = BG[:3] + (1,)

def make_label(text, size=14, bold=False, color=TEXT, markup=False, halign="left"):
    lbl = Label(
        text=text, font_size=dp(size), bold=bold,
        color=color, markup=markup,
        halign=halign, valign="middle",
        size_hint_y=None
    )
    lbl.bind(texture_size=lambda i, v: setattr(i, "height", v[1] + dp(6)))
    lbl.bind(width=lambda i, v: setattr(i, "text_size", (v, None)))
    return lbl

def make_btn(text, bg_color=ACCENT, text_color=(0,0,0,1), callback=None, height=dp(46)):
    btn = Button(
        text=text, font_size=dp(13), bold=True,
        background_normal="", background_color=bg_color,
        color=text_color, size_hint_y=None, height=height,
        border=(8, 8, 8, 8)
    )
    if callback:
        btn.bind(on_press=lambda *a: callback())
    return btn

def card_box(padding=dp(14), spacing=dp(8)):
    box = BoxLayout(orientation="vertical",
                    padding=padding, spacing=spacing,
                    size_hint_y=None)
    box.bind(minimum_height=box.setter("height"))
    with box.canvas.before:
        Color(*CARD)
        box._rect = RoundedRectangle(pos=box.pos, size=box.size, radius=[dp(10)])
    box.bind(pos=lambda i, v: setattr(i._rect, "pos", v),
             size=lambda i, v: setattr(i._rect, "size", v))
    return box

def spacer(h=dp(10)):
    w = Widget(size_hint_y=None, height=h)
    return w

# ── ADB/Settings writer ─────────────────────────────────────────────────────
def write_system(key, value):
    if not IS_ANDROID:
        return True, f"[PC] settings put system {key} {value}"
    try:
        Settings.System.putInt(get_resolver(), key, int(value))
        return True, f"{key} = {value}"
    except Exception as e:
        return False, str(e)

def write_global(key, value):
    if not IS_ANDROID:
        return True, f"[PC] settings put global {key} {value}"
    try:
        Settings.Global.putInt(get_resolver(), key, int(value))
        return True, f"{key} = {value}"
    except Exception as e:
        return False, str(e)

def write_global_float(key, value):
    if not IS_ANDROID:
        return True, f"[PC] settings put global {key} {value}"
    try:
        Settings.Global.putFloat(get_resolver(), key, float(value))
        return True, f"{key} = {value}"
    except Exception as e:
        return False, str(e)

def write_secure(key, value):
    if not IS_ANDROID:
        return True, f"[PC] settings put secure {key} {value}"
    try:
        Settings.Secure.putInt(get_resolver(), key, int(value))
        return True, f"{key} = {value}"
    except Exception as e:
        return False, str(e)

def check_write_settings():
    if not IS_ANDROID:
        return True
    return Settings.System.canWrite(get_context())

def request_write_settings():
    if not IS_ANDROID:
        return
    try:
        pkg = get_context().getPackageName()
        intent = Intent(Settings.ACTION_MANAGE_WRITE_SETTINGS,
                        Uri.parse(f"package:{pkg}"))
        intent.addFlags(Intent.FLAG_ACTIVITY_NEW_TASK)
        get_context().startActivity(intent)
    except Exception as e:
        pass

# ── Optimization functions ───────────────────────────────────────────────────
def cmd_lock_120hz():
    results = []
    for key in ["min_refresh_rate", "peak_refresh_rate"]:
        ok, msg = write_system(key, 120)
        results.append(f"{'✅' if ok else '❌'} {key}: {msg}")
    return "\n".join(results)

def cmd_reset_refresh():
    results = []
    for key in ["min_refresh_rate", "peak_refresh_rate"]:
        ok, msg = write_system(key, 60)
        results.append(f"{'✅' if ok else '❌'} {key}: {msg}")
    return "\n".join(results)

def cmd_disable_adaptive_brightness():
    ok, msg = write_system("screen_brightness_mode", 0)
    return f"{'✅' if ok else '❌'} adaptive brightness off: {msg}"

def cmd_enable_adaptive_brightness():
    ok, msg = write_system("screen_brightness_mode", 1)
    return f"{'✅' if ok else '❌'} adaptive brightness on: {msg}"

def cmd_disable_aod():
    ok, msg = write_secure("doze_always_on", 0)
    return f"{'✅' if ok else '❌'} AOD off: {msg}"

def cmd_haptic(val):
    ok, msg = write_system("haptic_feedback_enabled", val)
    return f"{'✅' if ok else '❌'} haptic={val}: {msg}"

def cmd_pointer_speed(val):
    ok, msg = write_system("pointer_speed", int(val))
    return f"{'✅' if ok else '❌'} pointer_speed={val}: {msg}"

def cmd_anim_scale(window, transition, animator):
    msgs = []
    for key, val in [("window_animation_scale", window),
                     ("transition_animation_scale", transition),
                     ("animator_duration_scale", animator)]:
        ok, msg = write_global_float(key, val)
        msgs.append(f"{'✅' if ok else '❌'} {key}={val}")
    return "\n".join(msgs)

def cmd_disable_all_anim():
    return cmd_anim_scale(0, 0, 0)

def cmd_reset_anim():
    return cmd_anim_scale(1.0, 1.0, 1.0)

def cmd_low_power_off():
    ok, msg = write_global("low_power", 0)
    return f"{'✅' if ok else '❌'} low_power=0: {msg}"

# ── Result Popup ────────────────────────────────────────────────────────────
def show_popup(title, message):
    content = BoxLayout(orientation="vertical", padding=dp(14), spacing=dp(10))
    with content.canvas.before:
        Color(*CARD)
        content._bg = Rectangle(pos=content.pos, size=content.size)
    content.bind(pos=lambda i, v: setattr(i._bg, "pos", v),
                 size=lambda i, v: setattr(i._bg, "size", v))

    lbl = make_label(message, size=12, color=TEXT, markup=False)
    lbl.bind(width=lambda i, v: setattr(i, "text_size", (v, None)))
    content.add_widget(lbl)

    close_btn = make_btn("Tutup", bg_color=ACCENT, text_color=(0,0,0,1))
    content.add_widget(close_btn)

    popup = Popup(title=title, content=content,
                  size_hint=(0.88, None), height=dp(260),
                  title_color=ACCENT, title_size=dp(14),
                  separator_color=ACCENT,
                  background_color=CARD,
                  border=(1,1,1,1))
    close_btn.bind(on_press=popup.dismiss)
    popup.open()

# ── Screens ──────────────────────────────────────────────────────────────────
class HomeScreen(Screen):
    def __init__(self, **kw):
        super().__init__(**kw)
        self._build()

    def _build(self):
        root = BoxLayout(orientation="vertical", spacing=0)

        # Header
        hdr = BoxLayout(size_hint_y=None, height=dp(56),
                        padding=[dp(16), 0], spacing=dp(10))
        with hdr.canvas.before:
            Color(0.07, 0.09, 0.12, 1)
            hdr._bg = Rectangle(pos=hdr.pos, size=hdr.size)
        hdr.bind(pos=lambda i,v: setattr(i._bg,"pos",v),
                 size=lambda i,v: setattr(i._bg,"size",v))

        hdr.add_widget(make_label(f"[b][color={A_HEX}]⚡ Phone Optimizer[/color][/b]",
                                  size=16, markup=True))
        root.add_widget(hdr)

        # Warning bar if WRITE_SETTINGS not granted
        self.warn_bar = BoxLayout(size_hint_y=None, height=dp(38),
                                  padding=[dp(12), 0])
        with self.warn_bar.canvas.before:
            Color(0.5, 0.3, 0.0, 1)
            self.warn_bar._bg = Rectangle(pos=self.warn_bar.pos, size=self.warn_bar.size)
        self.warn_bar.bind(pos=lambda i,v: setattr(i._bg,"pos",v),
                           size=lambda i,v: setattr(i._bg,"size",v))
        warn_lbl = make_label(
            f"[color={W_HEX}]⚠ Izin WRITE_SETTINGS belum diberikan — Ketuk untuk mengaktifkan[/color]",
            size=11, markup=True)
        self.warn_bar.add_widget(warn_lbl)
        self.warn_bar.bind(on_touch_down=self._on_warn_tap)
        root.add_widget(self.warn_bar)

        # Scrollable content
        sv = ScrollView(size_hint=(1, 1))
        content = BoxLayout(orientation="vertical", padding=dp(14),
                            spacing=dp(12), size_hint_y=None)
        content.bind(minimum_height=content.setter("height"))

        content.add_widget(self._section_display())
        content.add_widget(self._section_touch())
        content.add_widget(self._section_anim())
        content.add_widget(self._section_perf())
        content.add_widget(self._section_info())
        content.add_widget(spacer(dp(20)))

        sv.add_widget(content)
        root.add_widget(sv)
        self.add_widget(root)
        Clock.schedule_once(self._check_perm, 0.5)

    def _check_perm(self, *a):
        if check_write_settings():
            self.warn_bar.height = 0
            self.warn_bar.opacity = 0

    def _on_warn_tap(self, instance, touch):
        if instance.collide_point(*touch.pos):
            request_write_settings()
            Clock.schedule_once(self._check_perm, 1.5)

    def _run(self, fn, *args):
        def worker():
            result = fn(*args) if args else fn()
            Clock.schedule_once(lambda dt: show_popup("Hasil", result), 0)
        threading.Thread(target=worker, daemon=True).start()

    # ── Section: Display ──────────────────────────────────────────────────────
    def _section_display(self):
        box = card_box()
        box.add_widget(make_label(f"[b][color={A_HEX}]🖥️  Display & Refresh Rate[/color][/b]",
                                  size=13, markup=True))
        box.add_widget(make_label(
            f"[color={M_HEX}]Lock layar ke 120Hz untuk scrolling & animasi lebih mulus.[/color]",
            size=11, markup=True))
        box.add_widget(spacer(dp(4)))

        row1 = BoxLayout(size_hint_y=None, height=dp(46), spacing=dp(8))
        row1.add_widget(make_btn("🔒 Lock 120Hz", bg_color=ACCENT,
                                 text_color=(0,0,0,1),
                                 callback=lambda: self._run(cmd_lock_120hz)))
        row1.add_widget(make_btn("🔓 Reset 60Hz", bg_color=CARD,
                                 text_color=TEXT,
                                 callback=lambda: self._run(cmd_reset_refresh)))
        box.add_widget(row1)

        box.add_widget(spacer(dp(6)))
        box.add_widget(make_label(
            f"[color={M_HEX}]Adaptive brightness bisa bikin layar flicker. Matikan untuk kestabilan.[/color]",
            size=11, markup=True))
        row2 = BoxLayout(size_hint_y=None, height=dp(46), spacing=dp(8))
        row2.add_widget(make_btn("🚫 Matikan Auto Brightness", bg_color=WARNING,
                                 text_color=(0,0,0,1),
                                 callback=lambda: self._run(cmd_disable_adaptive_brightness)))
        row2.add_widget(make_btn("✅ Nyalakan", bg_color=CARD,
                                 text_color=TEXT,
                                 callback=lambda: self._run(cmd_enable_adaptive_brightness)))
        box.add_widget(row2)

        box.add_widget(spacer(dp(6)))
        box.add_widget(make_label(
            f"[color={M_HEX}]AOD (Always-On Display) bisa mengganggu responsivitas layar.[/color]",
            size=11, markup=True))
        box.add_widget(make_btn("💤 Matikan AOD", bg_color=WARNING,
                                text_color=(0,0,0,1),
                                callback=lambda: self._run(cmd_disable_aod)))
        return box

    # ── Section: Touch ────────────────────────────────────────────────────────
    def _section_touch(self):
        box = card_box()
        box.add_widget(make_label(f"[b][color={A2_HEX}]👆 Touchscreen[/color][/b]",
                                  size=13, markup=True))

        # Pointer speed
        box.add_widget(make_label(
            f"[color={M_HEX}]Kecepatan pointer (0=lambat, 7=cepat):[/color]",
            size=11, markup=True))
        self.ptr_slider = Slider(min=0, max=7, value=4, step=1,
                                 size_hint_y=None, height=dp(36))
        self.ptr_slider.bind(value=self._on_ptr_label)
        box.add_widget(self.ptr_slider)

        self.ptr_val_lbl = make_label(f"[color={A_HEX}]Nilai: 4[/color]",
                                      size=11, markup=True)
        box.add_widget(self.ptr_val_lbl)

        box.add_widget(make_btn("✅ Terapkan Pointer Speed", bg_color=ACCENT,
                                text_color=(0,0,0,1),
                                callback=lambda: self._run(cmd_pointer_speed,
                                                           int(self.ptr_slider.value))))
        box.add_widget(spacer(dp(8)))

        # Haptic
        box.add_widget(make_label(
            f"[color={M_HEX}]Haptic feedback:[/color]", size=11, markup=True))
        row = BoxLayout(size_hint_y=None, height=dp(46), spacing=dp(8))
        row.add_widget(make_btn("✅ Nyalakan Haptic", bg_color=ACCENT2,
                                text_color=(0,0,0,1),
                                callback=lambda: self._run(cmd_haptic, 1)))
        row.add_widget(make_btn("🚫 Matikan Haptic", bg_color=DANGER,
                                text_color=TEXT,
                                callback=lambda: self._run(cmd_haptic, 0)))
        box.add_widget(row)
        return box

    def _on_ptr_label(self, instance, val):
        self.ptr_val_lbl.text = f"[color={A_HEX}]Nilai: {int(val)}[/color]"

    # ── Section: Animasi ──────────────────────────────────────────────────────
    def _section_anim(self):
        box = card_box()
        box.add_widget(make_label(f"[b][color={A_HEX}]✨ Kecepatan Animasi UI[/color][/b]",
                                  size=13, markup=True))
        box.add_widget(make_label(
            f"[color={M_HEX}]Kurangi animasi agar UI terasa lebih cepat & responsif.[/color]",
            size=11, markup=True))
        box.add_widget(spacer(dp(4)))

        labels = ["Window", "Transition", "Animator"]
        self.anim_sliders = []
        for lbl_text in labels:
            row = BoxLayout(size_hint_y=None, height=dp(32), spacing=dp(8))
            row.add_widget(make_label(f"[color={TEXT[0]},{TEXT[1]},{TEXT[2]}]{lbl_text}:[/color]",
                                      size=11, markup=False, color=TEXT))
            sc = Slider(min=0, max=2, value=0.5, step=0.5, size_hint_x=0.65)
            self.anim_sliders.append(sc)
            row.add_widget(sc)
            box.add_widget(row)

        box.add_widget(spacer(dp(4)))
        row2 = BoxLayout(size_hint_y=None, height=dp(46), spacing=dp(6))
        row2.add_widget(make_btn("✅ Terapkan", bg_color=ACCENT,
                                 text_color=(0,0,0,1),
                                 callback=lambda: self._run(cmd_anim_scale,
                                     self.anim_sliders[0].value,
                                     self.anim_sliders[1].value,
                                     self.anim_sliders[2].value)))
        row2.add_widget(make_btn("❌ Off Semua", bg_color=ACCENT2,
                                 text_color=(0,0,0,1),
                                 callback=lambda: self._run(cmd_disable_all_anim)))
        row2.add_widget(make_btn("🔄 Reset", bg_color=CARD,
                                 text_color=TEXT,
                                 callback=lambda: self._run(cmd_reset_anim)))
        box.add_widget(row2)
        box.add_widget(make_label(
            f"[color={W_HEX}]⚠ Butuh izin WRITE_SECURE_SETTINGS (grant via ADB sekali)[/color]",
            size=10, markup=True))
        return box

    # ── Section: Performa ─────────────────────────────────────────────────────
    def _section_perf(self):
        box = card_box()
        box.add_widget(make_label(f"[b][color={A2_HEX}]🚀 Performa[/color][/b]",
                                  size=13, markup=True))
        box.add_widget(make_label(
            f"[color={M_HEX}]Matikan mode hemat daya agar CPU berjalan penuh.[/color]",
            size=11, markup=True))
        box.add_widget(make_btn("⚡ Nonaktifkan Battery Saver", bg_color=ACCENT2,
                                text_color=(0,0,0,1),
                                callback=lambda: self._run(cmd_low_power_off)))
        return box

    # ── Section: Info ADB ─────────────────────────────────────────────────────
    def _section_info(self):
        box = card_box()
        box.add_widget(make_label(f"[b][color={W_HEX}]📋 Grant Izin via ADB (sekali saja)[/color][/b]",
                                  size=13, markup=True))
        steps = (
            "Untuk fitur animasi & AOD, jalankan\n"
            "perintah ini dari PC setelah install APK:\n\n"
            "  adb shell pm grant\n"
            "  <package.name>\n"
            "  android.permission\n"
            "  .WRITE_SECURE_SETTINGS\n\n"
            "Package name ada di buildozer.spec\n"
            "Cukup sekali, lalu cabut USB."
        )
        box.add_widget(make_label(steps, size=11, color=MUTED))
        return box

# ── App ──────────────────────────────────────────────────────────────────────
class PhoneOptimizerApp(App):
    def build(self):
        self.title = "Phone Optimizer"
        sm = ScreenManager(transition=SlideTransition())
        sm.add_widget(HomeScreen(name="home"))
        return sm

if __name__ == "__main__":
    PhoneOptimizerApp().run()
