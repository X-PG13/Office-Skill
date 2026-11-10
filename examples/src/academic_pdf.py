FILENAME = "note.pdf"

PLAN = {
    "file_type": "pdf",
    "domain": "academic",
    "language": "en",
    "title": "State the result in the title",
    "subtitle": "A discussion note on exhibit sentences",
    "running_head": "Exhibit titles",
    "classification": "Discussion note. Not peer reviewed.",
    "authors": [{"name": "Ke Lin", "affiliation": "Independent"}],
    "date": "November 2026",
    "abstract": "An exhibit title that names the topic leaves the reader to invent the sentence. A title that states the comparison can be checked against the picture. This note argues for the second habit and does not report an experiment.",
    "keywords": ["exhibits", "graphical perception", "titles"],
    "sections": [
        {
            "heading": "The claim",
            "blocks": [
                {
                    "type": "paragraph",
                    "text": "A chart titled “Regional costs” tells the reader where to look and not what was found. A chart titled “Overlap zones cost more per stop than hub zones” makes a claim the picture can support or embarrass. The second title is harder to write, which is the reason to prefer it. The title is part of the evidence, not a label beside it.",
                },
                {
                    "type": "paragraph",
                    "text": "This is a writing claim. It is not a finding about memory, and it is not attributed to a laboratory. The only empirical work cited below is about how people decode graphics, not about how they remember sentences.",
                },
            ],
        },
        {
            "heading": "What the sentence is doing",
            "blocks": [
                {
                    "type": "paragraph",
                    "text": "A topic title and a claim title do different jobs. The first names the slice of the world. The second names the comparison and, usually, its direction. Once the direction is in the title, a reader can ask a narrow question: does the picture show that direction, in that unit, for those categories?",
                },
                {
                    "type": "table",
                    "caption": "Two titles for the same picture.",
                    "columns": ["Title", "What the reader must supply"],
                    "rows": [
                        ["Regional costs", "Which regions, which direction, which unit"],
                        ["Overlap zones cost more per stop", "Whether the bars agree"],
                    ],
                },
                {
                    "type": "paragraph",
                    "text": "The second row is still not a proof. It is a sentence with a truth value. That is the property worth buying. A title with no truth value cannot be wrong, and a title that cannot be wrong is not doing analytical work.",
                },
            ],
        },
        {
            "heading": "What to encode",
            "blocks": [
                {
                    "type": "paragraph",
                    "text": "Cleveland and McGill ordered elementary perceptual tasks by how accurately people extract quantitative information. Position along a common scale sits at the top of that order; area, volume, and color saturation sit lower [@cleveland1984]. For a comparison of a few categories, a bar or a dot on a shared axis is the encoding that matches the task. A pie asks the reader to compare angles or areas for a job that was a comparison of lengths.",
                },
                {
                    "type": "paragraph",
                    "text": "Tufte’s discussion of graphical integrity and of data-ink is the other standing reference for this habit: the picture should show the data, and the labels should say what the data are, in the unit the data were measured in [@tufte2001]. Neither citation is a license to put an invented number under a careful title. A precise title on an illustrative series still has to say that the series is illustrative.",
                },
            ],
        },
        {
            "heading": "A worked exhibit",
            "blocks": [
                {
                    "type": "paragraph",
                    "text": "Suppose four fulfillment zones and a cost per stop. The numbers below are a sketch, chosen so the comparison is obvious, and they are not measurements.",
                },
                {
                    "type": "table",
                    "caption": "Illustrative cost per stop, yuan. Not a measurement.",
                    "columns": ["Zone", "Yuan per stop", "Read as"],
                    "aligns": ["left", "right", "left"],
                    "rows": [
                        ["Hub-served", "6.4", "Baseline"],
                        ["Single coverage", "7.1", "Close to the hub"],
                        ["Overlap", "9.8", "The claim"],
                        ["Remote", "11.2", "A different problem"],
                    ],
                },
                {
                    "type": "paragraph",
                    "text": "The honest title is “Overlap costs more per stop than hub-served zones in this sketch.” The title “Cost by zone” would also fit a page on which the remote zone was cheapest. That is the test: if the title would survive a reversal of the data, it is not yet a result.",
                },
            ],
        },
        {
            "heading": "What this note does not show",
            "blocks": [
                {
                    "type": "paragraph",
                    "text": "There is no sample of readers, no response time, and no test of memory. Cleveland and McGill studied decoding of quantities, not recall of titles. Nothing here measures whether a claim title changes what a person remembers a week later. A study of that question would need a design this note does not have.",
                },
                {
                    "type": "paragraph",
                    "text": "The note also does not say that every heading in a paper should be a finding. A methods section can be titled “Methods.” The pressure applies where a picture is being asked to carry an argument: the title of that picture, and the title of the slide or the subsection that exists only to present it.",
                },
                {
                    "type": "list",
                    "items": [
                        "No new dataset was collected.",
                        "No DOI is attached, because none was re-checked for this note.",
                        "The yuan figures in the table are illustrative and labeled as such.",
                    ],
                },
            ],
        },
    ],
    "references": [
        {
            "id": "cleveland1984",
            "label": "Cleveland and McGill, 1984",
            "text": "Cleveland, W. S., and McGill, R. (1984). Graphical perception: Theory, experimentation, and application to the development of graphical methods. Journal of the American Statistical Association, 79(387), 531–554.",
        },
        {
            "id": "tufte2001",
            "label": "Tufte, 2001",
            "text": "Tufte, E. R. (2001). The Visual Display of Quantitative Information (2nd ed.). Cheshire, CT: Graphics Press.",
        },
    ],
}
