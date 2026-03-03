import streamlit as st
import math
import numpy as np 
import matplotlib.pyplot as plt

# Set page configuration
st.set_page_config(
    page_title="Little's Law Queue Calculator",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Streamlit app title
st.title("📊 Little's Law Queue Calculator")

# Put on sidebar
with st.sidebar:
    st.header("User Inputs")

    st.markdown("""
    **Little's Law**:  
                
    $L = \lambda W$  
    
    Where:
    - **L** = Average number of patients in the system  
    - **λ** = Average arrival rate (new patients per week)  
    - **W** = Average time in the system (weeks)
    """)

    st.divider()

    # User selects which variable to calculate
    calc_choice = st.selectbox(
        "Which variable do you want to calculate?",
        ("L (Average number in system)", "λ (Arrival rate)", "W (Average time in system)")
    )

    # Set λ, W to 1 by default, for error handling
    lam = 1.0
    W = 1.0

    # Input fields with validation
    try:
        if calc_choice == "L (Average number in system)":
            lam = st.number_input("Enter λ (Arrival rate)", min_value=0.0, format="%.0f")
            W = st.number_input("Enter W (Average wait time)", min_value=0.0, format="%.0f")
            if lam > 0 and W > 0:
                L = lam * W
                st.success(f"📈 L = {L:.0f} patients")
        
        elif calc_choice == "λ (Arrival rate)":
            L = st.number_input("Enter L (Average waiting list size)", min_value=0.0, format="%.0f")
            W = st.number_input("Enter W (Average wait time - weeks)", min_value=0.0, format="%.0f")
            if L > 0 and W > 0:
                lam = L / W
                st.success(f"📈 λ = {lam:.0f} new patients/week")
            else:
                st.warning("Please enter positive values for L and W.")
        
        elif calc_choice == "W (Average wait time)":
            L = st.number_input("Enter L (Average waiting list size)", min_value=0.0, format="%.0f")
            lam = st.number_input("Enter λ (Arrival rate)", min_value=0.0, format="%.0f")
            if L > 0 and lam > 0:
                W = L / lam
                st.success(f"📈 W = {W:.0f} weeks")

    except ValueError as e:
        st.error(f"Error: {e}")

    st.divider()

    # Add section to calculate number of cases in system to meet 1% service level

    # if L > 0 and W > 0:
    arrival_rate = lam  # Using the arrival rate from user input

    percentile = st.slider( 
        "Target percentile (e.g., 95 means 95% wait less than T):", 
        min_value=50, 
        max_value=99, 
        value=95 
        )

    target_time = st.number_input( 
        "Target maximum waiting time T (weeks):", 
        min_value=0.1, 
        value=6.0, 
        step=0.5 
        )

q = percentile / 100.0 

st.markdown("""
    Arrival rate 𝜆: average number of new cases per week.

    Service rate 𝜇: average number of cases completed per per week.
    """)

# Required gap μ - λ 
mu_minus_lambda = -math.log(1 - q) / target_time 

# Required service rate 
service_rate = arrival_rate + mu_minus_lambda 

# Queue metrics 
L = arrival_rate / mu_minus_lambda 
Lq = (arrival_rate**2) / (service_rate * mu_minus_lambda) 

# Expected breaches 
breach_rate = 1 - q 
breaches_per_week = arrival_rate * breach_rate 
breaches_over_window = breaches_per_week * target_time

st.divider()

# Create columns for outputs
col1, col2, col3 = st.columns(3)

# --- Output --- 
st.header("Results") 
col1.metric("Required service rate μ (per week)", f"{service_rate:.0f}") 
col2.metric("Size of waiting list required L", f"{L:.0f}") 
col3.metric("Average queue length Lq (waiting only)", f"{Lq:.0f}")

st.subheader("Expected Breaches") 
col1.metric("Breaches per week", f"{breaches_per_week:.0f}") 
col2.metric(f"Breaches over {target_time} weeks", f"{breaches_over_window:.0f}")

# Create columns for visuals
col1, col2, col3 = st.columns(3)

with col1:
    # --- Visual 1: Waiting time distribution --- 
    st.subheader("Waiting Time Distribution") 

    t_vals = np.linspace(0, target_time * 3, 200) 
    survival = np.exp(-(mu_minus_lambda) * t_vals) 

    fig1, ax1 = plt.subplots() 
    ax1.plot(t_vals, survival) 
    ax1.axvline(target_time, color='red', linestyle='--', label=f"T = {target_time} weeks") 
    ax1.set_xlabel("Waiting time (weeks)") 
    ax1.set_ylabel("P(W > t)") 
    ax1.set_title("Survival Function of Waiting Time") 
    ax1.legend() 
    st.pyplot(fig1)

    st.markdown("""
                𝑃(𝑊>𝑡)=𝑒−(𝜇−𝜆)𝑡"
                
                What this chart shows:  
                This curve shows the chance that someone will still be waiting 
                after a certain number of weeks. As you move to the right, the 
                line drops — meaning fewer and fewer people wait that long.
                """
                )

with col2:
    # --- Visual 2: Queue size vs service rate --- 
    st.subheader("Queue Size vs Service Rate") 

    mu_values = np.linspace(arrival_rate + 0.01, arrival_rate + 5, 200) 
    L_values = arrival_rate / (mu_values - arrival_rate) 

    fig2, ax2 = plt.subplots() 
    ax2.plot(mu_values, L_values) 
    ax2.axvline(service_rate, color='red', linestyle='--', label="Required μ") 
    ax2.set_xlabel("Service rate μ") 
    ax2.set_ylabel("Average number in system L") 
    ax2.set_title("Queue Size Explosion as μ Approaches λ") 
    ax2.set_ylim(0, min(max(L_values), 500)) 
    ax2.legend() 
    st.pyplot(fig2)

with col3:
    # --- Visual 3: Breaches over time --- 
    st.subheader("Expected Breaches Over Time") 

    weeks = np.arange(1, int(target_time) + 1) 
    breach_counts = breaches_per_week * weeks 

    fig3, ax3 = plt.subplots() 
    ax3.plot(weeks, breach_counts, marker='o') 
    ax3.set_xlabel("Weeks") 
    ax3.set_ylabel("Cumulative breaches") 
    ax3.set_title("Breaches Accumulated Over Target Window") 
    st.pyplot(fig3)