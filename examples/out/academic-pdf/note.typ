#set document(title: [State the result in the title], author: ("Ke Lin"))
#set page(
  paper: "a4",
  margin: (top: 22mm, bottom: 22mm, left: 24mm, right: 24mm),
  header: context {
    if counter(page).get().first() > 1 {
      text(size: 9pt, fill: rgb("#4A4A4A"), font: ("Liberation Sans", "Noto Sans CJK SC"))[
        Exhibit titles
        #h(1fr)
        Discussion note. Not peer reviewed.
      ]
    }
  },
  footer: context {
    align(center, text(size: 9pt, fill: rgb("#4A4A4A"))[
      #counter(page).display("1")
    ])
  },
)
#set text(font: ("Liberation Serif", "Noto Serif CJK SC"), size: 11pt, lang: "en", region: "US", fill: rgb("#1A1A1A"))
#set par(justify: true, leading: 0.78em, spacing: 0.72em, first-line-indent: 0.0em)
#set heading(numbering: "1.1")
#show heading.where(level: 1): it => {
  set text(font: ("Liberation Sans", "Liberation Sans"), size: 13pt, fill: rgb("#1A1A1A"))
  set par(first-line-indent: 0em)
  block(above: 1.35em, below: 0.55em, it)
}
#show heading.where(level: 2): it => {
  set text(font: ("Liberation Sans", "Liberation Sans"), size: 11pt)
  set par(first-line-indent: 0em)
  block(above: 1.1em, below: 0.4em, it)
}

#set par(first-line-indent: 0em)

#text(size: 9pt, fill: rgb("#4A4A4A"), font: ("Liberation Sans", "Noto Sans CJK SC"))[Discussion note. Not peer reviewed.]

#text(size: 20pt, weight: "bold")[State the result in the title]

#text(size: 12pt, fill: rgb("#4A4A4A"))[A discussion note on exhibit sentences]

#text(size: 10.5pt)[Ke Lin, Independent  ·  November 2026]

#v(0.9em)
#text(weight: "bold")[Abstract] #h(0.6em) An exhibit title that names the topic leaves the reader to invent the sentence. A title that states the comparison can be checked against the picture. This note argues for the second habit and does not report an experiment.

#text(size: 10.5pt, fill: rgb("#4A4A4A"))[Keywords  exhibits; graphical perception; titles]

#v(0.2em)
#set par(first-line-indent: 0.0em)
#heading(level: 1, numbering: "1.1")[The claim]
A chart titled “Regional costs” tells the reader where to look and not what was found. A chart titled “Overlap zones cost more per stop than hub zones” makes a claim the picture can support or embarrass. The second title is harder to write, which is the reason to prefer it. The title is part of the evidence, not a label beside it.
This is a writing claim. It is not a finding about memory, and it is not attributed to a laboratory. The only empirical work cited below is about how people decode graphics, not about how they remember sentences.
#heading(level: 1, numbering: "1.1")[What the sentence is doing]
A topic title and a claim title do different jobs. The first names the slice of the world. The second names the comparison and, usually, its direction. Once the direction is in the title, a reader can ask a narrow question: does the picture show that direction, in that unit, for those categories?
#figure(
  caption: [Two titles for the same picture.],
  table(
    columns: (1fr, 1fr),
    stroke: none,
    inset: (x: 7pt, y: 5pt),
    align: (left, right),
    [* Title *],
  [* What the reader must supply *],
  table.hline(stroke: 0.8pt),
  [Regional costs],
  [Which regions, which direction, which unit],
  table.hline(stroke: 0.3pt + rgb("#CCCCCC")),
  [Overlap zones cost more per stop],
  [Whether the bars agree],
  ),
)
The second row is still not a proof. It is a sentence with a truth value. That is the property worth buying. A title with no truth value cannot be wrong, and a title that cannot be wrong is not doing analytical work.
#heading(level: 1, numbering: "1.1")[What to encode]
Cleveland and McGill ordered elementary perceptual tasks by how accurately people extract quantitative information. Position along a common scale sits at the top of that order; area, volume, and color saturation sit lower (Cleveland and McGill, 1984). For a comparison of a few categories, a bar or a dot on a shared axis is the encoding that matches the task. A pie asks the reader to compare angles or areas for a job that was a comparison of lengths.
Tufte’s discussion of graphical integrity and of data-ink is the other standing reference for this habit: the picture should show the data, and the labels should say what the data are, in the unit the data were measured in (Tufte, 2001). Neither citation is a license to put an invented number under a careful title. A precise title on an illustrative series still has to say that the series is illustrative.
#heading(level: 1, numbering: "1.1")[A worked exhibit]
Suppose four fulfillment zones and a cost per stop. The numbers below are a sketch, chosen so the comparison is obvious, and they are not measurements.
#figure(
  caption: [Illustrative cost per stop, yuan. Not a measurement.],
  table(
    columns: (1fr, 1fr, 1fr),
    stroke: none,
    inset: (x: 7pt, y: 5pt),
    align: (left, right, left),
    [* Zone *],
  [* Yuan per stop *],
  [* Read as *],
  table.hline(stroke: 0.8pt),
  [Hub-served],
  [6.4],
  [Baseline],
  table.hline(stroke: 0.3pt + rgb("#CCCCCC")),
  [Single coverage],
  [7.1],
  [Close to the hub],
  table.hline(stroke: 0.3pt + rgb("#CCCCCC")),
  [Overlap],
  [9.8],
  [The claim],
  table.hline(stroke: 0.3pt + rgb("#CCCCCC")),
  [Remote],
  [11.2],
  [A different problem],
  ),
)
The honest title is “Overlap costs more per stop than hub-served zones in this sketch.” The title “Cost by zone” would also fit a page on which the remote zone was cheapest. That is the test: if the title would survive a reversal of the data, it is not yet a result.
#heading(level: 1, numbering: "1.1")[What this note does not show]
There is no sample of readers, no response time, and no test of memory. Cleveland and McGill studied decoding of quantities, not recall of titles. Nothing here measures whether a claim title changes what a person remembers a week later. A study of that question would need a design this note does not have.
The note also does not say that every heading in a paper should be a finding. A methods section can be titled “Methods.” The pressure applies where a picture is being asked to carry an argument: the title of that picture, and the title of the slide or the subsection that exists only to present it.
#set enum(numbering: "1.", indent: 0.5em, body-indent: 0.4em)
+ No new dataset was collected.
+ No DOI is attached, because none was re-checked for this note.
+ The yuan figures in the table are illustrative and labeled as such.
#heading(level: 1, numbering: none)[References]
#set par(first-line-indent: 0em, hanging-indent: 1.1em, spacing: 0.55em)
#block(below: 0.45em)[Cleveland, W. S., and McGill, R. (1984). Graphical perception: Theory, experimentation, and application to the development of graphical methods. Journal of the American Statistical Association, 79(387), 531–554.]
#block(below: 0.45em)[Tufte, E. R. (2001). The Visual Display of Quantitative Information (2nd ed.). Cheshire, CT: Graphics Press.]
