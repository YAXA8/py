import asyncio
import websockets
import json
import subprocess
import sys
import io
import base64

# --- AUTOMATIC LIBRARY INSTALLATION ---
try:
    import pyautogui
except ImportError:
    print("[Bridge] 'pyautogui' library is missing. Installing it automatically...")
    try:
        subprocess.run([sys.executable, "-m", "pip", "install", "pyautogui", "--quiet"])
        import pyautogui
        print("[Bridge] 'pyautogui' installed successfully!")
    except Exception as e:
        print(f"[Bridge] Warning: Could not auto-install pyautogui: {e}")

try:
    from PIL import ImageGrab
except ImportError:
    print("[Bridge] 'pillow' library is missing. Installing it automatically...")
    try:
        subprocess.run([sys.executable, "-m", "pip", "install", "pillow", "--quiet"])
        from PIL import ImageGrab
        print("[Bridge] 'pillow' installed successfully!")
    except Exception as e:
        print(f"[Bridge] Warning: Could not auto-install pillow: {e}")

# Fail-safe security: If anything goes wrong, slamming the mouse to any corner of the screen aborts execution
pyautogui.FAILSAFE = True
# --------------------------------------

# Helper to capture screen to Base64
def capture_screenshot_b64():
    screenshot = ImageGrab.grab()
    buffer = io.BytesIO()
    screenshot.save(buffer, format="PNG")
    img_str = base64.b64encode(buffer.getvalue()).decode("utf-8")
    return img_str

async def handle_connection(websocket):
    print("\n[Bridge] Browser connected.")
    try:
        async for message in websocket:
            data = json.loads(message)
            command = data.get("command", "").strip()
            
            # 1. INTERCEPT SCREENSHOT TRIGGER
            if command == "[SCREENSHOT]":
                print("\n[Bridge] Executing Screenshot Capture...")
                try:
                    img_b64 = capture_screenshot_b64()
                    await websocket.send(json.dumps({
                        "status": "screenshot",
                        "image": img_b64
                    }))
                    print("[Bridge] Screenshot sent successfully.")
                except Exception as e:
                    print(f"[Bridge Error] Screenshot failed: {e}")
                    await websocket.send(json.dumps({
                        "status": "error",
                        "output": f"Failed to take screenshot: {e}"
                    }))
                continue
            
            # 2. INTERCEPT PRECISE MOUSE TRIGGER
            if command.startswith("[MOUSE]"):
                print(f"\n[Bridge] Executing Mouse Control: {command}")
                try:
                    parts = command.replace("[MOUSE]", "").strip().split()
                    action = parts[0].lower() if len(parts) > 0 else "position"
                    
                    output = ""
                    if action == "position":
                        x, y = pyautogui.position()
                        output = f"Mouse Position: x={x}, y={y}"
                        
                    elif action == "move":
                        x, y = int(parts[1]), int(parts[2])
                        duration = float(parts[3]) if len(parts) > 3 else 0.2
                        pyautogui.moveTo(x, y, duration=duration)
                        output = f"Moved mouse to x={x}, y={y}"
                        
                    elif action == "click":
                        x, y = int(parts[1]), int(parts[2])
                        button = parts[3].lower() if len(parts) > 3 else "left"
                        clicks = int(parts[4]) if len(parts) > 4 else 1
                        pyautogui.click(x, y, button=button, clicks=clicks)
                        output = f"Clicked mouse at x={x}, y={y}"
                        
                    elif action == "drag":
                        x, y = int(parts[1]), int(parts[2])
                        duration = float(parts[3]) if len(parts) > 3 else 0.5
                        pyautogui.dragTo(x, y, duration=duration)
                        output = f"Dragged mouse to x={x}, y={y}"
                        
                    elif action == "scroll":
                        amount = int(parts[1])
                        pyautogui.scroll(amount)
                        output = f"Scrolled mouse by {amount}"
                        
                    else:
                        output = f"Unknown mouse action: {action}"
                        
                    await websocket.send(json.dumps({
                        "status": "success",
                        "output": output
                    }))
                    print(f"[Bridge] {output}")
                except Exception as e:
                    print(f"[Bridge Error] Mouse action failed: {e}")
                    await websocket.send(json.dumps({
                        "status": "error",
                        "output": f"Mouse action failed: {e}"
                    }))
                continue
            
            # 3. STABLE CMD BACKEND (Bypasses PowerShell registry completely)
            print(f"\n[Executing Command in CMD]:\n{command}")
            try:
                result = subprocess.run(
                    command,
                    shell=True,
                    capture_output=True, 
                    text=True, 
                    timeout=30
                )
                output = f"STDOUT:\n{result.stdout}\nSTDERR:\n{result.stderr}"
                status = "success"
            except subprocess.TimeoutExpired:
                output = "Error: Execution timed out after 30 seconds."
                status = "error"
            except Exception as e:
                output = f"Error: {str(e)}"
                status = "error"
                
            print(f"[System Output]:\n{output}")
            
            # Send the output back to the browser
            await websocket.send(json.dumps({
                "status": status,
                "output": output
            }))
            
    except websockets.exceptions.ConnectionClosedOK:
        print("[Bridge] Browser disconnected.")
    except Exception as e:
        print(f"[Bridge Error]: {e}")

async def main():
    print("Starting Automated CMD Terminal Bridge on ws://localhost:8766 ...")
    async with websockets.serve(handle_connection, "localhost", 8766):
        await asyncio.Future()  # Keep running indefinitely

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\nServer stopped.")