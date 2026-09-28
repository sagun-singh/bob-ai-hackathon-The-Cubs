"""
FIR Intelligence & Crime Pattern Detector - Streamlit skeleton (Person 4)

Run with:   streamlit run app.py

Right now everything is FAKE / hard-coded so the page renders immediately.
At the 1:30 mark, only the function `analyze_firs()` needs to change:
replace its body with calls to Person 2's LLM function and Person 3's matcher.
The rest of the page stays exactly as it is.

Shared field names (agreed with the team - do not rename):
    fir_id, crime_type, accused_description, location, mo_summary, victim_profile
"""

import pandas as pd
import streamlit as st

st.set_page_config(
    page_title="FIR Intelligence & Crime Pattern Detector",
    page_icon="🚔",
    layout="wide",
)

# --------------------------------------------------------------------------
# FAKE DATA (delete once real data is wired in)
# --------------------------------------------------------------------------
SAMPLE_TEXT = """FIR 1: On 3 March at 6:40 PM near Sector 21 market, two men on a black motorcycle snatched a gold chain from a woman walking home and fled.

FIR 2: On 9 March at 7:10 PM outside Sector 9 bus stop, two men on a black bike pulled a gold chain from an elderly woman and sped away.

FIR 3: A caller posing as a bank officer asked the complainant for an OTP and withdrew Rs 48,000 from his account."""

FAKE_RESULTS = [
    {
        "fir_id": "FIR-1",
        "crime_type": "Chain snatching",
        "accused_description": "Two men, black motorcycle",
        "location": "Sector 21 market",
        "mo_summary": "Two riders on a bike snatch gold chain from a woman on foot",
        "victim_profile": "Woman, walking alone in the evening",
    },
    {
        "fir_id": "FIR-2",
        "crime_type": "Chain snatching",
        "accused_description": "Two men, black bike",
        "location": "Sector 9 bus stop",
        "mo_summary": "Two riders on a bike pull gold chain from an elderly woman",
        "victim_profile": "Elderly woman, evening",
    },
    {
        "fir_id": "FIR-3",
        "crime_type": "Cyber fraud",
        "accused_description": "Unknown caller",
        "location": "Online / phone",
        "mo_summary": "Poses as bank officer, asks for OTP, drains account",
        "victim_profile": "Adult male account holder",
    },
]

FAKE_FLAGGED = [
    {
        "fir_ids": ["FIR-1", "FIR-2"],
        "similarity": 82,
        "reason": "Same MO (two riders on a black bike snatching gold chains from women "
        "on foot in the evening) and matching accused description.",
    }
]

FAKE_SUMMARY = (
    "This batch of 3 FIRs shows a likely chain-snatching series (2 FIRs) "
    "and 1 cyber-fraud report. (Placeholder text - real AI summary comes later.)"
)


# --------------------------------------------------------------------------
# THE ONE FUNCTION TO SWAP LATER
# --------------------------------------------------------------------------
def analyze_firs(raw_text: str) -> dict:
    """
    Takes the pasted FIR text, returns a dict with exactly these keys:
        "results": list of dicts (one per FIR, using the shared field names)
        "flagged": list of {"fir_ids": [...], "similarity": int, "reason": str}
        "summary": str

    TODO at 1:30: replace the body with something like
        firs = split_into_firs(raw_text)
        results = [classify_and_extract(f) for f in firs]     # Person 2
        flagged = find_linked_series(results)                  # Person 3
        summary = make_summary(results, flagged)               # Person 2
        return {"results": results, "flagged": flagged, "summary": summary}
    """
    return {
        "results": FAKE_RESULTS,
        "flagged": FAKE_FLAGGED,
        "summary": FAKE_SUMMARY,
    }


def count_firs(raw_text: str) -> int:
    """Rough count: FIRs are separated by blank lines."""
    return len([p for p in raw_text.split("\n\n") if p.strip()])


# --------------------------------------------------------------------------
# PAGE
# --------------------------------------------------------------------------
st.title("🚔 FIR Intelligence & Crime Pattern Detector")
st.caption(
    "Decision-support for investigators. All data shown is invented; "
    "a human always reviews any flagged match."
)

# Input area
raw_text = st.text_area(
    "Paste a batch of FIRs (separate each FIR with a blank line)",
    value=SAMPLE_TEXT,
    height=220,
)

col_btn, col_count = st.columns([1, 4])
with col_btn:
    analyze_clicked = st.button("Analyze", type="primary", use_container_width=True)
with col_count:
    st.write(f"{count_firs(raw_text)} FIR(s) detected in the box above")

# Run analysis and remember it, so the page doesn't blank out on re-render
if analyze_clicked:
    if not raw_text.strip():
        st.warning("Please paste at least one FIR first.")
    else:
        with st.spinner("Analysing FIRs..."):
            try:
                st.session_state["analysis"] = analyze_firs(raw_text)
            except Exception as e:  # keep the demo alive if something breaks
                st.error(f"Something went wrong during analysis: {e}")

analysis = st.session_state.get("analysis")

st.divider()

if analysis is None:
    st.info("Paste FIRs above and click **Analyze** to see results.")
else:
    results = analysis["results"]
    flagged = analysis["flagged"]

    # 1. Summary at the top
    st.subheader("📝 Summary")
    st.write(analysis["summary"])

    # Quick numbers
    df = pd.DataFrame(results)
    m1, m2, m3 = st.columns(3)
    m1.metric("FIRs analysed", len(df))
    m2.metric("Crime types found", df["crime_type"].nunique() if not df.empty else 0)
    m3.metric("Possible repeat-offender groups", len(flagged))

    # 2. Flagged panel (the first thing a judge should notice)
    st.subheader("⚠ Possible Repeat Offenders")
    if not flagged:
        st.success("No linked FIRs found in this batch.")
    else:
        for group in flagged:
            ids = " + ".join(group["fir_ids"])
            st.warning(
                f"**{ids}**  ·  similarity {group['similarity']}%\n\n"
                f"**Why linked:** {group['reason']}"
            )

    # 3. Results table
    st.subheader("📋 Extracted details")
    st.dataframe(
        df,
        use_container_width=True,
        hide_index=True,
        column_config={
            "fir_id": "FIR",
            "crime_type": "Crime type",
            "accused_description": "Accused",
            "location": "Location",
            "mo_summary": "Modus Operandi",
            "victim_profile": "Victim",
        },
    )
