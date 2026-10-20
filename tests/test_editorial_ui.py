"""Regression checks for the editorial UI; no real model API is called."""
import json
from pathlib import Path
from urllib.parse import urlsplit
from playwright.sync_api import sync_playwright,expect
from paperweave.render import STATIC,ROOT,browser_launch


def test_upload_long_filename_and_recoverable_config_error():
    with sync_playwright() as p:
        browser=browser_launch(p)
        try:
            for width in (1440,390):
                page=browser.new_page(viewport={'width':width,'height':1000})
                errors=[];page.on('pageerror',lambda e:errors.append(str(e)))
                def route(req):
                    path=urlsplit(req.request.url).path
                    if path=='/':req.fulfill(path=str(STATIC/'index.html'),content_type='text/html')
                    elif path=='/assets/dashboard.css':req.fulfill(path=str(STATIC/'dashboard.css'),content_type='text/css')
                    elif path=='/api/config':req.abort()
                    elif path=='/api/jobs':req.fulfill(status=400,json={'detail':'请先配置模型参数后重试。'})
                    else:req.abort()
                page.route('https://paperweave.test/**',route)
                page.goto('https://paperweave.test/');page.wait_for_load_state('networkidle')
                expect(page.locator('#config')).to_contain_text('请确认本地服务')
                filename='含有非常长的中文标题和UnbrokenResearchIdentifier'*8+'.pdf'
                page.locator('#file').set_input_files({'name':filename,'mimeType':'application/pdf','buffer':b'%PDF-1.4\nfixture'})
                expect(page.locator('#filename')).to_have_text(filename)
                assert page.evaluate('document.documentElement.scrollWidth <= innerWidth+1')
                if width==390:
                    assert page.locator('#submit').bounding_box()['height']>=44
                    assert float(page.locator('#file').evaluate('e=>getComputedStyle(e).fontSize').replace('px',''))>=16
                page.locator('#submit').click()
                expect(page.locator('#status')).to_have_text('请先配置模型参数后重试。')
                expect(page.locator('#submit')).to_be_enabled()
                expect(page.locator('#upload-form')).to_have_attribute('aria-busy','false')
                assert not errors,errors
                page.close()
        finally:browser.close()


def test_reader_keyboard_filter_state_and_index_spacing():
    file=ROOT/'outputs/teaching-demo/dashboard.html'
    with sync_playwright() as p:
        browser=browser_launch(p)
        try:
            page=browser.new_page(viewport={'width':1440,'height':1000})
            page.context.set_offline(True)
            page.goto(file.resolve().as_uri());page.wait_for_load_state('networkidle')
            canvas=page.locator('#canvas');canvas.focus()
            before=page.locator('#diagram').get_attribute('style')
            page.keyboard.press('ArrowRight')
            assert page.locator('#diagram').get_attribute('style')!=before
            page.keyboard.press('0')
            button=page.locator('#diagram [data-paper-id="n0001"]').first
            expect(button).to_have_attribute('role','button')
            button.focus();page.keyboard.press('Enter')
            expect(page.locator('#detail-content h2')).to_contain_text('稳定来源')
            page.locator('#critical-filter').click()
            expect(page.locator('#critical-filter')).to_have_attribute('aria-pressed','true')
            expect(page.locator('#all-filter')).to_have_attribute('aria-pressed','false')
            page.locator('#all-filter').click()
            page.locator('#mode-flowchart').click()
            expect(page.locator('#render-state')).to_have_text('Mermaid 已校验',timeout=30000)
            expect(page.locator('#mode-flowchart')).to_have_attribute('aria-pressed','true')
            page.locator('#mode-mindmap').click()
            expect(page.locator('#render-state')).to_have_text('Mermaid 已校验',timeout=30000)
            footer=page.locator('.outline-foot').bounding_box()
            index=page.locator('#outline').bounding_box()
            assert index['y']+index['height']<=footer['y']+1
            page.locator('#theme').click()
            expect(page.locator('#render-state')).to_have_text('Mermaid 已校验',timeout=30000)
            page.screenshot(path=str(ROOT/'outputs/dark-preview.png'),full_page=True)
        finally:browser.close()
