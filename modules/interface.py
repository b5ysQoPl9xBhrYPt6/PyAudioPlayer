from os.path import *  # type: ignore
from flet import *  # type: ignore
from threading import Thread
from random import choice
from time import sleep
import flet_audio as fta
import flet as ft
import os, sys

class Interface:
    def __init__(self, audio_directory: str, page: Page):
        self.dir = audio_directory
        self.audio_list = [os.path.abspath(os.path.join(self.dir, audio)) for audio in os.listdir(self.dir)]
        self.page = page
        self.pos, self.dur = 0, 0
        self.pos_mins = 0
        self.pos_secs = 0
        self.dur_mins = 0
        self.dur_secs = 0
        self.chosen = choice(self.audio_list)
        # ELEMENTS
        self.title = Text(
            value = '',
            weight = FontWeight.W_500,
            color = Colors.WHITE54
        )
        self.button_pause = IconButton(
            icon = Icons.PLAY_ARROW,
            icon_color = Colors.WHITE30,
            style = ButtonStyle(
                shape = RoundedRectangleBorder(radius = 3),
                overlay_color = Colors.WHITE12
            ),
            on_click = lambda _: self.resume()
        )
        self.button_skip = IconButton(
            icon = Icons.SKIP_NEXT,
            icon_color = Colors.WHITE30,
            style = ButtonStyle(
                shape = RoundedRectangleBorder(radius = 3),
                overlay_color = Colors.WHITE12
            ),
            on_click = lambda _: self.skip()
        )
        self.slider = Slider(
            value = 0.25,
            expand = True,
            active_color = Colors.WHITE38,
            thumb_color = Colors.WHITE38,
            scale = 0.8,
            on_change_start = lambda _: self.pause(),
            on_change_end = lambda _: self.release(),
            on_change = lambda e: self.update_time_info(e)
        )
        self.time_info = Text(
            value = '0:00 / 0:00',
            color = Colors.WHITE38
        )
        self.player = fta.Audio(
            src = self.chosen, autoplay = False,
            on_position_changed = lambda _: self.update_slider(),
            on_state_changed = lambda e: self._check_end(e)
        )
        # ELEMENTS
        # GROUPS
        self.title_row = WindowDragArea(
            content = Row(
                controls = [
                    Icon(name = Icons.MUSIC_NOTE, color = Colors.WHITE30, size = 25),
                    self.title,
                    self.player
                ]
            )
        )
        self.buttons_row = Row(
            controls = [
                self.button_pause,
                self.button_skip
            ]
        )
        self.slider_row = Row(
            controls = [
                self.slider,
                self.time_info
            ],
            expand = True,
            alignment = MainAxisAlignment.SPACE_BETWEEN
        )
        # GROUPS
        # MAIN
        self.container = Container(
            content = Column(
                controls = [
                    Row(
                        controls = [
                            self.title_row,
                            self.buttons_row
                        ],
                        alignment = MainAxisAlignment.SPACE_BETWEEN
                    ),
                    self.slider_row
                ]
            ),
            expand = True,
            padding = 12,
            alignment = alignment.top_left,
            border_radius = 3,
            bgcolor = Colors.WHITE10
        )
        # MAIN
        Thread(target = lambda: self._thread_update_title(), daemon = True).start()

    def pause(self):
        self.button_pause.icon = Icons.PLAY_ARROW
        self.button_pause.on_click = lambda _: self.resume()
        self.player.pause()
        self.player.update()
        self.button_pause.update()

    def resume(self):
        self.button_pause.icon = Icons.PAUSE
        self.button_pause.on_click = lambda _: self.pause()
        self.player.resume()
        self.player.update()
        self.button_pause.update()

    def skip(self):
        if len(self.audio_list) < 1:
            self.audio_list = [os.path.abspath(os.path.join(self.dir, audio)) for audio in os.listdir(self.dir)]
        self.chosen = choice(self.audio_list)
        self.audio_list.remove(self.chosen)
        print(f'Chosen: {self.chosen.split('\\')[-1]};\nList lenght: {len(self.audio_list)}\n')

        self.player.src = self.chosen
        self.button_pause.icon = Icons.PAUSE
        self.button_pause.on_click = lambda _: self.pause()
        self.title.value = self.chosen.split('\\')[-1]
        self.time_info.value = '0:00 / 0:00'
        self.slider.value = 0
        self.slider.update()
        self.time_info.update()
        self.player.update()
        self.button_pause.update()
        self.title.update()
        Thread(target = lambda: self._thread_play_audio(), daemon = True).start()

    def update_slider(self):
        try:
            self.pos = self.player.get_current_position() if not self.player.get_current_position() is None else 0
            self.dur = self.player.get_duration() if not self.player.get_duration() is None else 0
            self.pos_mins = round(self.pos / 1000) // 60  # type: ignore
            self.pos_secs = round(self.pos / 1000) % 60  # type: ignore
            self.dur_mins = round(self.dur / 1000) // 60  # type: ignore
            self.dur_secs = round(self.dur / 1000) % 60  # type: ignore
            self.slider.value = round(self.pos / self.dur, 3)  # type: ignore
            self.time_info.value = f'{self.pos_mins}:{self.pos_secs:02d} / {self.dur_mins}:{self.dur_secs:02d}'
            self.slider.update()
            self.time_info.update()
        except ZeroDivisionError:
            pass

    def update_time_info(self, e: ControlEvent):
        self.pos = e.control.value * self.dur
        self.pos_mins = round(self.pos / 1000) // 60  # type: ignore
        self.pos_secs = round(self.pos / 1000) % 60  # type: ignore
        self.time_info.value = f'{self.pos_mins}:{self.pos_secs:02d} / {self.dur_mins}:{self.dur_secs:02d}'
        self.time_info.update()

    def release(self):
        self.player.seek(round(self.slider.value * self.dur))  # type: ignore
        print(round(self.slider.value * self.dur))  # type: ignore
        self.resume()

    def _thread_play_audio(self):
        sleep(0.05)
        self.player.play()
        self.player.update()

    def _thread_update_title(self):
        sleep(0.05)
        self.title.value = self.chosen.split('\\')[-1]
        self.title.update()

    def _check_end(self, e: fta.AudioStateChangeEvent):
        print(e.state)
        if e.state == fta.AudioState.COMPLETED:
            self.skip()

        
def main(page: Page, audio_directory: str):
    page.title = 'Audio Player'
    page.window.resizable = False
    page.window.maximizable = False
    page.window.minimizable = False
    page.window.alignment = alignment.center
    page.window.title_bar_hidden = True
    page.window.opacity = 0.6
    page.window.always_on_top = True
    page.theme_mode = ThemeMode.DARK
    page.window.width = 480
    page.window.height = 120

    interface = Interface(audio_directory, page)

    page.add(
        *[
            interface.container
        ]
    )

    page.update()
