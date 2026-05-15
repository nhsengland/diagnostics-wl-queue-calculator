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

    # Toggle between static and variable arrival rates
    arrival_type = st.radio(
        "Arrival Rate Type",
        ("Static (constant rate)", "Variable (non-static rate)")
    )

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
        if arrival_type == "Static (constant rate)":
            # Static lambda input
            if calc_choice == "L (Average number in system)":
                lam = st.number_input("Enter λ (Average arrivals per week)", min_value=0.0, format="%.0f")
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

        else:  # Variable arrival rate
            st.info("📊 Enter arrival rates for different time periods")
            
            num_periods = st.number_input("Number of time periods:", min_value=1, max_value=12, value=4)
            
            periods_data = []
            col_labels = st.columns(3)
            with col_labels[0]:
                st.markdown("**Period Name**")
            with col_labels[1]:
                st.markdown("**Duration (weeks)**")
            with col_labels[2]:
                st.markdown("**Average arrivals per week**")
            
            for i in range(num_periods):
                col1, col2, col3 = st.columns(3)
                with col1:
                    period_name = st.text_input(f"Period {i+1}", value=f"Period {i+1}", key=f"period_name_{i}")
                with col2:
                    duration = st.number_input(f"Duration {i+1} (weeks)", min_value=0.1, value=4.0, step=0.5, key=f"duration_{i}")
                with col3:
                    rate = st.number_input(f"Rate {i+1} (per week)", min_value=0.0, value=10.0, format="%.2f", key=f"rate_{i}")
                
                periods_data.append({
                    "name": period_name,
                    "duration": duration,
                    "rate": rate
                })
            
            # Store in session state for use in chart at bottom
            st.session_state.periods_data = periods_data
            
            # Calculate weighted average lambda
            total_weighted_arrivals = sum(p["duration"] * p["rate"] for p in periods_data)
            total_duration = sum(p["duration"] for p in periods_data)
            lam = total_weighted_arrivals / total_duration if total_duration > 0 else 1.0
            
            st.success(f"📈 Weighted Average λ = {lam:.2f} patients/week")
            
            # Display breakdown
            st.markdown("**Variable Arrival Rate Breakdown:**")
            breakdown_data = []
            for p in periods_data:
                total_arrivals = p["duration"] * p["rate"]
                pct = (total_arrivals / total_weighted_arrivals * 100) if total_weighted_arrivals > 0 else 0
                breakdown_data.append({
                    "Period": p["name"],
                    "Duration (weeks)": p["duration"],
                    "Rate (per week)": f"{p['rate']:.2f}",
                    "Total Arrivals": f"{total_arrivals:.0f}",
                    "% of Total": f"{pct:.1f}%"
                })
            
            st.dataframe(breakdown_data, use_container_width=True)
            
            # Now handle the calculation choice with weighted average lambda
            if calc_choice == "L (Average number in system)":
                W = st.number_input("Enter W (Average wait time)", min_value=0.0, format="%.2f")
                if lam > 0 and W > 0:
                    L = lam * W
                    st.success(f"📈 L = {L:.0f} patients (using weighted average λ)")
            
            elif calc_choice == "λ (Arrival rate)":
                st.info(f"✓ Weighted average λ calculated from periods: {lam:.2f} patients/week")
            
            elif calc_choice == "W (Average wait time)":
                L = st.number_input("Enter L (Average waiting list size)", min_value=0.0, format="%.0f")
                if L > 0 and lam > 0:
                    W = L / lam
                    st.success(f"📈 W = {W:.2f} weeks (using weighted average λ)")

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

# --- Visual 4: Variable Arrival Rates Chart (if applicable) ---
if 'periods_data' in st.session_state and len(st.session_state.periods_data) > 0:
    st.divider()
    st.subheader("Variable Arrival Rates Over Time")
    
    periods_data = st.session_state.periods_data
    
    # Create time series data
    period_names = [p["name"] for p in periods_data]
    arrival_rates = [p["rate"] for p in periods_data]
    
    fig4, ax4 = plt.subplots(figsize=(10, 5))
    ax4.bar(period_names, arrival_rates, color='steelblue', edgecolor='black', alpha=0.7)
    ax4.axhline(lam, color='red', linestyle='--', linewidth=2, label=f"Weighted Average λ = {lam:.2f}")
    ax4.set_xlabel("Period")
    ax4.set_ylabel("Arrival Rate (cases per week)")
    ax4.set_title("Arrival Rate Distribution Across Periods")
    ax4.legend()
    ax4.grid(axis='y', alpha=0.3)
    st.pyplot(fig4)