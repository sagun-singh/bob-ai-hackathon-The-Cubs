# Presentation

**Project:** FIR Intelligence & Crime Pattern Detector
**Problem Statement:** PS10, IBM Bob × NFSU AI Hackathon
**Team:** The Cubs

Our slide deck is in this folder as `slides.pdf`.

## Accepted Formats

- slides.pdf: preferred (universally viewable)
- slides.pptx: acceptable
- slides.key: acceptable (macOS Keynote)

The file is named `slides.pdf` so the evaluation pipeline can locate it reliably.

## Slide Structure (8 slides)

**Slide 1: Title**
FIR Intelligence & Crime Pattern Detector. Team The Cubs, Problem Statement 10.

**Slide 2: Problem**
Police stations file thousands of FIRs every day as free text. UP Police's CCTNS holds over 3 crore digitised FIRs with no NLP layer on top. Cases like the Jamtara cyber-fraud gang went undetected for years because their FIRs were scattered across districts and never linked.

**Slide 3: Solution**
A Streamlit tool that reads a batch of FIRs, classifies each one, extracts the key facts, and flags FIRs that likely involve the same offender. Screenshot of the app.

**Slide 4: Architecture**
One Streamlit app, five steps:
1. Mock FIR data
2. One combined LLM prompt per FIR (crime type, accused description, location, MO, victim profile as JSON)
3. Repeat-offender matcher (rapidfuzz text similarity)
4. One-paragraph AI summary
5. Streamlit display (results table, flagged panel, summary)

**Slide 5: Demo / Key Feature**
Paste a batch of FIRs and click Analyze. The app shows:
- A Crime Type Breakdown bar chart (assault, burglary, chain snatching, cyber fraud, theft, vehicle theft)
- A Full Results table with id, station, date, crime type, accused description, location, MO summary and victim profile for every FIR
- A "Possible Repeat Offenders" panel listing linked FIRs, match strength and a plain-English reason

**Slide 6: IBM Technologies**
IBM Bob is the AI engine behind the two language-understanding steps of the pipeline:
- **Classification and extraction:** one combined Bob prompt per FIR returns crime type, accused description, location, modus operandi and victim profile as structured JSON.
- **Summary generation:** a second, short Bob prompt turns the crime-type counts and flagged groups into a plain-English summary for officers.
- **Everything else** (FIR parsing, rapidfuzz repeat-offender matching, Streamlit display) is regular Python, so Bob is used only where language understanding is needed.
- Bob was also used as our AI coding assistant to build and debug the app during the hackathon.

**Slide 7: Results / Impact**
- 30 mock FIRs analysed in one batch
- 6 crime categories detected automatically: theft (11), cyber fraud (10), chain snatching (4), assault (3), burglary (1), vehicle theft (1)
- Structured fields extracted per FIR: accused description, location, MO, victim profile
- Possible repeat-offender groups flagged with match strength and reason
- Human-in-the-loop by design: every flag needs officer review

**Slide 8: Team**
- Sanjeevani: mock FIR dataset
- Sagun: AI prompts (classification and extraction)
- Shweta: repeat-offender matcher (rapidfuzz)
- Kanishka: Streamlit app and integration

## Future Work

- Scale from 15-20 to 40-60+ FIRs
- LLM-reasoned match rationale (Layer 2)
- Styled dashboard
- Downloadable PDF/report export

## Ethical Notes

- All FIR data is invented by our team. No real names, addresses, or case numbers are used.
- This is a decision-support tool for investigators, not an automated accusation system. A human reviews every flagged match.
