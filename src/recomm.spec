import shutil

a = Analysis(
    scripts=['recomm_town/window_main.py'],
)
pyz = PYZ(a.pure)
exe = EXE(pyz, a.scripts, a.binaries, a.zipfiles, a.datas, name="recomm")

shutil.rmtree('dist/assets', ignore_errors=True)
shutil.copytree(SPECPATH + './recomm_town/assets', 'dist/assets')