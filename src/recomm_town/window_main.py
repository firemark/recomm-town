#!/usr/bin/env python3
import os
import sys
from pathlib import Path
from tkinter import ttk, Tk, StringVar, IntVar, BooleanVar, W
from tkinter.font import Font

ASSETS_PATH = Path(sys.executable).parent / "assets"
TOWNS_PATH = ASSETS_PATH / "towns"
os.environ["ASSETS"] = str(ASSETS_PATH)


class StartupApp:
    def __init__(self):
        self.root = Tk()
        self.root.title("Recomm Town Setup")
        self.frm = ttk.Frame(self.root, padding=10)
        self.frm.grid()

        towns = list(TOWNS_PATH.glob("*.yaml"))
        self.town = StringVar(value=str(towns[0]))
        self.match_time = IntVar(value=300)
        self.fullscreen = BooleanVar(value=False)
        self.exited = False
        self._rows = 0
        
        self.label_font = Font(size=12)
        self._label("Town:")
        for file in towns:
            self._grid(ttk.Radiobutton(self.frm, text=file.stem, value=str(file), variable=self.town))

        self._sep()

        self.match_time_label = self._label("Match time:")
        self._grid(ttk.Scale(self.frm, orient="horizontal", from_=1, to_=3600, variable=self.match_time, command=self.on_match_time))
        self.on_match_time(self.match_time.get())

        self._label("Fullscreen:")
        self._grid(ttk.Checkbutton(self.frm, variable=self.fullscreen))

        self._sep()
        self._grid(ttk.Button(self.frm, text="Quit", command=self.quit), col=0, new_row=False)
        self._grid(ttk.Button(self.frm, text="Run", command=self.run), col=1)

    def _label(self, label):
        return self._grid(ttk.Label(self.frm, text=label, font=self.label_font, width=15), col=0, new_row=False)
    
    def _sep(self):
        return self._grid(ttk.Separator(self.frm))

    def _grid(self, widget, col=1, new_row=True):
        widget.grid(column=col, row=self._rows, sticky=W)
        if new_row:
            self._rows += 1
        return widget

    def loop(self):
        self.root.mainloop()

    def on_match_time(self, value):
        v = int(float(value))
        minutes = v // 60
        seconds = v % 60
        self.match_time_label.config(text=f"Match time {minutes:02d}:{seconds:02d}")

    def run(self):
        self.root.destroy()

    def quit(self):
        self.exited = True
        self.root.destroy()


if __name__ == "__main__":
    app = StartupApp()
    app.loop()
    if not app.exited:
        from recomm_town.generic_main import run
        run(
            town=Path(app.town.get()),
            match_time=app.match_time.get(),
            fullscreen=app.fullscreen.get(),
            output_filename="out.json",
        )
