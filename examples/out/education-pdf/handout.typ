#set document(title: [比例尺], author: (""))
#set page(
  paper: "a4",
  margin: (top: 18mm, bottom: 18mm, left: 18mm, right: 18mm),
  header: context {
    if counter(page).get().first() > 1 {
      text(size: 9pt, fill: rgb("#5C6770"), font: ("Liberation Sans", "Noto Sans CJK SC"))[
        比例尺
        #h(1fr)
        教学示例 · 临湾市临江中学数学组（虚构） · 2026年11月
      ]
    }
  },
  footer: context {
    align(center, text(size: 9pt, fill: rgb("#5C6770"))[
      #counter(page).display("1")
    ])
  },
)
#set text(font: ("Noto Serif CJK SC", "Liberation Serif"), size: 12pt, lang: "zh", region: "CN", fill: rgb("#1C2430"))
#set par(justify: false, leading: 0.78em, spacing: 0.72em, first-line-indent: 2.0em)
#set heading(numbering: none)
#show heading.where(level: 1): it => {
  set text(font: ("Noto Sans CJK SC", "Liberation Sans"), size: 16pt, fill: rgb("#1C2430"))
  set par(first-line-indent: 0em)
  block(above: 1.35em, below: 0.55em, it)
}
#show heading.where(level: 2): it => {
  set text(font: ("Noto Sans CJK SC", "Liberation Sans"), size: 14pt)
  set par(first-line-indent: 0em)
  block(above: 1.1em, below: 0.4em, it)
}

#set par(first-line-indent: 0em)

#text(size: 9pt, fill: rgb("#5C6770"), font: ("Liberation Sans", "Noto Sans CJK SC"))[教学示例 · 临湾市临江中学数学组（虚构） · 2026年11月]

#text(size: 20pt, weight: "bold")[比例尺]

#text(size: 12pt, fill: rgb("#5C6770"))[七年级数学学习单]

#text(size: 10.5pt)[2026年11月]

#text(size: 10.5pt, fill: rgb("#5C6770"))[关键词  比例尺；单位换算]

#v(0.2em)
#set par(first-line-indent: 2.0em)
#heading(level: 1, numbering: none)[这一节要会的两件事]
第一，把图上距离换成实地距离。第二，把实地距离换成图上距离。两件事都先统一单位，再乘或除。比例尺 1:50000 的意思是：图上 1 厘米对应实地 50000 厘米。
#heading(level: 1, numbering: none)[先看完一个例子]
比例尺 1:50000，图上距离 3.6 厘米，求实地距离。
$ 3.6 times 50000 = 180000 $
180000 的单位仍是厘米。100 厘米为 1 米，所以实地 1800 米，也就是 1.8 千米。先乘比例尺的后项，再换单位。不要先把 3.6 厘米改成米再去乘 50000。
#heading(level: 1, numbering: none)[练习]
#set enum(numbering: "1.", indent: 0.5em, body-indent: 0.4em)
+ 比例尺 1:20000，图上 4.5 厘米。实地是多少千米？
+ 比例尺 1:100000，实地 2.4 千米。图上是多少厘米？
+ 图上 5 厘米代表实地 2 千米。比例尺是多少？
每题写出单位换算。只写最后的数字不算完成。
#heading(level: 1, numbering: none)[容易错的一步]
千米和厘米之间差五个零：1 千米 = 1000 米 = 100000 厘米。第二题如果把 2.4 千米当成 2.4 厘米去除，会得到一个小得离谱的数。先写成 240000 厘米，再除以 100000。
#figure(
  caption: [这三题用到的换算。],
  table(
    columns: (1fr, 1fr),
    stroke: none,
    inset: (x: 7pt, y: 5pt),
    align: (left, right),
    [* 关系 *],
  [* 数值 *],
  table.hline(stroke: 0.8pt),
  [1 米],
  [100 厘米],
  table.hline(stroke: 0.3pt + rgb("#D5D8DC")),
  [1 千米],
  [100000 厘米],
  table.hline(stroke: 0.3pt + rgb("#D5D8DC")),
  [1:50000 的 1 厘米],
  [实地 500 米],
  ),
)
#pagebreak()
#heading(level: 1, numbering: none)[参考答案]
1. 4.5 × 20000 = 90000 厘米 = 900 米 = 0.9 千米。
2. 2.4 千米 = 240000 厘米。240000 ÷ 100000 = 2.4 厘米。
3. 2 千米 = 200000 厘米。图上 5 厘米对应 200000 厘米，比是 5:200000，化成 1:40000。
