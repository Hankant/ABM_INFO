"""Draw the single-event study framework as matching editable SVG and PNG.

This is a local illustration tool only. It makes no network or model calls.
Requires Pillow; uses a locally installed Chinese font. Run from any directory.
"""
from __future__ import annotations

import math
from pathlib import Path
from xml.sax.saxutils import escape

from PIL import Image, ImageDraw, ImageFont


ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "deliverables" / "single_event"
W, H, SCALE = 2400, 1810, 2
FONT_REGULAR = Path("C:/Windows/Fonts/msyh.ttc")
FONT_BOLD = Path("C:/Windows/Fonts/msyhbd.ttc")

INK = "#173344"
MUTED = "#526773"
LINE = "#CAD6DC"
BLUE = "#26739D"
TEAL = "#248979"
RED = "#BF6255"
GOLD = "#B68A35"


class Canvas:
    """A small common drawing surface keeps the raster and vector identical."""

    def __init__(self):
        self.image = Image.new("RGB", (W * SCALE, H * SCALE), "white")
        self.draw = ImageDraw.Draw(self.image)
        self.svg = [
            f'<svg xmlns="http://www.w3.org/2000/svg" width="{W}" height="{H}" viewBox="0 0 {W} {H}">',
            '<title>单事件LLM社交传播模型框架</title>',
            '<desc>左侧为实验社交网络及默认圈内定向示意，右侧为真实事件输入与行为特征提取、初始化、逐轮信息浏览与模型决策、政府干预及结果统计。</desc>',
            '<rect width="100%" height="100%" fill="white"/>',
        ]
        self.fonts = {}

    def _font(self, size, bold=False):
        key = size, bold
        if key not in self.fonts:
            path = FONT_BOLD if bold else FONT_REGULAR
            self.fonts[key] = ImageFont.truetype(str(path), int(size * SCALE))
        return self.fonts[key]

    def rect(self, box, fill="white", stroke=LINE, radius=18, width=2):
        x, y, right, bottom = box
        points = [round(v * SCALE) for v in box]
        self.draw.rounded_rectangle(points, radius=radius * SCALE, fill=fill,
                                    outline=stroke, width=width * SCALE)
        self.svg.append(f'<rect x="{x}" y="{y}" width="{right-x}" height="{bottom-y}" rx="{radius}" fill="{fill}" stroke="{stroke}" stroke-width="{width}"/>')

    def ellipse(self, box, fill, stroke, width=2):
        x, y, right, bottom = box
        self.draw.ellipse([round(v * SCALE) for v in box], fill=fill,
                          outline=stroke, width=width * SCALE)
        self.svg.append(f'<ellipse cx="{(x+right)/2}" cy="{(y+bottom)/2}" rx="{(right-x)/2}" ry="{(bottom-y)/2}" fill="{fill}" stroke="{stroke}" stroke-width="{width}"/>')

    def circle(self, x, y, r, fill, stroke, width=2):
        self.ellipse((x-r, y-r, x+r, y+r), fill, stroke, width)

    def text(self, x, y, label, size=28, color=INK, bold=False, anchor="left"):
        font = self._font(size, bold)
        measured = self.draw.textlength(label, font=font) / SCALE
        px = x if anchor == "left" else x - measured / (2 if anchor == "center" else 1)
        self.draw.text((round(px*SCALE), round(y*SCALE)), label, font=font, fill=color, anchor="lt")
        svg_anchor = {"left": "start", "center": "middle", "right": "end"}[anchor]
        weight = 700 if bold else 400
        self.svg.append(f'<text x="{x}" y="{y}" font-family="Microsoft YaHei, Noto Sans CJK SC, sans-serif" font-size="{size}" font-weight="{weight}" fill="{color}" text-anchor="{svg_anchor}" dominant-baseline="text-before-edge">{escape(label)}</text>')

    def lines(self, x, y, labels, size=28, gap=42, color=INK, bold=False, anchor="left"):
        for i, label in enumerate(labels):
            self.text(x, y+i*gap, label, size, color, bold, anchor)

    def line(self, points, color=LINE, width=3, dashed=False):
        coords = [(round(x*SCALE), round(y*SCALE)) for x, y in points]
        if dashed:
            for (x1, y1), (x2, y2) in zip(points, points[1:]):
                distance = math.hypot(x2-x1, y2-y1)
                for offset in range(0, math.ceil(distance), 16):
                    a, b = offset/distance, min(offset+9, distance)/distance
                    self.draw.line([(round((x1+(x2-x1)*a)*SCALE), round((y1+(y2-y1)*a)*SCALE)),
                                    (round((x1+(x2-x1)*b)*SCALE), round((y1+(y2-y1)*b)*SCALE))],
                                   fill=color, width=width*SCALE)
        else:
            self.draw.line(coords, fill=color, width=width*SCALE, joint="curve")
        values = " ".join(f"{x},{y}" for x, y in points)
        dash = ' stroke-dasharray="9 7"' if dashed else ""
        self.svg.append(f'<polyline points="{values}" fill="none" stroke="{color}" stroke-width="{width}" stroke-linejoin="round"{dash}/>')

    def arrow(self, points, color=BLUE, width=4, dashed=False, head=13):
        self.line(points, color, width, dashed)
        x, y = points[-1]
        px, py = points[-2]
        angle = math.atan2(y-py, x-px)
        vertices = [(x, y),
                    (x-head*math.cos(angle)+head*.52*math.sin(angle),
                     y-head*math.sin(angle)-head*.52*math.cos(angle)),
                    (x-head*math.cos(angle)-head*.52*math.sin(angle),
                     y-head*math.sin(angle)+head*.52*math.cos(angle))]
        self.draw.polygon([(round(a*SCALE), round(b*SCALE)) for a, b in vertices], fill=color)
        self.svg.append('<polygon points="' + ' '.join(f'{a:.2f},{b:.2f}' for a, b in vertices) + f'" fill="{color}"/>')

    def user(self, x, y, color, selected=False):
        if selected:
            self.circle(x, y, 27, "#FFF9F7", RED, 3)
        self.circle(x, y, 20, "white", color, 3)
        self.circle(x, y-5, 5, color, color, 1)
        self.ellipse((x-10, y+3, x+10, y+13), color, color, 1)

    def step(self, box, number, title, body, color=BLUE, fill="#F7FAFC", size=27, gap=40):
        self.rect(box, fill, "#C9DCE6")
        x, y, _, _ = box
        self.circle(x+39, y+39, 20, color, color, 1)
        self.text(x+39, y+23, str(number), 27, "white", True, "center")
        self.text(x+77, y+22, title, 31, color, True)
        self.lines(x+32, y+77, body, size=size, gap=gap)

    def save(self):
        OUT.mkdir(parents=True, exist_ok=True)
        self.image.save(OUT / "模型流程图.png", dpi=(300, 300), optimize=True)
        (OUT / "模型流程图.svg").write_text("\n".join(self.svg + ["</svg>"]), encoding="utf-8")


