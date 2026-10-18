import json
from pathlib import Path
from playwright.sync_api import sync_playwright,expect
from paperweave.render import browser_launch
from paperweave.config import ROOT

def test_offline_interactions_and_exports(tmp_path):
    file=ROOT/'outputs'/'teaching-demo'/'dashboard.html'
    assert file.is_file(),'先执行 python examples/build_demo.py'
    with sync_playwright() as p:
        browser=browser_launch(p)
        try:
            context=browser.new_context(viewport={'width':1550,'height':1080},accept_downloads=True)
            context.set_offline(True)
            page=context.new_page();errors=[];remote=[]
            page.on('pageerror',lambda e:errors.append(str(e)))
            page.on('request',lambda req:remote.append(req.url) if req.url.startswith(('https:','http:')) else None)
            page.goto(file.resolve().as_uri());page.wait_for_load_state('networkidle')
            expect(page.locator('#paper-title')).to_contain_text('Page-aware')
            expect(page.locator('#notice')).to_contain_text('非真实模型')
            assert page.locator('#diagram svg').count()==1
            expect(page.locator('.node-button')).to_have_count(11)
            page.locator('#search').fill('末页')
            expect(page.locator('.node-button')).to_have_count(1)
            page.locator('.node-button').click()
            expect(page.locator('#detail-content h2')).to_contain_text('末页')
            page.locator('.page-link').first.click()
            expect(page.locator('#source-dialog')).to_be_visible()
            expect(page.locator('#source-page')).to_contain_text('4')
            page.locator('#close-source').click();page.locator('#search').fill('')
            page.locator('#mode-flowchart').click()
            expect(page.locator('#render-state')).to_have_text('Mermaid 已校验',timeout=30000)
            assert page.locator('#diagram [data-paper-id]').count()>=11
            page.locator('#diagram [data-paper-id="n0001"]').first.click(force=True)
            expect(page.locator('#detail-content h2')).to_contain_text('稳定来源')
            page.locator('#theme').click()
            expect(page.locator('body')).to_have_attribute('data-theme','dark')
            expect(page.locator('#render-state')).to_have_text('Mermaid 已校验',timeout=30000)
            page.locator('#collapse').click()
            expect(page.locator('#render-state')).to_have_text('Mermaid 已校验',timeout=30000)
            page.locator('#expand').click()
            expect(page.locator('#render-state')).to_have_text('Mermaid 已校验',timeout=30000)
            for button in ('export-mmd','export-svg','export-json','download-html'):
                with page.expect_download() as download:page.locator('#'+button).click()
                assert download.value.suggested_filename
                if button=='download-html':download.value.save_as(tmp_path/'saved.html')
            saved=context.new_page();saved.goto((tmp_path/'saved.html').as_uri());saved.wait_for_load_state('networkidle')
            expect(saved.locator('#paper-title')).to_contain_text('Page-aware')
            assert saved.locator('#diagram svg').count()==1
            page.locator('#theme').click()
            expect(page.locator('#render-state')).to_have_text('Mermaid 已校验',timeout=30000)
            page.locator('#mode-mindmap').click()
            expect(page.locator('#render-state')).to_have_text('Mermaid 已校验',timeout=30000)
            page.screenshot(path=str(ROOT/'outputs'/'dashboard-preview.png'),full_page=True)
            assert not errors,errors
            assert not remote,remote
        finally:browser.close()


def test_mobile_and_native_mindmap_node_clicks():
    file=ROOT/'outputs'/'teaching-demo'/'dashboard.html'
    with sync_playwright() as p:
        browser=browser_launch(p)
        try:
            context=browser.new_context(viewport={'width':390,'height':844})
            context.set_offline(True)
            page=context.new_page();page.goto(file.resolve().as_uri());page.wait_for_load_state('networkidle')
            assert page.evaluate('document.documentElement.scrollWidth <= window.innerWidth+1')
            assert page.locator('#diagram [data-paper-id="n0001"]').count()>=1
            page.locator('#diagram [data-paper-id="n0001"]').first.dispatch_event('click')
            expect(page.locator('#detail-content h2')).to_contain_text('稳定来源')
            page.screenshot(path=str(ROOT/'outputs'/'mobile-preview.png'),full_page=True)
        finally:browser.close()
