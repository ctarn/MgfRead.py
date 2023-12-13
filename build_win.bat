pyinstaller -F -w --noconfirm -i fig/MgfRead.png MgfRead.py
del MgfRead.spec
rmdir /s /q build
