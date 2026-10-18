<!-- PDF page 1 -->
# **Page-aware document evidence**

ABSTRACT

This synthetic teaching paper studies page-aware evidence linking for local document

readers.

The core question is whether stable source identifiers can preserve traceability through

chunked analysis.

Our contribution is a source-first pipeline that keeps page numbers and verbatim text beside

each finding.

The teaching example contains no real experiment and no external research claims.

INTRODUCTION

Long documents can hide important limitations near the end. Processing only the abstract

loses this evidence.

We use a local PDF extractor followed by bounded model requests and a self-contained

reading dashboard.


PaperWeave synthetic teaching fixture / 1




<!-- PDF page 2 -->
# **Method: sources before summaries**

METHOD

Each paragraph receives a stable source identifier and the physical PDF page number.

The model returns a concise finding, a reader-friendly explanation, and a verbatim evidence

quote.

An exact normalized text match checks that the quoted words exist in the extracted source.

A matching quote does not prove that a model conclusion is semantically correct.

ARGUMENT

First preserve the sources, then analyze each chunk, and finally merge findings without

deleting leaves.


PaperWeave synthetic teaching fixture / 2




<!-- PDF page 3 -->
# **A controlled illustration**

ILLUSTRATIVE EVALUATION

The fixture uses a deterministic local response server to test the complete software path.

It is not an evaluation of a real language model and cannot establish scientific accuracy.

The dashboard includes searchable nodes, evidence panels, diagram switching, and offline

exports.

The implementation records analyzed chunk identifiers so omitted processing steps remain

visible.


PaperWeave synthetic teaching fixture / 3




<!-- PDF page 4 -->
# **Limits and application boundary**

LIMITATIONS

This demonstration uses synthetic text and does not measure performance on real scientific

papers.

Image-only scans require OCR before use in the text-PDF baseline.

Evidence matching confirms text presence rather than entailment of the model claim.

APPLICATION BOUNDARY

The tool supports assisted reading, while numerical claims and scientific conclusions need

human checking.

TAIL_SENTINEL: The last page must be analyzed and included in the coverage report.


PaperWeave synthetic teaching fixture / 4