def main():
    c = Canvas()
    c.text(65, 47, "单事件 LLM 社交传播模型", 55, INK, True)
    c.text(67, 124, "真实事件行为特征提取  ·  582 名独立 Agent  ·  政府纠正干预  ·  80 轮同步演化", 28, MUTED)

    c.rect((60, 205, 775, 1640), "#FFFFFF", LINE, 24)
    c.rect((815, 205, 2340, 1640), "#FFFFFF", LINE, 24)
    c.text(95, 232, "A  实体与实验网络", 35, INK, True)
    c.text(850, 232, "B  一个事件的时间流程", 35, INK, True)

    # A: illustrative nodes; the actual experiment has 82 + 500 separate agents.
    c.ellipse((91, 465, 360, 777), "#F0F6FA", "#D1E2EC")
    c.ellipse((452, 465, 739, 777), "#EFF8F5", "#CAE4DC")
    c.text(225, 414, "圈内用户", 31, BLUE, True, "center")
    c.text(595, 414, "圈外用户", 31, TEAL, True, "center")
    inside = [(143, 547), (240, 502), (313, 576), (274, 689), (153, 692), (222, 600)]
    outside = [(532, 506), (647, 529), (707, 615), (644, 708), (518, 692), (588, 604)]
    for nodes in (inside, outside):
        for a, b in ((0, 1), (0, 4), (1, 2), (1, 5), (2, 3), (2, 5), (3, 4), (3, 5), (4, 5), (0, 5)):
            c.line([nodes[a], nodes[b]], "#CDDAE0", 2)
    for a, b in ((1, 0), (2, 5), (3, 4)):
        c.line([inside[a], outside[b]], "#DAE2E5", 2)
    c.arrow([(165, 544), (211, 514)], BLUE, 4)
    c.arrow([(329, 578), (557, 597)], TEAL, 4)
    c.arrow([(610, 607), (680, 614)], TEAL, 4)
    for i, (x, y) in enumerate(inside):
        c.user(x, y, BLUE, i == 3)
    for x, y in outside:
        c.user(x, y, TEAL)
    c.text(225, 802, "82 人", 32, BLUE, True, "center")
    c.text(595, 802, "500 人", 32, TEAL, True, "center")
    c.text(420, 560, "跨圈传播", 23, TEAL, False, "center")
    c.circle(412, 344, 31, "#FBF5E8", GOLD, 3)
    c.text(412, 323, "S", 34, GOLD, True, "center")
    c.text(463, 322, "事件源帖", 29, GOLD, True)
    c.arrow([(391, 369), (260, 480)], GOLD, 4)
    c.text(267, 363, "第 0 轮", 23, GOLD, False, "center")
    c.circle(411, 938, 31, "#FFF2EE", RED, 3)
    c.text(411, 917, "G", 34, RED, True, "center")
    c.text(461, 918, "政府纠正", 29, RED, True)
    c.arrow([(394, 911), (284, 716)], RED, 3, True)
    c.text(411, 989, "T_G 时一次投送：默认圈内 40 人", 25, RED, False, "center")
    c.text(411, 1025, "定向可选：圈内 / 随机 / 圈外", 24, RED, False, "center")

    c.line([(108, 1084), (145, 1084)], "#CDDAE0", 3)
    c.text(158, 1067, "关注关系", 23, MUTED)
    c.arrow([(306, 1084), (344, 1084)], TEAL, 3, head=10)
    c.text(355, 1067, "信息传播", 23, MUTED)
    c.circle(533, 1084, 11, "white", RED, 2)
    c.text(554, 1067, "直接接收者", 23, MUTED)
    c.text(107, 1110, "图中仅画部分用户；节点与边不是实测关系。", 24, MUTED)

    c.rect((95, 1150, 740, 1325), "#F8FAFB", "#E0E7EB", 16)
    c.text(120, 1176, "每人关注：8 名同圈 + 2 名跨圈用户", 29, INK, True)
    c.lines(120, 1224, ["圈内 / 圈外划分与关注边属于实验设定。", "信息沿关注关系传播，并有推荐曝光。"], 25, 42, MUTED)

    c.rect((95, 1355, 740, 1587), "#F8FAFB", "#E0E7EB", 16)
    c.text(120, 1381, "独立主体，不共享内心状态", 30, INK, True)
    c.lines(120, 1436, ["每人各自维护信念、记忆与互动记录。", "他人观点仅通过亲眼可见的公开表达进入。", "历史评论内容不预装为初始立场。"], 25, 44, MUTED)

    # B: chronological main path; the intervention and recurrence stay separate.
    left, right, mid = 855, 1805, 1330
    c.step((left, 300, right, 507), 1, "真实事件输入与行为画像", [
        "事件源帖 + 250 条评论 + 72 条非空转发",
        "画像：公开计数；逐人发言 / 转发 / 长度 / 问句统计",
        "行为统计仅作参考，不拟合参数；不训练、不预装立场。"], size=26, gap=41)
    c.arrow([(mid, 507), (mid, 542)], BLUE)
    c.step((left, 542, right, 657), 2, "初始化 582 人与实验网络", [
        "82 人圈内 + 500 人圈外；每人 8 同圈关注 + 2 跨圈关注"], size=26)
    c.arrow([(mid, 657), (mid, 692)], BLUE)
    c.rect((left, 692, right, 762), "#FBF7ED", "#E5D8B9", 16)
    c.text(mid, 708, "第 0 轮：事件源帖进入网络", 31, GOLD, True, "center")
    c.arrow([(mid, 762), (mid, 807)], BLUE)

    c.step((left, 807, right, 981), 3, "每轮 t：浏览信息与接收政府直投", [
        "活跃浏览：关注流 / 推荐 + 至多 2 条评论、1 条转发",
        "槽位内优先读取自己帖的回复。",
        "政府直投额外到达：接收者不活跃也读取。"], size=24, gap=31)
    c.arrow([(mid, 981), (mid, 1016)], BLUE)
    c.step((left, 1016, right, 1195), 4, "LLM 独立判断与行动", [
        "当前内容 + 可见的他人表达 + 个人画像 + 最近记忆",
        "输出信念分 0–100，并选择：沉默 / 评论 / 转发"], size=27, gap=42)
    c.arrow([(mid, 1195), (mid, 1230)], BLUE)
    c.step((left, 1230, right, 1358), 5, "同步提交，本轮新帖下一轮可见", [
        "保留传播链；沿圈内及跨圈关注关系继续扩散。"], color=TEAL, fill="#F2F9F6", size=27)

    c.rect((1870, 577, 2300, 974), "#FFF7F4", "#E6C8C0", 18)
    c.text(1898, 602, "政府纠正：一次外部干预", 28, RED, True)
    c.lines(1898, 656, ["T_G = 20（默认）", "可选 10 / 20 / 30 / 40 / 50", "一次 40 人；默认圈内", "定向另可选：随机 / 圈外", "GT = 0.6（默认）"], 25, 43)
    c.line([(1898, 869), (2272, 869)], "#E6C8C0", 2)
    c.lines(1898, 890, ["后续由用户转发扩散，", "与原话题信息并存。"], 25, 39, RED)
    c.arrow([(1870, 889), (right, 889)], RED, 4)

    c.arrow([(right, 1294), (1838, 1294), (1838, 951), (right, 951)], TEAL, 4)
    c.rect((1870, 1075, 2300, 1288), "#F3F9F6", "#CCE2D9", 18)
    c.text(1898, 1103, "下一轮传播反馈", 29, TEAL, True)
    c.lines(1898, 1159, ["t < 80：重复浏览与决策", "形成圈内 / 跨圈互动链。"], 26, 46, TEAL)

    c.arrow([(mid, 1358), (mid, 1418)], BLUE)
    c.text(mid+27, 1368, "t = 80", 24, MUTED)
    c.step((left, 1418, 2300, 1599), 6, "80 轮终点：状态、传播与转变时间", [
        "四种状态曲线：未接触 / 接受 / 不确定 / 拒绝；圈内外对比与传播链",
        "TBU：T_G 前为 accept → 首次 reject；30 轮内未转变者按右删失记录。"], color=INK, fill="#F4F7F9", size=28, gap=45)

    c.line([(65, 1681), (2335, 1681)], "#D7E0E5", 2)
    c.text(66, 1710, "说明：政府纠正使用实验澄清文本，无实证官方证据；离线 Mock 仅检验流程，不构成真实 LLM 研究结果。", 28, MUTED)
    c.text(66, 1754, "状态依据对原始主张的信念评分；发言行为与内心信念分开记录。", 25, MUTED)
    c.save()
    print(OUT / "模型流程图.png")
    print(OUT / "模型流程图.svg")


if __name__ == "__main__":
    main()
