import streamlit as st
import pandas as pd
import requests
import gspread
from oauth2client.service_account import ServiceAccountCredentials
import pypdf             # Dynamic PDF CV parser

# 1. Page Configuration & Custom CSS Injection for a Premium UI
st.set_page_config(
    page_title="UK RX & Insolvency Agentic Engine",
    page_icon="💼",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Premium Dark Glassmorphism Styling
st.markdown("""
<style>
    .stApp {
        background-color: #0d1117;
        color: #c9d1d9;
    }
    button[data-baseweb="tab"] {
        font-size: 16px;
        font-weight: 600;
        color: #8b949e !important;
        background-color: transparent !important;
        border: none !important;
    }
    button[aria-selected="true"] {
        color: #58a6ff !important;
        border-bottom: 2px solid #58a6ff !important;
    }
    .custom-card {
        background: rgba(22, 27, 34, 0.8);
        border: 1px solid #30363d;
        border-radius: 12px;
        padding: 20px;
        margin-bottom: 15px;
        box-shadow: 0 4px 12px rgba(0,0,0,0.15);
    }
    .metric-value {
        font-size: 28px;
        font-weight: bold;
        color: #58a6ff;
    }
    .metric-label {
        font-size: 13px;
        color: #8b949e;
        text-transform: uppercase;
        letter-spacing: 1px;
    }
</style>
""", unsafe_allow_html=True)

# 2. Comprehensive UK RX Firms Database with Email Mapping Patterns
UK_RX_DATABASE = {
    "Alvarez & Marsal (A&M)": {"domain": "alvarezandmarsal.com", "syntax": "fi.l", "category": "Elite Boutique", "keywords": ["Alvarez", "A&M", "Alvarez & Marsal"]},
    "Houlihan Lokey": {"domain": "hl.com", "syntax": "f.l", "category": "Elite Boutique", "keywords": ["Houlihan", "Lokey"]},
    "FTI Consulting": {"domain": "fticonsulting.com", "syntax": "f.l", "category": "Elite Boutique", "keywords": ["FTI", "FTI Consulting"]},
    "AlixPartners": {"domain": "alixpartners.com", "syntax": "fi.l", "category": "Elite Boutique", "keywords": ["AlixPartners", "Alix"]},
    "Teneo": {"domain": "teneo.com", "syntax": "f.l", "category": "Elite Boutique", "keywords": ["Teneo"]},
    "Kroll": {"domain": "kroll.com", "syntax": "f.l", "category": "Elite Boutique", "keywords": ["Kroll"]},
    "Rothschild & Co": {"domain": "rothschildandco.com", "syntax": "f.l", "category": "Elite Boutique", "keywords": ["Rothschild"]},
    "Lazard": {"domain": "lazard.com", "syntax": "f.l", "category": "Elite Boutique", "keywords": ["Lazard"]},
    "Evercore": {"domain": "evercore.com", "syntax": "f.l", "category": "Elite Boutique", "keywords": ["Evercore"]},
    "PJT Partners": {"domain": "pjtpartners.com", "syntax": "f.l", "category": "Elite Boutique", "keywords": ["PJT", "PJT Partners"]},
    "Jefferies": {"domain": "jefferies.com", "syntax": "f.l", "category": "Elite Boutique", "keywords": ["Jefferies"]},
    "Greenhill & Co.": {"domain": "greenhill.com", "syntax": "f.l", "category": "Elite Boutique", "keywords": ["Greenhill"]},
    
    "Interpath Advisory": {"domain": "interpathadvisory.com", "syntax": "f.l", "category": "Independent Specialist", "keywords": ["Interpath"]},
    "FRP Advisory": {"domain": "frpadvisory.com", "syntax": "f.l", "category": "Independent Specialist", "keywords": ["FRP", "FRP Advisory"]},
    "Quantuma": {"domain": "quantuma.com", "syntax": "f.l", "category": "Independent Specialist", "keywords": ["Quantuma"]},
    "Begbies Traynor": {"domain": "begbies-trapnor.com", "syntax": "f.l", "category": "Independent Specialist", "keywords": ["Begbies", "Traynor", "Begbies Traynor"]},
    "BTG Advisory": {"domain": "btgadvisory.com", "syntax": "f.l", "category": "Independent Specialist", "keywords": ["BTG", "BTG Advisory"]},
    "Leonard Curtis": {"domain": "lcg.info", "syntax": "f.l", "category": "Independent Specialist", "keywords": ["Leonard Curtis", "Leonard"]},
    "Evelyn Partners (ex-ReSolve)": {"domain": "evelyn.com", "syntax": "f.l", "category": "Independent Specialist", "keywords": ["Evelyn", "Evelyn Partners", "ReSolve"]},
    
    "BDO": {"domain": "bdo.co.uk", "syntax": "f.l", "category": "Mid-Tier Network", "keywords": ["BDO"]},
    "Grant Thornton UK": {"domain": "uk.gt.com", "syntax": "f.l", "category": "Mid-Tier Network", "keywords": ["Grant Thornton", "Thornton"]},
    "RSM UK": {"domain": "rsmuk.com", "syntax": "f.l", "category": "Mid-Tier Network", "keywords": ["rsm", "rsm uk"]},
    "Mazars (Forvis Mazars)": {"domain": "mazars.co.uk", "syntax": "f.l", "category": "Mid-Tier Network", "keywords": ["Mazars", "Forvis"]},
    "Moore Kingston Smith": {"domain": "mks.co.uk", "syntax": "f.l", "category": "Mid-Tier Network", "keywords": ["Moore Kingston", "Kingston Smith"]},
    "Menzies LLP": {"domain": "menzies.co.uk", "syntax": "f.l", "category": "Mid-Tier Network", "keywords": ["Menzies"]},
    "Dow Schofield Watts (DSW)": {"domain": "dswcapital.com", "syntax": "f.l", "category": "Mid-Tier Network", "keywords": ["Dow Schofield", "DSW"]},
    "Gambit Corporate Finance": {"domain": "gambitcf.com", "syntax": "f.l", "category": "Mid-Tier Network", "keywords": ["Gambit"]},
    "Liverpool Street Capital Advisors": {"domain": "lscadvisors.com", "syntax": "f.l", "category": "Mid-Tier Network", "keywords": ["Liverpool Street", "Liverpool"]},
    "MCF Corporate Finance": {"domain": "mcfcf.com", "syntax": "f.l", "category": "Mid-Tier Network", "keywords": ["MCF"]},
    
    "PwC": {"domain": "pwc.com", "syntax": "f.l", "category": "Big 4", "keywords": ["PwC", "PriceWaterhouse", "PricewaterhouseCoopers"]},
    "Deloitte": {"domain": "deloitte.co.uk", "syntax": "f.l", "category": "Big 4", "keywords": ["Deloitte"]},
    "EY": {"domain": "ey.com", "syntax": "f.l", "category": "Big 4", "keywords": ["EY", "Ernst", "Young", "Ernst & Young"]},
    "KPMG": {"domain": "kpmg.co.uk", "syntax": "f.l", "category": "Big 4", "keywords": ["KPMG"]},
    
    "BCG TURN": {"domain": "bcg.com", "syntax": "f.l", "category": "Consulting / Strategy", "keywords": ["BCG", "Boston Consulting", "BCG TURN"]},
    "McKinsey & Company (Transformation/RTS)": {"domain": "mckinsey.com", "syntax": "f.l", "category": "Consulting / Strategy", "keywords": ["McKinsey", "RTS"]},
    "Bain & Company (Turnaround/Restructuring)": {"domain": "bain.com", "syntax": "f.l", "category": "Consulting / Strategy", "keywords": ["Bain"]}
}

ALL_FIRMS = list(UK_RX_DATABASE.keys())

# Helper function to extract, sanitize, and compact PDF text (Lighter 2000 Char limit for instant load)
def extract_text_from_pdf(uploaded_file):
    try:
        reader = pypdf.PdfReader(uploaded_file)
        text = ""
        for page in reader.pages:
            page_text = page.extract_text()
            if page_text:
                text += page_text + "\n"
        
        # 1. Clean non-ASCII characters to prevent API choking
        text = "".join(char for char in text if ord(char) < 128)
        # 2. Compact text
        text = "\n".join([line.strip() for line in text.split("\n") if line.strip()])
        # 3. Micro-cap at 2000 characters for instant, lag-free API responses
        return text[:2000]
    except Exception as e:
        return f"Error reading PDF: {e}"

# Helper function to connect to Google Sheets
# Helper function to connect to Google Sheets (Supports both Local JSON & Secure Cloud Secrets!)
def get_google_sheet(sheet_name):
    try:
        scope = ["https://spreadsheets.google.com/feeds", "https://www.googleapis.com/auth/drive"]
        
        # 1. Cloud Mode: Load natively from encrypted Streamlit Secrets
        if "gcp_service_account" in st.secrets:
            creds = ServiceAccountCredentials.from_json_keyfile_dict(
                dict(st.secrets["gcp_service_account"]), 
                scope
            )
        # 2. Local Mode Fallback: Load from local google_creds.json
        else:
            creds = ServiceAccountCredentials.from_json_keyfile_name("google_creds.json", scope)
            
        client = gspread.authorize(creds)
        
        # Securely locks onto your exact Spreadsheet ID!
        sheet = client.open_by_key("1QczXissyO24ZorFyOaodDThm-29AbdQFU4tsb0UkSzI").sheet1
        return sheet, None
    except Exception as e:
        return None, str(e)

# Helper function to find and overwrite a specific row in Google Sheets (Dual-Match Handle & Name Fallback!)
def update_custom_pitch_in_sheets(sheet_name, target_url, target_name, invite_text, follow_up_text):
    try:
        sheet, conn_error = get_google_sheet(sheet_name)
        if conn_error:
            return False, conn_error
        
        # 1. Fetch raw lists from Google Sheets (Column A and Column E)
        names = sheet.col_values(1)
        urls = sheet.col_values(5)
        
        # Helper to extract unique handle
        def extract_handle(u_str):
            u_str = u_str.strip().lower().rstrip("/")
            if "/in/" in u_str:
                parts = u_str.split("/in/")
                if len(parts) > 1:
                    return parts[1].split("?")[0].strip()
            return u_str
            
        target_handle = extract_handle(target_url)
        clean_target_name = target_name.split(" - ")[0].split(" | ")[0].strip().lower() # e.g. "scott rubin"
        
        row_idx = None
        match_type = ""
        
        # STRATEGY 1: Substring Handle Matching
        for idx, u_val in enumerate(urls):
            u_clean = u_val.strip().lower()
            if extract_handle(u_clean) == target_handle or target_handle in u_clean:
                row_idx = idx + 1
                match_type = "LinkedIn Handle (Substring)"
                break
                
        # STRATEGY 2: Fallback Substring Name Matching (Guarantees Name Match!)
        if row_idx is None:
            for idx, n_val in enumerate(names):
                n_clean = n_val.strip().lower()
                # Check if "scott rubin" is inside "scott rubin - se alvarez..."
                if clean_target_name in n_clean or n_clean in clean_target_name:
                    row_idx = idx + 1
                    match_type = "Name (Substring Match)"
                    break
        
        if row_idx is not None:
            # Overwrite Column G (7) and Column H (8) for that specific row
            sheet.update_cell(row_idx, 7, invite_text)
            sheet.update_cell(row_idx, 8, follow_up_text)
            return True, f"Matched by {match_type} (Row {row_idx})"
        else:
            return False, f"Could not find a row in Google Sheet matching handle '{target_handle}' or Name '{clean_target_name}'."
    except Exception as e:
        return False, str(e)

# Helper to detect firm
def detect_firm(title_or_snippet):
    text = title_or_snippet.lower()
    for firm, info in UK_RX_DATABASE.items():
        for keyword in info["keywords"]:
            if keyword.lower() in text:
                return firm, info["category"]
    return "Unknown / Other", "N/A"

# Helper function to predict email
def predict_email(full_name, firm_name):
    if not full_name or firm_name not in UK_RX_DATABASE:
        return None, None
    
    firm_info = UK_RX_DATABASE[firm_name]
    domain = firm_info["domain"]
    syntax = firm_info["syntax"]
    
    parts = [p.strip().lower() for p in full_name.split() if p.strip()]
    if len(parts) == 0:
        return None, None
    
    first = parts[0]
    last = parts[-1] if len(parts) > 1 else ""
    first_initial = first[0] if first else ""
    
    if syntax == "f.l" and last:
        email = f"{first}.{last}@{domain}"
    elif syntax == "fi.l" and last:
        email = f"{first_initial}.{last}@{domain}"
    elif syntax == "fil" and last:
        email = f"{first_initial}{last}@{domain}"
    elif syntax == "f":
        email = f"{first}@{domain}"
    elif syntax == "l" and last:
        email = f"{last}@{domain}"
    else:
        email = f"{first}.{last}@{domain}" if last else f"{first}@{domain}"
        
    return email, firm_info["category"]

# 3. Sidebar - Control Panel
st.sidebar.title("Search Controls")
st.sidebar.write("Configure your target parameters below.")

# Google Sheet Name Configuration
sheet_name = st.sidebar.text_input("Google Sheet Name", value="UK RX Leads Tracker")

# DYNAMIC FILE UPLOADER FOR TAILORED CV
uploaded_cv = st.sidebar.file_uploader("Upload Tailored CV (PDF) 📄", type=["pdf"], help="Upload your firm-specific CV. Gemini will read it to customize your pitch.")

# Firm selection
selected_firms = st.sidebar.multiselect(
    "Select Target Firms",
    options=ALL_FIRMS,
    default=["Alvarez & Marsal (A&M)", "FRP Advisory", "Interpath Advisory"]
)

# Roles / Seniority
selected_roles = st.sidebar.multiselect(
    "Select Target Roles",
    options=["Partner", "Managing Director", "Director", "Associate", "HR", "Recruitment", "Talent Acquisition"],
    default=["Partner", "Director"]
)

# Location Input
location = st.sidebar.text_input("Target Location", value="London, United Kingdom")

# Durham Alumni Toggle
durham_only = st.sidebar.toggle("Durham University Alumni Only 🎓", value=False)

# API Keys Section (Prefilled with your actual credentials)
api_key = st.sidebar.text_input("SerpApi Key", type="password", placeholder="Enter your SerpApi key")
gemini_key = st.sidebar.text_input("Gemini API Key 🔑", type="password", placeholder="Enter your Google Gemini key")

st.sidebar.divider()
st.sidebar.write("💡 *Tip: Select multiple firms and roles to compile a comprehensive sheet in one go.*")

# Initialize Session State Variables for Row Binding & Dynamic Inputs
if "target_name" not in st.session_state:
    st.session_state["target_name"] = "Alex Mercer"
if "target_firm" not in st.session_state:
    st.session_state["target_firm"] = "Alvarez & Marsal (A&M)"
if "target_snippet" not in st.session_state:
    st.session_state["target_snippet"] = "Partner specializing in middle-market operational corporate recovery and restructuring."
if "target_url" not in st.session_state:
    st.session_state["target_url"] = "https://uk.linkedin.com/in/mock-url"
if "ai_generated_invite" not in st.session_state:
    st.session_state["ai_generated_invite"] = ""
if "ai_generated_follow_up" not in st.session_state:
    st.session_state["ai_generated_follow_up"] = ""

# 4. Main Body - Tabs Setup
st.title("💼 UK RX & Insolvency Agentic Networking Engine")
st.write("Systematic lead finder & outreach assistant for Srujan Dhawale.")

tab1, tab2, tab3, tab4 = st.tabs([
    "🔍 Lead Finder Engine", 
    "✉️ Corporate Email Predictor", 
    "📝 AI Pitch Composer", 
    "📈 Interactive CRM"
])

# ---- TAB 1: LEAD FINDER ENGINE ----
with tab1:
    st.subheader("Live LinkedIn X-Ray Search")
    st.write("Click 'Execute Search' to pull live profiles. 💡 *Click on any row to load that person into the Pitch Composer!*")
    
    col1, col2 = st.columns([3, 1])
    
    if "search_results_df" not in st.session_state:
        st.session_state["search_results_df"] = None
        
    with col1:
        if st.button("🚀 Execute Search", type="primary"):
            if not api_key:
                st.error("Error: Please enter your SerpApi Key in the sidebar control panel to run a live search.")
            elif not selected_firms or not selected_roles:
                st.warning("Please select at least one firm and one role in the sidebar.")
            else:
                roles_query = " OR ".join([f'"{r}"' for r in selected_roles])
                firms_query = " OR ".join([f'"{f}"' for f in selected_firms])
                alumni_query = ' AND ("Durham" OR "DUBS" OR "Durham University")' if durham_only else ""
                
                full_query = f'site:uk.linkedin.com/in/ ({firms_query}) AND ({roles_query}) AND "{location}"{alumni_query}'
                
                st.write(f"**Executing Query:** `{full_query}`")
                
                all_leads = []
                start_offset = 0
                max_pages = 2  
                
                progress_bar = st.progress(0)
                status_text = st.empty()
                
                for page in range(max_pages):
                    status_text.text(f"Fetching page {page + 1} from Google search...")
                    
                    params = {
                        "engine": "google",
                        "q": full_query,
                        "api_key": api_key,
                        "num": 100,
                        "start": start_offset
                    }
                    
                    try:
                        response = requests.get("https://serpapi.com/search", params=params)
                        
                        if response.status_code == 200:
                            data = response.json()
                            results = data.get("organic_results", [])
                            
                            if not results:
                                break
                                
                            for item in results:
                                raw_title = item.get("title", "")
                                link = item.get("link", "")
                                snippet = item.get("snippet", "")
                                
                                clean_title = raw_title.replace(" | LinkedIn", "").replace(" - LinkedIn", "")
                                detected_firm, category = detect_firm(clean_title + " " + snippet)
                                
                                all_leads.append({
                                    "Name & Title": clean_title,
                                    "Detected Firm": detected_firm,
                                    "Category": category,
                                    "Location": location,
                                    "LinkedIn Link": link,
                                    "Snippet Summary": snippet
                                })
                            
                            serp_pagination = data.get("serpapi_pagination", {})
                            if "next" in serp_pagination:
                                start_offset += 100
                            else:
                                break
                        else:
                            st.error(f"API Error (Page {page+1}): Received status code {response.status_code}")
                            break
                    except Exception as e:
                        st.error(f"Error during API call: {e}")
                        break
                        
                    progress_bar.progress((page + 1) / max_pages)
                
                status_text.text("Finished fetching results!")
                progress_bar.empty()
                
                if all_leads:
                    df = pd.DataFrame(all_leads)
                    st.session_state["search_results_df"] = df
                    st.success(f"Found {len(df)} matching profiles!")
                else:
                    st.warning("No live profiles found matching your current parameters.")
                    st.session_state["search_results_df"] = None

        if st.session_state["search_results_df"] is not None:
            event = st.dataframe(
                st.session_state["search_results_df"], 
                width="stretch",
                on_select="rerun",
                selection_mode="single-row",
                key="leads_dataframe"
            )
            
            selected_row_idx = None
            if event:
                try:
                    rows = event.selection.rows
                    if rows:
                        selected_row_idx = rows[0]
                except AttributeError:
                    try:
                        rows = event.get("selection", {}).get("rows", [])
                        if rows:
                            selected_row_idx = rows[0]
                    except Exception:
                        pass
            
            if selected_row_idx is not None:
                selected_row = st.session_state["search_results_df"].iloc[selected_row_idx]
                new_url = selected_row["LinkedIn Link"]
                
                # ONLY reset and load if it's actually a brand-new selection!
                if st.session_state.get("target_url") != new_url:
                    raw_name = selected_row["Name & Title"].split(" - ")[0].split(" | ")[0]
                    st.session_state["target_name"] = raw_name
                    st.session_state["target_firm"] = selected_row["Detected Firm"]
                    st.session_state["target_snippet"] = selected_row["Snippet Summary"]
                    st.session_state["target_url"] = new_url
                    st.session_state["ai_generated_invite"] = "" 
                    st.session_state["ai_generated_follow_up"] = ""
                    
                    if "live_invite_area" in st.session_state:
                        del st.session_state["live_invite_area"]
                    if "live_follow_up_area" in st.session_state:
                        del st.session_state["live_follow_up_area"]
                        
                    st.toast(f"🎯 Loaded {raw_name} ({selected_row['Detected Firm']}) into Pitch Composer!")
            
    with col2:
        st.write("### Actions")
        if st.session_state["search_results_df"] is not None:
            csv_data = st.session_state["search_results_df"].to_csv(index=False).encode('utf-8')
            st.download_button(
                label="📥 Download Results (CSV)",
                data=csv_data,
                file_name="rx_linkedin_leads.csv",
                mime="text/csv"
            )
            
            # GOOGLE SHEETS DE-DUPLICATED SYNC BUTTON (KEEPS COLUMNS G & H COMPLETELY BLANK!)
            if st.button("💾 Sync All to Google Sheets", type="primary"):
                sheet, conn_error = get_google_sheet(sheet_name)
                
                if conn_error:
                    st.error(f"❌ Google Sheets Connection Error: {conn_error}")
                elif sheet is not None:
                    with st.spinner("Connecting to Google Sheets Cloud..."):
                        try:
                            # 1. Fetch existing spreadsheet data to de-duplicate by URL
                            existing_values = sheet.get_all_values()
                            existing_urls = set()
                            
                            # LinkedIn URL is Column E (index 4)
                            if len(existing_values) > 1:
                                for row in existing_values[1:]:
                                    if len(row) > 4:
                                        existing_urls.add(row[4].strip())
                            
                            if not existing_values:
                                # Create initial expanded headers if sheet is empty
                                sheet.append_row(["Name & Title", "Detected Firm", "Category", "Location", "LinkedIn Link", "Outreach Status", "Connection Invite Note", "Detailed Post-Connection Pitch", "Notes / Snippet Summary"])
                            
                            # 2. Build append list (excluding duplicates & leaving Columns G & H blank!)
                            rows_to_append = []
                            skipped_count = 0
                            for _, row in st.session_state["search_results_df"].iterrows():
                                url = row["LinkedIn Link"].strip()
                                if url in existing_urls:
                                    skipped_count += 1
                                    continue
                                
                                # Modified to leave G and H completely blank!
                                rows_to_append.append([
                                    row["Name & Title"],
                                    row["Detected Firm"],
                                    row["Category"],
                                    row["Location"],
                                    url,
                                    "Not Contacted",
                                    "",  # Connection Invite Note left blank on initial bulk sync!
                                    "",  # Detailed Post-Connection Pitch left blank on initial bulk sync!
                                    row["Snippet Summary"]
                                ])
                            
                            # 3. Write only unique rows to Google Sheet
                            if rows_to_append:
                                sheet.append_rows(rows_to_append)
                                st.success(f"✅ Successfully synced {len(rows_to_append)} new leads! ({skipped_count} duplicates skipped)")
                            else:
                                st.info(f"ℹ️ All {skipped_count} leads already exist in your CRM. No duplicates were added.")
                        except Exception as ex:
                            st.error(f"❌ Error pushing data: {ex}")
        else:
            st.button("📥 Download Results (CSV)", disabled=True)
            st.button("💾 Sync All to Google Sheets", disabled=True)

# ---- TAB 2: EMAIL PREDICTOR ----
with tab2:
    st.subheader("Corporate Email Address Predictor")
    st.write("Generates corporate emails based on established UK restructuring firm email patterns.")
    
    test_name = st.text_input("Enter Professional's Full Name (e.g., John Doe)", "John Doe")
    test_firm = st.selectbox("Select Target Firm", options=ALL_FIRMS)
    
    if st.button("🔮 Predict Email Pattern", type="primary"):
        predicted_email, category = predict_email(test_name, test_firm)
        
        if predicted_email:
            st.success("Email Generated Successfully!")
            col_em1, col_em2 = st.columns(2)
            with col_em1:
                st.metric(label=f"Predicted Email ({test_firm})", value=predicted_email)
            with col_em2:
                st.metric(label="Firm Classification", value=category)
            st.info(f"💡 Standard pattern for {test_firm} is `{UK_RX_DATABASE[test_firm]['syntax']}` on domain `{UK_RX_DATABASE[test_firm]['domain']}`.")
        else:
            st.error("Please enter a valid name.")

# ---- TAB 3: AI PITCH COMPOSER (LIVE DYNAMIC CV FILE UPLOADED) ----
# ---- TAB 3: AI PITCH COMPOSER (LIVE DYNAMIC CV FILE UPLOADED) ----
with tab3:
    st.subheader("AI-Assisted Pitch Builder")
    st.write("Generates both a 300-character Invite Handshake and a Highly Detailed, CV-driven coffee-chat request in a single call [1].")
    
    pitch_type = st.radio(
        "Select Outreach Strategy:",
        ["Select Outreach Strategy:", "Partner / MD Cold Connection", "Durham Alumni Warm Intro", "HR / Recruiter Inquiry"],
        horizontal=True,
        index=1  # Default to Partner Cold Connection
    )
    
    st.divider()
    
    # SICK & CRAZY FEATURE: Lead Source Selector!
    lead_source = st.radio(
        "Select Lead Source:",
        ["Active Search Results (Tab 1 Selection)", "Load Synced Lead from CRM (Google Sheets)"],
        horizontal=True
    )
    
    # If loading from CRM, fetch names dynamically, sort them A-Z, and auto-populate!
    if lead_source == "Load Synced Lead from CRM (Google Sheets)":
        sheet, conn_error = get_google_sheet(sheet_name)
        if conn_error:
            st.error(f"❌ Google Sheets Connection Error: {conn_error}")
        elif sheet is not None:
            with st.spinner("Fetching synced lead directory from your Google Sheet..."):
                try:
                    records = sheet.get_all_records()
                    if records:
                        crm_df = pd.DataFrame(records)
                        
                        # Filter out empty names, extract unique ones, and sort alphabetically A-Z!
                        unique_names = sorted([name for name in crm_df["Name & Title"].unique() if name.strip()])
                        
                        selected_name = st.selectbox("🔍 Search & Select Saved Lead from CRM:", unique_names)
                        
                        # Retrieve matching row and load details into active state
                        matched_row = crm_df[crm_df["Name & Title"] == selected_name].iloc[0]
                        raw_name = selected_row_name = selected_name.split(" - ")[0].split(" | ")[0]
                        
                        # Force update session states
                        st.session_state["target_name"] = raw_name
                        st.session_state["target_firm"] = matched_row["Detected Firm"]
                        st.session_state["target_snippet"] = matched_row["Notes / Snippet Summary"]
                        st.session_state["target_url"] = matched_row["LinkedIn Link"]
                    else:
                        st.warning("ℹ️ Your Google Sheet is connected but contains no leads yet. Please sync some leads from Tab 1 first.")
                except Exception as e:
                    st.error(f"Error loading leads from CRM: {e}")
                    
    st.divider()
    
    col_ui1, col_ui2 = st.columns(2)
    with col_ui1:
        target_name = st.text_input("Target Recipient Name", value=st.session_state["target_name"])
        target_firm = st.text_input("Target Recipient's Firm", value=st.session_state["target_firm"])
    with col_ui2:
        target_snippet = st.text_area("Live Biography / Context (from LinkedIn)", value=st.session_state["target_snippet"], height=100)
    
    first_name = target_name.split()[0]
    
    fallback_invite = f"Hi {first_name}, incoming Durham MSc. I founded Vivarium Group and built V-OS Sovereign, an agentic intelligence terminal for distressed asset restructuring (IBC/US Title 11). Highly admire your restructuring work at {target_firm} and would love to connect."
    fallback_follow_up = f"Hi {first_name}, thanks for connecting! As an incoming Durham MSc student with a background building custom turnaround software (V-OS Sovereign), I wanted to reach out. I would highly value a brief 15-minute virtual coffee chat to ask about your outlook on tech-driven turnarounds in the UK mid-market. Best, Srujan."
    
    col_p1, col_p2 = st.columns([2, 1])
    
    with col_p1:
        # GEMINI TWO-STAGE DYNAMIC HTTPS REST GENERATOR (Simplified Plain Text Output -> Lightning Fast!)
        if st.button("🪄 Generate Custom Dual-Stage AI Pitch with Gemini 3.5", type="primary"):
            if not gemini_key:
                st.error("Error: Please enter your Gemini API Key in the left sidebar to use the AI Generator.")
            elif not uploaded_cv:
                st.warning("⚠️ No CV PDF Uploaded! Please upload your tailored CV (PDF) in the sidebar first so Gemini can read your background.")
            else:
                status_box = st.empty()
                status_box.info("🤖 Starting AI generation pipeline...")
                
                try:
                    status_box.info("📖 Step 1/3: Reading and parsing your uploaded PDF CV...")
                    cv_text = extract_text_from_pdf(uploaded_cv)
                    
                    if "Error reading PDF" in cv_text:
                        st.error(cv_text)
                        status_box.empty()
                    else:
                        char_count = len(cv_text)
                        status_box.info(f"✅ Step 1 complete: Successfully parsed PDF! ({char_count} characters extracted).")
                        
                        status_box.info(f"🌐 Step 2/3: Transmitting CV and context to Google Gemini (model: gemini-3.5-flash)...")
                        
                        prompt = f"""
                        You are Srujan Dhawale's personal corporate restructuring networking coach. Your task is to generate TWO distinct, highly tailored, non-generic messages for Srujan's outreach.
                        
                        Srujan's CV Context (Extracted directly from Srujan's uploaded PDF):
                        \"\"\"
                        {cv_text}
                        \"\"\"
                        
                        Recipient context:
                        - Name: {target_name}
                        - Firm: {target_firm}
                        - Context/Biography: {target_snippet}
                        - Outreach Strategy Chosen: {pitch_type}
                        
                        YOUR TASK:
                        Write two highly customized, polite, distinct, and proactive outreach templates.
                        
                        Message 1: A brief connection request handshake. It must be strictly under 300 characters (including spaces). Keep it brief, polite, and establish a hook.
                        
                        Message 2: A detailed, high-leverage follow-up message to be sent as a DM after they accept. There is no strict length limit here. You must make it highly professional, extremely tailored, extract specific impressive points from Srujan's CV (such as Vivarium Group, V-OS Sovereign, valuation, LBO, etc.), relate them to the recipient's focus or firm, and explicitly ask for 15 minutes of their time for a virtual coffee chat/Zoom call.
                        
                        OUTPUT FORMAT REQUIREMENT:
                        You must respond with the connection invite first, followed by a separator line of exactly "===", followed by the detailed post-connection pitch. Do not include any other markdown formatting, bullet points, headers, or explanations. Just output the two blocks separated by "===".
                        
                        Example:
                        [Invite Text Here under 300 characters]
                        ===
                        [Detailed Coffee Chat Message Here]
                        """
                        
                        # Direct HTTP REST POST payload structure (Gemini 3.5-flash)
                        url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-3.5-flash:generateContent?key={gemini_key}"
                        headers = {"Content-Type": "application/json"}
                        payload = {
                            "contents": [
                                {
                                    "parts": [
                                        {"text": prompt}
                                    ]
                                }
                            ]
                        }
                        
                        # 60-second robust timeout
                        response = requests.post(url, headers=headers, json=payload, timeout=60)
                        
                        if response.status_code == 200:
                            data = response.json()
                            try:
                                raw_ai_text = data["candidates"][0]["content"]["parts"][0]["text"].strip()
                                
                                # Split the response cleanly by the "===" divider!
                                if "===" in raw_ai_text:
                                    parts = raw_ai_text.split("===")
                                    ai_invite = parts[0].strip()
                                    ai_follow_up = parts[1].strip()
                                else:
                                    # Fallback if AI didn't use the divider
                                    ai_invite = raw_ai_text[:280]
                                    ai_follow_up = raw_ai_text
                                
                                st.session_state["ai_generated_invite"] = ai_invite
                                st.session_state["ai_generated_follow_up"] = ai_follow_up
                                
                                # Force update text-area widget states immediately
                                st.session_state["live_invite_area"] = ai_invite
                                st.session_state["live_follow_up_area"] = ai_follow_up
                                
                                status_box.success("🎉 Step 3 complete: Custom dual-stage notes generated successfully!")
                            except Exception as parse_err:
                                st.error(f"❌ Parser Error: Failed to extract text from Google's response payload. Details: {parse_err}")
                                status_box.empty()
                        else:
                            st.error(f"❌ Google REST API Error (HTTP {response.status_code}): {response.text}")
                            status_box.empty()
                except Exception as ex:
                    st.error(f"❌ Secure connection error: {ex}")
                    status_box.empty()

        # Determine display values
        display_invite = st.session_state["ai_generated_invite"] if st.session_state["ai_generated_invite"] else fallback_invite
        display_follow_up = st.session_state["ai_generated_follow_up"] if st.session_state["ai_generated_follow_up"] else fallback_follow_up
        
        col_box1, col_box2 = st.columns(2)
        
        with col_box1:
            st.markdown("<div class='custom-card'>", unsafe_allow_html=True)
            st.write("### 🤝 Stage 1: The Connection Handshake")
            st.write("Paste this into your initial LinkedIn invite request.")
            
            final_invite = st.text_area("LinkedIn Invite Note Draft:", value=display_invite, height=130, key="live_invite_area")
            invite_len = len(final_invite)
            
            if invite_len > 300:
                st.markdown(f"🔴 **Characters: {invite_len} / 300 (EXCEEDS LIMIT - Truncate before sending!)**")
            elif invite_len > 270:
                st.markdown(f"🟡 **Characters: {invite_len} / 300 (Close to limit)**")
            else:
                st.markdown(f"🟢 **Characters: {invite_len} / 300 (Perfect size)**")
            st.markdown("</div>", unsafe_allow_html=True)
                
        with col_box2:
            st.markdown("<div class='custom-card'>", unsafe_allow_html=True)
            st.write("### ☕ Stage 2: The Detailed Post-Connection Pitch")
            st.write("Send this as a DM after they accept your connection request.")
            
            final_follow_up = st.text_area("Post-Connection Coffee Chat Pitch:", value=display_follow_up, height=130, key="live_follow_up_area")
            st.markdown(f"📝 **Words: {len(final_follow_up.split())} words (No limit)**")
            st.markdown("</div>", unsafe_allow_html=True)
            
        st.divider()
        
        # LIVE SINGLE-ROW OVERWRITE SYNC TO GOOGLE SHEETS! (Wired with our brand new dynamic name + handle search!)
        col_sv1, col_sv2 = st.columns([1, 4])
        with col_sv1:
            if st.button("💾 Save Custom Pitch to CRM", type="primary", use_container_width=True):
                with st.spinner("Locating lead and updating spreadsheet..."):
                    target_url = st.session_state["target_url"]
                    success, error_msg = update_custom_pitch_in_sheets(sheet_name, target_url, target_name, final_invite, final_follow_up)
                    
                    if success:
                        st.success(f"✅ CRM Row Updated successfully! ({error_msg})")
                    else:
                        st.error(f"❌ Overwrite Failed: {error_msg}")
        with col_sv2:
            st.info("💡 *Tip: Click 'Save Custom Pitch to CRM' to find this contact in your Google Sheet and overwrite the placeholder templates with these newly generated customized notes!*")

    with col_p2:
        st.info("💡 **Why this works:** Rather than sending a generic intro, highlighting your actual technical background (Vivarium & V-OS Sovereign) proves immediately to senior partners that you possess genuine technical and restructuring-related skills.")

# ---- TAB 4: INTERACTIVE CRM ----
with tab4:
    st.subheader("Your Active Cloud CRM Dashboard")
    st.write("Displaying metrics and records pulled directly from your active Google Sheet.")
    
    if st.button("🔄 Sync & Refresh CRM Dashboard", type="primary"):
        sheet, conn_error = get_google_sheet(sheet_name)
        if conn_error:
            st.error(f"❌ Google Sheets Connection Error: {conn_error}")
        elif sheet is not None:
            with st.spinner("Fetching live data from Google Sheets..."):
                try:
                    records = sheet.get_all_records()
                    if records:
                        crm_df = pd.DataFrame(records)
                        
                        col_mt1, col_col2, col_col3 = st.columns(3)
                        with col_mt1:
                            st.markdown(f"<div class='custom-card'><div class='metric-label'>Total CRM Leads</div><div class='metric-value'>{len(crm_df)}</div></div>", unsafe_allow_html=True)
                        with col_col2:
                            boutiques = len(crm_df[crm_df["Category"] == "Elite Boutique"])
                            st.markdown(f"<div class='custom-card'><div class='metric-label'>Elite Boutique Targets</div><div class='metric-value'>{boutiques}</div></div>", unsafe_allow_html=True)
                        with col_col3:
                            specs = len(crm_df[crm_df["Category"] == "Independent Specialist"])
                            st.markdown(f"<div class='custom-card'><div class='metric-label'>Specialist RX Targets</div><div class='metric-value'>{specs}</div></div>", unsafe_allow_html=True)
                        
                        st.dataframe(crm_df, width="stretch")
                    else:
                        st.info("Your Google Sheet is connected but currently contains no leads. Search and save some leads from Tab 1 to see them here!")
                except Exception as ex:
                    st.error(f"Error reading Google Sheets: {ex}")