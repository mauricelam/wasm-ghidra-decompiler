import os
import time
from playwright.sync_api import sync_playwright

def run():
    video_dir = os.environ.get("RECORD_VIDEO_DIR", "verification/videos")
    screenshot_dir = os.environ.get("SCREENSHOT_DIR", "verification/screenshots")
    os.makedirs(video_dir, exist_ok=True)
    os.makedirs(screenshot_dir, exist_ok=True)
    screenshot_path = os.path.join(screenshot_dir, "wasm_libcodec2.png")

    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        context = browser.new_context(
            record_video_dir=video_dir
        )
        page = context.new_page()

        try:
            print("1. Navigating to example_wasm.html...")
            page.goto("http://localhost:8000/wasm_examples/example_wasm.html")
            page.wait_for_timeout(1000)

            # Wait for WASM module initialization
            print("2. Waiting for WASM module ready status...")
            page.wait_for_selector("#output:has-text('Module ready')", timeout=15000)
            page.wait_for_timeout(500)

            print("3. Selecting ARM v7 architecture...")
            # Select ARM:LE:32:v7 from dropdown
            select_elem = page.locator("#processorSelect")
            options = select_elem.locator("option").all()
            target_value = None
            for opt in options:
                text = opt.inner_text()
                if "Generic ARM/Thumb v7 little endian" in text and "default" not in text:
                    target_value = opt.get_attribute("value")
                    break

            if target_value is None:
                raise Exception("Could not find ARM v7 option in processor list")

            select_elem.select_option(target_value)
            page.wait_for_timeout(500)

            print("4. Attaching binary testdata/libcodec2.so...")
            bin_path = os.path.abspath("testdata/libcodec2.so")
            page.set_input_files("#binInput", bin_path)
            page.wait_for_timeout(500)

            print("5. Setting base address and function address...")
            page.fill("#baseAddr", "0x1000")
            page.wait_for_timeout(500)
            page.fill("#funcName", "0x1250")
            page.wait_for_timeout(500)

            print("6. Clicking Run Decompiler...")
            page.click("#decompileBtn")
            page.wait_for_timeout(1000)

            print("7. Checking output status...")
            # Wait up to 15 seconds for output to change from Calling WASM decompiler...
            for _ in range(30):
                text = page.inner_text("#output")
                if "Calling WASM decompiler..." not in text:
                    break
                time.sleep(0.5)

            output_text = page.inner_text("#output")
            print("Current Output:")
            print(output_text)

            page.screenshot(path=screenshot_path)
            print(f"Screenshot saved to {screenshot_path}")

            if "void 0x1250(void)" in output_text or "func_0x00001250" in output_text:
                print("WASM Decompilation test passed!")
            else:
                raise Exception("Decompilation did not succeed as expected")

        finally:
            context.close()
            browser.close()

if __name__ == "__main__":
    run()
