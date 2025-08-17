# ==============================================================================
# Weekly Pocket Expense Tracker (Python + CSV + Streamlit)
# ==============================================================================

# --- Step 1: Importing Necessary Libraries ---
import streamlit as st
import pandas as pd
import os
import hashlib
from datetime import datetime
import plotly.express as px
import plotly.graph_objects as go


# --- Step 2: Page Configuration ---
st.set_page_config(
    page_title="Weekly Pocket Expense Tracker",
    page_icon="✨",
    layout="wide"
)


# --- Step 3: Data Handling Functions ---

def load_or_initialize_csv(file_path, columns):

    try:
        if not os.path.exists(file_path) or os.path.getsize(file_path) == 0:
            df = pd.DataFrame(columns=columns)
            df.to_csv(file_path, index=False)
            return df
        return pd.read_csv(file_path)
    except Exception as e:
        st.error(f"Error loading or creating file {file_path}: {e}")
        return pd.DataFrame(columns=columns)

def add_user(username, password):
    users_df = load_or_initialize_csv(USERS_FILE, ["username", "password"])
    if username in users_df["username"].values:
        return False
    hashed_password = hashlib.sha256(str.encode(password)).hexdigest()
    new_user = pd.DataFrame([[username, hashed_password]], columns=["username", "password"])
    updated_df = pd.concat([users_df, new_user], ignore_index=True)
    updated_df.to_csv(USERS_FILE, index=False)
    return True

def login_user(username, password):
    users_df = load_or_initialize_csv(USERS_FILE, ["username", "password"])
    if not users_df.empty and username in users_df["username"].values:
        user_data = users_df[users_df["username"] == username]
        hashed_password = hashlib.sha256(str.encode(password)).hexdigest()
        return hashed_password == user_data["password"].iloc[0]
    return False

def add_expense(username, date, category, amount, description):
    expenses_df = load_or_initialize_csv(EXPENSES_FILE, ["username", "Date", "Category", "Amount", "Description"])
    new_expense = pd.DataFrame([[username, date, category, amount, description]], columns=expenses_df.columns)
    updated_df = pd.concat([expenses_df, new_expense], ignore_index=True)
    updated_df.to_csv(EXPENSES_FILE, index=False)

def get_user_expenses(username):
    expenses_df = load_or_initialize_csv(EXPENSES_FILE, ["username", "Date", "Category", "Amount", "Description"])
    user_expenses = expenses_df[expenses_df["username"] == username].copy()
    if not user_expenses.empty:
        user_expenses['Date'] = pd.to_datetime(user_expenses['Date'])
    return user_expenses


# --- Step 4: File Paths ---
USERS_FILE = "users.csv"
EXPENSES_FILE = "expenses.csv"


