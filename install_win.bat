@echo off
for /f "delims=" %%a in ('dir /l /s /b *.apk') do (
   echo adb install %%~na%%~xa
   adb install %%a
)

pause