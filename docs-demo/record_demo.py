"""演示兜底录制：登录→看板→违规→详情→复核→排名→培训。
输出: video/webm + 一系列 png 截图。
"""
import os, sys, time
from pathlib import Path
from playwright.sync_api import sync_playwright

OUT = Path(__file__).resolve().parent
VIDEO_DIR = OUT / "video"
SHOT_DIR = OUT / "screenshots"
VIDEO_DIR.mkdir(exist_ok=True)
SHOT_DIR.mkdir(exist_ok=True)

FRONTEND = "http://localhost:5173"

# 每页停留时间（秒），让视频更自然
DWELL = 5

def shot(page, name, full_page=False):
    path = SHOT_DIR / f"{name}.png"
    page.screenshot(path=str(path), full_page=full_page, type="png")
    print(f"  -> {path.name}")

def main():
    with sync_playwright() as p:
        browser = p.chromium.launch()
        ctx = browser.new_context(
            viewport={"width": 1440, "height": 900},
            record_video_dir=str(VIDEO_DIR),
            record_video_size={"width": 1440, "height": 900},
        )
        page = ctx.new_page()

        # 1. 登录页
        print("[1/7] 登录页")
        page.goto(f"{FRONTEND}/login")
        page.wait_for_load_state("networkidle")
        time.sleep(DWELL)
        shot(page, "01-login")

        # 2. 登录 admin
        print("[2/7] 登录 -> dashboard")
        page.fill('input[placeholder*="用户"]', "admin")
        page.fill('input[type="password"]', "admin123456")
        time.sleep(1)
        shot(page, "02-login-filled")
        page.locator('button', has_text="登 录").first.click()
        page.wait_for_url("**/dashboard", timeout=10000)
        page.wait_for_load_state("networkidle")
        time.sleep(DWELL)
        # 滚动一下让趋势图露出来
        page.mouse.wheel(0, 400)
        time.sleep(1)
        page.mouse.wheel(0, -400)
        time.sleep(1)
        shot(page, "03-dashboard")

        # 3. 违规列表
        print("[3/7] 违规列表")
        page.goto(f"{FRONTEND}/violations")
        page.wait_for_load_state("networkidle")
        time.sleep(DWELL)
        shot(page, "04-violations-list")

        # 4. 违规详情
        print("[4/7] 违规详情")
        page.locator('button', has_text="详情").first.click()
        page.wait_for_url("**/violations/**", timeout=10000)
        page.wait_for_load_state("networkidle")
        time.sleep(DWELL)
        shot(page, "05-violation-detail")

        # 5. 复核
        print("[5/7] 复核页")
        page.goto(f"{FRONTEND}/violations")
        page.wait_for_load_state("networkidle")
        time.sleep(1)
        page.locator('button', has_text="复核").first.click()
        page.wait_for_url("**/review/**", timeout=10000)
        page.wait_for_load_state("networkidle")
        time.sleep(DWELL)
        # 切换一下复核结果 radio 让操作可见
        page.locator('text=接受申述').click()
        time.sleep(1)
        page.locator('text=确认违规').click()
        time.sleep(1)
        shot(page, "06-review")

        # 6. 员工排名 (切到"全部"才能看到数据)
        print("[6/7] 员工排名")
        page.goto(f"{FRONTEND}/ranking")
        page.wait_for_load_state("networkidle")
        time.sleep(2)
        page.click('text=全部')
        time.sleep(DWELL)
        shot(page, "07-ranking")

        # 7. 培训素材
        print("[7/7] 培训素材")
        page.goto(f"{FRONTEND}/training")
        page.wait_for_load_state("networkidle")
        time.sleep(DWELL)
        shot(page, "08-training")

        # 收尾回到 dashboard
        page.goto(f"{FRONTEND}/dashboard")
        page.wait_for_load_state("networkidle")
        time.sleep(3)

        browser.close()

    # 找生成的 video 文件并改名
    videos = list(VIDEO_DIR.glob("*.webm"))
    if videos:
        v = videos[0]
        target = OUT / "demo-recording.webm"
        v.rename(target)
        print(f"\n视频已保存: {target}")
    else:
        print("\n未找到录制的视频文件")

if __name__ == "__main__":
    main()