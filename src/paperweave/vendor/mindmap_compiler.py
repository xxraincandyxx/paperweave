"""Adapted from Dicklesworthstone/mindmap-generator, commit 4b835da.
README declares MIT. Based on _generate_mermaid_mindmap / _add_node_to_mindmap.
Changes: stable node IDs, no emoji API, safe labels, arbitrary children, no duplicate leaves.
"""
import re

def safe_label(text):
    # Plain Unicode letters and numbers survive. Mermaid structural punctuation cannot enter grammar.
    text=re.sub(r'[^\w\s\u4e00-\u9fff.,，。:：;%％+−=/\-]', ' ', str(text), flags=re.UNICODE)
    return re.sub(r'\s+',' ',text).strip()[:70] or '节点'


def generate_mindmap(tree):
    lines=['mindmap']
    def add(node,depth):
        nid=re.sub(r'[^A-Za-z0-9_]','',node['id'])
        label=safe_label(node['label'])
        shape=f'{nid}(("{label}"))' if depth==1 else f'{nid}["{label}"]'
        lines.append('    '*depth+shape)
        for child in node.get('children',[]):
            add(child,depth+1)
    add(tree,1)
    return '\n'.join(lines)


def generate_flowchart(tree):
    lines=['flowchart LR']
    def add(node):
        lines.append(f'{node["id"]}["{safe_label(node["label"])}"]')
        for child in node.get('children',[]):
            add(child); lines.append(f'{node["id"]} --> {child["id"]}')
    add(tree)
    return '\n'.join(lines)
