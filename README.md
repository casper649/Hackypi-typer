# Hackypi-typer
in this you will need a hackypi from SD components. its great for python and having things automated 

**Typing_Connection.py**-handles communication between your Raspberry Pi Pico (HackyPi Typer) and your Windows computer over USB serial. It allows the Pico to receive information, commands, or text from the computer and process that information so the HackyPi can interact with the typing system. Essentially, it acts as the connection bridge between the computer and the Pico, allowing them to communicate so the HackyPi can automate typing tasks.

**Typing_Tester.py**-is responsible for testing and evaluating the HackyPi Typer's typing performance. It measures typing speed (WPM) and accuracy by comparing the text entered by the Raspberry Pi Pico against the original text. This helps verify that the HackyPi Typer can consistently type at the desired speed and accuracy, ensuring it meets the project's performance goals.

**Windows_Typing_connection.py**-handles the Windows-side communication with the Raspberry Pi Pico in the HackyPi Typer. It establishes a USB serial connection, allowing Windows to send typing instructions and text to the Pico. It acts as the computer-side partner to **Typing_Connection.py**, coordinating data transfer so the Pico can receive the text and automatically type it using USB HID keyboard emulation.

please note you might have to change the underlined parts with the PATH you choose-

<pre><code>Set shell = CreateObject("WScript.Shell")
shell.Run """<ins>A:\Python</ins>\pythonw.exe"" ""<ins>A:\Hackypi\projects\Windows</ins>\Windows_typing_connection.py""", 0, False</code></pre>

to get a hackypi device please visit- https://shop.sb-components.co.uk/products/hackypi-compact-diy-usb-hacking-tool?srsltid=AYCX9vJD5jBOyuuJFF59QCk6LI_1GS4Bpfx2bz-cU9tmD4ACZ3XVAs73
