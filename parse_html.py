import glob
import types
import os
from lxml import html
from lxml.html import Element, HTMLParser, tostring
from weasyprint import HTML


MUBU_DIR = 'mubu\\'
HTML_DIR = 'html\\'
PDF_DIR = 'pdf\\'

PRINT_CSS = '../css/print.css'
MUBU_CSS = '../css/mubu.css'

mubuList = []

level = 0
hLevel = 0
pLevel = 0

leading = ''
hLeading = ''
pLeading = ''

htmlFile = None

MUST_COLOR = True
MUST_BOLD = False
MUST_DIGITAL = True
MUST_STEM = False

DIGITALS = '零〇一二三四五六七八九十百壹贰叁肆伍陆柒捌玖拾佰0123456789'
STEMS = '甲乙丙丁戊己庚辛壬癸子丑寅卯辰巳午未申酉戌亥'

IGNORED_CLASSES = ['bullet', 'bullet-dot']
REMOVE_ATTRS = ['style', 'target', 'spellcheck', 'rel']


def parse(path: str):

    global level
    global leading
    global hLevel
    global hLeading
    global pLevel
    global pLeading

    level = 0
    hLevel = 1
    pLevel = 0

    leading = ''
    hLeading = ''
    pLeading = ''

    global htmlFile

    htmlPath = path.replace(MUBU_DIR, HTML_DIR)
    htmlFile = open(htmlPath, 'w', encoding='utf-8')
    htmlFile.write('<!DOCTYPE html>\n<html>\n<head>\n<meta charset="utf-8"/>\n')
    htmlFile.write(f'<link rel="stylesheet" href="{PRINT_CSS}" type="text/css"/>\n')
    htmlFile.write(f'<link rel="stylesheet" href="{MUBU_CSS}" type="text/css"/>\n')

    print('parse: ', path)
    parser = HTMLParser(encoding='utf-8')
    tree = html.parse(path, parser)
    root = tree.getroot()

    # /html/body
    body = root.find('body')
    if body is None:
        print('no "html/body" node.')
        return

    # /html/body/title
    titles = body.cssselect('div.title')
    if len(titles) == 0:
        print('no "/html/body/title" node.')
        return
    title = titles[0]

    print('title: ', title.text)
    htmlFile.write(f'<title>{title.text}</title>\n</head>\n<body>\n')

    # /html/body/ul
    ul = body.find('ul')
    if ul is None:
        print('no "/html/body/ul" node.')
        return

    # travelNode(ul)
    travelHead(ul)

    htmlFile.write('</body>\n</html>\n')
    htmlFile.close()


def travelNode(node: Element):
    global level
    global leading

    if node is None:
        return

    bindMethods(node)

    node.cleanBullet()
    node.cleanAttrs()

    print(leading, node.tag, node.attrib)

    level += 1
    leading += ' '
    childs = node.findall('*')
    for child in childs:
        travelNode(child)
    level -= 1
    leading = leading[:-1]


def travelHead(ul: Element):
    global hLevel
    global hLeading
    global pLevel
    global pLeading

    if ul is None:
        return

    lis = ul.findall('li')

    for li in lis:

        if li is None:
            continue

        contents = li.xpath('div[contains(@class, "content")]')
        if len(contents) == 0:
            continue
        content = contents[0]

        span = content.find('span')

        isHeading = checkHeading(li, span)

        if isHeading:
            print(f'{hLeading}<h{hLevel}>{inner(span)}</h{hLevel}>')
            htmlFile.write(f'{hLeading}<h{hLevel}>{inner(span)}</h{hLevel}>\n')

            notes = li.xpath('div[contains(@class, "note")]')
            if len(notes) > 0:
                note = notes[0]
                htmlFile.write(f'{hLeading}{inner(note)}\n')

            childrens = li.xpath('div[contains(@class, "children")]')
            if len(childrens) > 0:
                children = childrens[0]

                ul = children.find('ul')
                if ul:
                    hLevel += 1
                    hLeading += '  '
                    travelHead(ul)
                    hLevel -= 1
                    hLeading = hLeading[:-2]

        else:
            htmlFile.write(f'{hLeading}{inner(content)}\n')

            notes = li.xpath('div[contains(@class, "note")]')
            if len(notes) > 0:
                note = notes[0]

                htmlFile.write(f'{hLeading}{inner(note)}\n')

            childrens = li.xpath('div[contains(@class, "children")]')
            if len(childrens) > 0:
                children = childrens[0]

                htmlFile.write(f'{hLeading}{inner(children)}\n')


def inner(node: Element) -> str:
    if node is None:
        return ''

    return tostring(node, encoding='unicode')


def bindMethods(node: Element):
    node.cleanBullet = types.MethodType(cleanBullet, node)
    node.cleanAttrs = types.MethodType(cleanAttrs, node)


def cleanBullet(self: Element):
    bullet = self.find('div.bullet')

    if bullet:
        self.remove(bullet)


def cleanAttrs(self: Element):

    for attr in REMOVE_ATTRS:
        if attr in self.attrib:
            self.attrib.pop(attr)


def checkHeading(li: Element, span: Element) -> bool:

    if li is None:
        return False

    for attr in li.classes:
        if attr.startswith('heading'):
            return True

    hasColor = False
    hasBold = False
    hasDigital = False
    hasStem = False

    if span is None:
        return False

    if 'bold' in span.classes:
        hasBold = True

    for klass in span.classes:
        if klass.startswith('text-color'):
            hasColor = True

    if len(span.text) > 0 and span.text[0] in DIGITALS\
            or len(span.text) > 1 and span.text[1] in DIGITALS:
        hasDigital = True

    if len(span.text) > 0 and span.text[0] in STEMS:
        hasStem = True

    if MUST_COLOR and not hasColor\
            or MUST_BOLD and not hasBold\
            or MUST_DIGITAL and not hasDigital\
            or MUST_STEM and not hasStem:
        return False

    return True


def getMubuList():
    global mubuList

    mubuList = glob.glob(f'{MUBU_DIR}*.htm*')


def topdf(path):

    htmlPath = path.replace(MUBU_DIR, HTML_DIR)
    pdfPath = path.replace(MUBU_DIR, PDF_DIR)
    pdfPath = pdfPath.replace('.html', '.pdf')

    print('convert to: ', pdfPath)
    HTML(htmlPath).write_pdf(pdfPath)


def main():
    global htmlFile

    getMubuList()

    if not os.path.exists(HTML_DIR):
        os.makedirs(HTML_DIR, exist_ok=True)

    if not os.path.exists(PDF_DIR):
        os.makedirs(PDF_DIR, exist_ok=True)

    for mubu in mubuList:
        parse(mubu)
        topdf(mubu)

    print('done!')


if __name__ == "__main__":
    main()
