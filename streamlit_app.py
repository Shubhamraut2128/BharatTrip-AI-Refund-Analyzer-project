import streamlit as st
import pandas as pd
import plotly.express as px
from groq import Groq
import os
from dotenv import load_dotenv


st.set_page_config(
    page_title="AI Refund Analyzer",
    layout="wide"
)


st.title("AI Refund Analyzer")


uploaded_file = st.file_uploader(
    "Upload Refund Excel",
    type=["xlsx"]
)


if uploaded_file:

    # Load sheets

    support = pd.read_excel(
        uploaded_file,
        sheet_name="Support_Tracker"
    )

    finance = pd.read_excel(
        uploaded_file,
        sheet_name="Finance_Tracker"
    )

    escalation = pd.read_excel(
        uploaded_file,
        sheet_name="Escalations"
    )


    # Rename IDs

    support = support.rename(
        columns={
            "Ticket ID":"Refund_ID",
            "Refund Amount (INR)":"Refund_Amount"
        }
    )


    finance = finance.rename(
        columns={
            "Ref No":"Refund_ID",
            "Amount Paid (INR)":"Amount_Paid"
        }
    )


    escalation = escalation.rename(
        columns={
            "Related Ticket / Ref":"Refund_ID",
            "Escalation ID":"Escalation_ID"
        }
    )


    st.success("Dataset Loaded Successfully")


    # KPI


    col1,col2,col3,col4 = st.columns(4)


    col1.metric(
        "Support Records",
        len(support)
    )


    col2.metric(
        "Finance Records",
        len(finance)
    )


    col3.metric(
        "Escalations",
        len(escalation)
    )


    col4.metric(
        "Difference",
        len(support)-len(finance)
    )



    # Missing Finance


    missing_finance = support[
        ~support["Refund_ID"].isin(
            finance["Refund_ID"]
        )
    ]


    st.subheader(
        "Missing Refunds in Finance"
    )


    st.dataframe(
        missing_finance
    )


    # Missing Support


    missing_support = finance[
        ~finance["Refund_ID"].isin(
            support["Refund_ID"]
        )
    ]


    # Merge


    merged = support.merge(
        finance,
        on="Refund_ID",
        how="inner"
    )


    # Status mismatch


    status_mismatch = merged[
        merged["Status"] != merged["Payout Status"]
    ]


    st.subheader(
        "Status Mismatch"
    )


    st.dataframe(
        status_mismatch
    )



    # Amount mismatch


    amount_mismatch = merged[
        merged["Refund_Amount"] != merged["Amount_Paid"]
    ]


    st.subheader(
        "Amount Mismatch"
    )


    st.dataframe(
        amount_mismatch
    )



    # Chart


    fig = px.bar(
        support,
        x="Status",
        title="Refund Status Distribution"
    )


    st.plotly_chart(fig)



    # Groq AI


    load_dotenv()


    client = Groq(
        api_key=os.getenv(
            "GROQ_API_KEY"
        )
    )


    def summarize(prompt):

        response = client.chat.completions.create(

            model="llama-3.3-70b-versatile",

            messages=[
                {
                    "role":"user",
                    "content":prompt
                }
            ],

            temperature=0.3

        )

        return response.choices[0].message.content



    prompt = f"""

You are an Operations Consultant.

Analyze BharatTrip Refund Operations.

Records:

Support:
{len(support)}

Finance:
{len(finance)}

Escalations:
{len(escalation)}

Missing Finance Refunds:
{len(missing_finance)}

Missing Support Refunds:
{len(missing_support)}

Status Mismatch:
{len(status_mismatch)}

Amount Mismatch:
{len(amount_mismatch)}


Generate:

1. Executive Summary

2. Root Cause Analysis

3. Business Impact

4. Recommendations

5. AI Automation Opportunities

"""


    if st.button("Generate AI Report"):

        report = summarize(prompt)


        st.subheader(
            "AI Analysis"
        )


        st.markdown(
            report
        )



    # Download CSV


    csv = missing_finance.to_csv(
        index=False
    ).encode("utf-8")


    st.download_button(

        label="Download Missing Refunds",

        data=csv,

        file_name="missing_refunds.csv",

        mime="text/csv"

    )