# --- Step 5: Vibrant & Colorful UI Styling ---
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Poppins:wght@300;400;600;700&display=swap');
    
    html, body, [class*="st-"] { font-family: 'Poppins', sans-serif; }
    .main {
        background-image: url("https://images.unsplash.com/photo-1554034483-26ab8a834b94?q=80&w=2070&auto=format&fit=crop");
        background-size: cover; background-repeat: no-repeat; background-attachment: fixed;
    }
    .stApp > header { background-color: transparent; }
    .st-emotion-cache-16txtl3, .st-emotion-cache-1y4p8pa, .st-emotion-cache-0 {
        background: rgba(255, 255, 255, 0.1); backdrop-filter: blur(10px);
        border-radius: 20px; border: 1px solid rgba(255, 255, 255, 0.2);
        padding: 25px; color: white;
    }
    .st-emotion-cache-16txtl3 p, .st-emotion-cache-16txtl3 h1, .st-emotion-cache-16txtl3 h2, .st-emotion-cache-16txtl3 h3, .st-emotion-cache-16txtl3 label {
        color: white !important; text-shadow: 1px 1px 3px rgba(0,0,0,0.2);
    }
    .stTabs [data-baseweb="tab-list"] { gap: 24px; }
    .stTabs [data-baseweb="tab"] { background-color: transparent; }
    .stTabs [aria-selected="true"] {
        background-color: rgba(138, 43, 226, 0.3); border-bottom: 3px solid #8A2BE2;
    }
    .metric-card {
        background: rgba(0, 0, 0, 0.2); padding: 1.5rem; border-radius: 10px;
        text-align: center; border-left: 5px solid #8A2BE2; height: 100%;
    }
    .metric-card h3 { color: #DA70D6; } .metric-card p { font-size: 2rem; }
    .stButton > button { background: linear-gradient(90deg, #8A2BE2, #DA70D6); color: white; border: none; font-weight: bold;}
</style>
""", unsafe_allow_html=True)


# --- Step 6: Colorful Visualization Functions ---
def get_all_charts(df):
    """Creates a list of 10+ Plotly chart objects for visualization."""
    charts = []
    category_summary = df.groupby('Category')['Amount'].sum().reset_index()
    # Chart 1: Pie Chart
    fig = px.pie(category_summary, values='Amount', names='Category', title='Spending by Category', hole=.4, color_discrete_sequence=px.colors.qualitative.Vivid)
    charts.append(("Spending Distribution", fig))
    # Chart 2: Bar Chart
    fig = px.bar(category_summary.sort_values('Amount', ascending=False), x='Category', y='Amount', title='Category-wise Spending', color='Category', color_discrete_sequence=px.colors.qualitative.Bold)
    charts.append(("Category Comparison", fig))
    # Chart 3: Line Chart
    daily_summary = df.set_index('Date').resample('D')['Amount'].sum().reset_index()
    fig = px.line(daily_summary, x='Date', y='Amount', title='Daily Spending Trend', markers=True)
    fig.update_traces(line=dict(color='#DA70D6', width=3))
    charts.append(("Spending Over Time", fig))
    # Chart 4: Treemap
    fig = px.treemap(category_summary, path=['Category'], values='Amount', title='Interactive Category Breakdown', color_discrete_sequence=px.colors.qualitative.T10)
    charts.append(("Category Treemap", fig))
    # Chart 5: Sunburst Chart
    df['Month'] = df['Date'].dt.strftime('%B')
    sunburst_data = df.groupby(['Month', 'Category'])['Amount'].sum().reset_index()
    fig = px.sunburst(sunburst_data, path=['Month', 'Category'], values='Amount', title='Monthly & Category Spending', color='Amount', color_continuous_scale='Plasma')
    charts.append(("Sunburst View", fig))
    # Chart 6: Cumulative Spending
    df_sorted = df.sort_values('Date')
    df_sorted['Cumulative'] = df_sorted['Amount'].cumsum()
    fig = px.area(df_sorted, x='Date', y='Cumulative', title='Cumulative Spending Over Time')
    charts.append(("Cumulative Spending", fig))
    # Chart 7: Box Plot
    fig = px.box(df, x='Category', y='Amount', title='Transaction Amount Distribution', color='Category', color_discrete_sequence=px.colors.qualitative.Safe)
    charts.append(("Transaction Spread", fig))
    # Chart 8: Calendar Heatmap
    cal_data = df.set_index('Date').resample('D')['Amount'].sum().reset_index()
    cal_data['Day'] = cal_data['Date'].dt.date
    fig = go.Figure(data=go.Heatmap(z=cal_data['Amount'], x=cal_data['Date'], y=[''], colorscale='Cividis_r'))
    fig.update_layout(title='Daily Spending Heatmap')
    charts.append(("Daily Heatmap", fig))
    # Chart 9: Stacked Bar Chart
    monthly_summary = df.groupby([df['Date'].dt.strftime('%Y-%m'), 'Category'])['Amount'].sum().unstack(fill_value=0)
    fig = px.bar(monthly_summary, title='Monthly Spending by Category', barmode='stack', color_discrete_sequence=px.colors.qualitative.Alphabet)
    charts.append(("Monthly Stacked View", fig))
    # Chart 10: Transaction Frequency Funnel
    freq_data = df['Category'].value_counts().reset_index()
    fig = px.funnel(freq_data, x='count', y='Category', title='Transaction Frequency by Category', color_discrete_sequence=px.colors.qualitative.G10)
    charts.append(("Transaction Frequency", fig))
    return charts


# --- Step 7: Session State Initialization ---
if 'logged_in' not in st.session_state: st.session_state['logged_in'] = False
if 'username' not in st.session_state: st.session_state['username'] = ""
if 'chart_page' not in st.session_state: st.session_state.chart_page = 0


# --- Step 8: Main App UI and Logic ---

def show_login_signup():
    """Login/Signup page ko render karta hai."""
    st.markdown("<h1 style='text-align: center;'>🎨 Expense Tracker</h1>", unsafe_allow_html=True)
    st.markdown("<p style='text-align: center;'>Your personal key to mastering your money.</p>", unsafe_allow_html=True)
    
    col1, col2, col3 = st.columns([1, 1, 1])
    with col2:
        # --- (BUG FIXED HERE)
        choice = st.radio(
            "Login or Sign Up", 
            ('Login', 'Sign Up'),
            horizontal=True,
            label_visibility="collapsed"
        )
        
        if choice == 'Login':
            with st.form("login_form"):
                username = st.text_input("Username", placeholder="Enter your username")
                password = st.text_input("Password", type='password', placeholder="Enter your password")
                if st.form_submit_button('Secure Login', use_container_width=True):
                    if login_user(username, password):
                        st.session_state.logged_in = True
                        st.session_state.username = username
                        st.rerun()
                    else: st.error("Incorrect username or password")
        else: # Sign Up
            with st.form("signup_form"):
                new_username = st.text_input("Choose a Username", placeholder="Create a unique username")
                new_password = st.text_input("Choose a Password", type='password', placeholder="Create a strong password")
                if st.form_submit_button('Create Account', use_container_width=True):
                    if add_user(new_username, new_password): st.success("Account created! Please login.")
                    else: st.error("This username is already taken.")

def show_dashboard():
    username = st.session_state.username
    with st.sidebar:
        st.subheader(f"Welcome, {username}! 👋")
        if st.button("Logout", use_container_width=True):
            st.session_state.logged_in = False
            st.session_state.username = ""
            st.rerun()
        st.markdown("---")
        
        st.subheader("➕ Add New Expense")
        with st.form("expense_form", clear_on_submit=True):
            date = st.date_input("Date", value=datetime.today())
            category = st.selectbox("Category", ['🍔 Food', '🚗 Travel', '🏠 Rent', '🛍️ Shopping', '❤️ Health', '🎉 Entertainment'])
            amount = st.number_input("Amount (₹)", min_value=0.01, format="%.2f")
            description = st.text_input("Description (Optional)")
            if st.form_submit_button("Add Expense", type="primary"):
                add_expense(username, date, category, amount, description)
                st.success("Expense added successfully!")

    st.markdown(f'# Welcome to Your <span style="color:#DA70D6;">Vibrant</span> Dashboard, {username}!', unsafe_allow_html=True)
    expenses_df = get_user_expenses(username)
    
    tab1, tab2, tab3 = st.tabs(["🔮 Expenses Overview", "📊 Advanced Visualizations", "📞 Connect with Me"])
    
    with tab1:
        st.header("Financial Snapshot")
        if not expenses_df.empty:
            current_month_expenses = expenses_df[expenses_df['Date'].dt.month == datetime.now().month]
            
            # --- Magical Metric Cards ---
            total_spent = expenses_df['Amount'].sum()
            monthly_spent = current_month_expenses['Amount'].sum()
            avg_transaction = expenses_df['Amount'].mean()
            most_freq_cat = expenses_df['Category'].mode()[0] if not expenses_df['Category'].empty else "N/A"

            col1, col2, col3, col4 = st.columns(4)
            with col1: st.markdown(f'<div class="metric-card"><h3>Total Spent</h3><p>₹{total_spent:,.2f}</p></div>', unsafe_allow_html=True)
            with col2: st.markdown(f'<div class="metric-card"><h3>Spent This Month</h3><p>₹{monthly_spent:,.2f}</p></div>', unsafe_allow_html=True)
            with col3: st.markdown(f'<div class="metric-card"><h3>Avg. Transaction</h3><p>₹{avg_transaction:,.2f}</p></div>', unsafe_allow_html=True)
            with col4: st.markdown(f'<div class="metric-card"><h3>Favorite Category</h3><p>{most_freq_cat}</p></div>', unsafe_allow_html=True)
            st.markdown("---")

            st.header("Recent Transactions")
            st.dataframe(expenses_df.drop(columns=['username']).sort_values('Date', ascending=False).head(10), use_container_width=True)
        
        else:
            st.info("No expenses recorded yet. Add one from the sidebar to get started!")

    with tab2:
        st.header("Deep Dive into Your Spending")
        if not expenses_df.empty:
            all_charts = get_all_charts(expenses_df)
            total_pages = (len(all_charts) + 2) // 3
            st.session_state.chart_page %= total_pages
            
            start_idx = st.session_state.chart_page * 3
            end_idx = start_idx + 3
            charts_to_show = all_charts[start_idx:end_idx]
            
            if charts_to_show:
                cols = st.columns(len(charts_to_show))
                for i, (title, chart) in enumerate(charts_to_show):
                    with cols[i]:
                        st.subheader(title)
                        chart.update_layout(paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0.2)', font_color='white', legend=dict(font=dict(color="white")))
                        st.plotly_chart(chart, use_container_width=True)
            
            col1, col2, col3 = st.columns([1, 1, 1])
            if col1.button("⬅️ Previous Charts", use_container_width=True):
                st.session_state.chart_page = (st.session_state.chart_page - 1 + total_pages) % total_pages
                st.rerun()
            if col3.button("Next Charts ➡️", use_container_width=True):
                st.session_state.chart_page = (st.session_state.chart_page + 1) % total_pages
                st.rerun()
        else:
            st.info("Add some expenses to see your personalized visualizations!")

    with tab3:
        st.header("Connect with the Developer")
        col1, col2, col3 = st.columns([1, 2, 1])
        with col2:
            st.markdown("""
            <div style="text-align: center; font-size: 1.1rem;">
                <p>Hope you are enjoying this Pocket Expense Tracker!</p>
                <a href="https://in.linkedin.com/in/shatarudra-prakash-singh-313956299" target="_blank" style="text-decoration: none; color: #DA70D6; font-size: 1.5rem; font-weight: bold;">🔗 LinkedIn</a>
                <br><br>
                <a href="https://instagram.com/shatarudra_92" target="_blank" style="text-decoration: none; color: #DA70D6; font-size: 1.5rem; font-weight: bold;">📸 Instagram</a>
            </div>
            """, unsafe_allow_html=True)


# --- Step 9: Main Application Router ---
if st.session_state.logged_in:
    show_dashboard()
else:
    show_login_signup()