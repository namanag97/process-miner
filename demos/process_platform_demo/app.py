"""
Process Mining Platform - Technology Demo (Enhanced)
Main Streamlit Application

Run with: streamlit run app.py
"""
import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime
import json

# Page configuration
st.set_page_config(
    page_title="Process Mining Tech Demo",
    page_icon="⚙️",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS
st.markdown("""
<style>
    .main-header {
        font-size: 2.5rem;
        font-weight: 700;
        background: linear-gradient(90deg, #667eea, #764ba2);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        margin-bottom: 0.5rem;
    }
    .sub-header {
        font-size: 1.2rem;
        color: #6b7280;
        margin-bottom: 2rem;
    }
    .metric-card {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        border-radius: 10px;
        padding: 1.5rem;
        color: white;
    }
    .stTabs [data-baseweb="tab-list"] {
        gap: 24px;
    }
    .stTabs [data-baseweb="tab"] {
        font-weight: 600;
    }
</style>
""", unsafe_allow_html=True)


# Dataset loading with caching
@st.cache_data
def load_dataset(dataset_name: str, n_cases: int = 300):
    """Load dataset from the dataset loader."""
    from utils.datasets import DatasetLoader
    return DatasetLoader.load_dataset(dataset_name, n_cases=n_cases)


@st.cache_data
def get_dataset_stats(df):
    """Get statistics for a dataset."""
    from utils.datasets import get_dataset_statistics
    return get_dataset_statistics(df)


def render_dataset_selector():
    """Render dataset selector in sidebar."""
    from utils.datasets import DatasetLoader
    
    datasets = DatasetLoader.list_datasets()
    
    st.sidebar.markdown("### 📊 Dataset")
    selected_dataset = st.sidebar.selectbox(
        "Select Dataset",
        options=list(datasets.keys()),
        format_func=lambda x: x.replace("_", " ").title()
    )
    
    n_cases = st.sidebar.slider("Number of Cases", 100, 1000, 300, 50)
    
    return selected_dataset, n_cases


def render_predictive_demo(event_log):
    """Render predictive analytics demo with step-by-step progress."""
    st.header("🔮 Predictive Process Analytics")
    st.caption("Using Machine Learning to predict process outcomes, next activities, and remaining time")
    
    st.markdown("---")
    
    # Step-by-step execution
    if st.button("▶️ Run Predictive Analysis", type="primary", use_container_width=True):
        
        # Create progress container
        progress_container = st.container()
        results_container = st.container()
        
        with progress_container:
            progress_bar = st.progress(0, text="Starting...")
            status_area = st.empty()
            
            import time
            from demos.predictive import ProcessPredictor
            
            try:
                predictor = ProcessPredictor()
                
                # STEP 1: Feature Extraction
                progress_bar.progress(10, text="Step 1/6: Extracting features from event log...")
                status_area.info(f"""
                📊 **Extracting Features**
                - Analyzing {len(event_log):,} events from {event_log['case_id'].nunique():,} cases
                - Creating prefix-based features (what happened before each event)
                - Features: activity sequence, order value, priority, region, deviations
                """)
                time.sleep(0.5)
                
                features_df = predictor.prepare_features(event_log)
                status_area.success(f"✅ Extracted {len(features_df):,} training samples with 7 features each")
                time.sleep(0.3)
                
                # STEP 2: Encode Features
                progress_bar.progress(25, text="Step 2/6: Encoding categorical features...")
                status_area.info("""
                🔢 **Encoding Features for ML**
                - Converting activities to numbers (Label Encoding)
                - Scaling numerical features (StandardScaler)
                - Preparing train/test split (80/20)
                """)
                time.sleep(0.5)
                
                # STEP 3: Train Outcome Model
                progress_bar.progress(40, text="Step 3/6: Training outcome prediction model...")
                status_area.info("""
                🌲 **Training Outcome Model**
                - Algorithm: Random Forest Classifier (100 trees)
                - Target: Will case complete successfully? (Yes/No)
                - Training on historical completion data...
                """)
                time.sleep(0.3)
                
                outcome_results = predictor.train_outcome_model(event_log)
                status_area.success(f"✅ Outcome model trained - Accuracy: {outcome_results['accuracy']*100:.1f}%")
                time.sleep(0.3)
                
                # STEP 4: Train Next Activity Model
                progress_bar.progress(60, text="Step 4/6: Training next activity model...")
                status_area.info(f"""
                🌲 **Training Next Activity Model**
                - Algorithm: Random Forest Classifier (100 trees)
                - Target: Predict next activity from {event_log['activity'].nunique()} possible activities
                - Learning activity transition patterns...
                """)
                time.sleep(0.3)
                
                next_act_results = predictor.train_next_activity_model(event_log)
                status_area.success(f"✅ Next activity model trained - Accuracy: {next_act_results['accuracy']*100:.1f}%")
                time.sleep(0.3)
                
                # STEP 5: Train Time Model
                progress_bar.progress(80, text="Step 5/6: Training remaining time model...")
                status_area.info("""
                📈 **Training Time Prediction Model**
                - Algorithm: Gradient Boosting Regressor (100 estimators)
                - Target: Predict remaining hours until completion
                - Learning duration patterns from historical data...
                """)
                time.sleep(0.3)
                
                time_results = predictor.train_time_model(event_log)
                status_area.success(f"✅ Time model trained - MAE: {time_results['mae_hours']:.1f} hours")
                time.sleep(0.3)
                
                # STEP 6: Make Sample Prediction
                progress_bar.progress(95, text="Step 6/6: Making sample prediction...")
                status_area.info("""
                🎯 **Making Live Prediction**
                - Simulating a running case at "Stock Check" activity
                - Applying all 3 trained models
                - Generating predictions...
                """)
                time.sleep(0.3)
                
                sample_case = {
                    'prefix_length': 3,
                    'current_activity': 'Stock Check',
                    'order_value': 5000,
                    'priority': 'High',
                    'region': 'North',
                    'num_unique_activities': 3,
                    'has_deviation': False
                }
                prediction = predictor.predict_case(sample_case)
                
                progress_bar.progress(100, text="✅ Analysis Complete!")
                status_area.success("🎉 **All models trained and prediction generated!**")
                time.sleep(0.5)
                
                # Clear progress and show results
                progress_bar.empty()
                status_area.empty()
                
                with results_container:
                    st.success("### ✅ Analysis Results")
                    
                    # Model Performance
                    st.subheader("📊 Model Performance")
                    col1, col2, col3 = st.columns(3)
                    
                    with col1:
                        acc = outcome_results['accuracy']*100
                        st.metric("Outcome Prediction", f"{acc:.1f}%", 
                                 delta="Good" if acc > 80 else "Acceptable")
                        st.caption("Can predict if case will complete")
                    
                    with col2:
                        acc = next_act_results['accuracy']*100
                        st.metric("Next Activity", f"{acc:.1f}%",
                                 delta="Good" if acc > 70 else "Acceptable")
                        st.caption("Can predict next step in process")
                    
                    with col3:
                        mae = time_results['mae_hours']
                        st.metric("Time Prediction", f"{mae:.1f}h MAE",
                                 delta="Good" if mae < 24 else "Moderate")
                        st.caption("Average prediction error")
                    
                    st.markdown("---")
                    
                    # Live Prediction
                    st.subheader("🎯 Sample Prediction")
                    st.markdown("""
                    **Scenario:** A case currently at "Stock Check" activity with a $5,000 High-priority order from the North region.
                    """)
                    
                    col1, col2, col3 = st.columns(3)
                    with col1:
                        prob = prediction.get('completion_probability', 0)*100
                        st.metric("Completion Probability", f"{prob:.0f}%")
                        if prob > 80:
                            st.success("✅ Likely to complete")
                        elif prob > 50:
                            st.warning("⚠️ Monitor this case")
                        else:
                            st.error("🚨 High risk")
                    
                    with col2:
                        st.metric("Next Activity", prediction.get('next_activity', 'N/A'))
                        if 'next_activity_probabilities' in prediction:
                            st.caption("Confidence:")
                            for act, p in list(prediction['next_activity_probabilities'].items())[:3]:
                                st.progress(p, text=f"{act}: {p*100:.0f}%")
                    
                    with col3:
                        hours = prediction.get('remaining_time_hours', 0)
                        st.metric("Time to Complete", f"{hours:.1f}h")
                        if hours < 24:
                            st.success("Complete today")
                        else:
                            st.info(f"~{hours/24:.0f} days")
                    
                    # Animated Feature Importance
                    st.markdown("---")
                    st.subheader("🎥 Algorithm Visualization")
                    st.caption("Watch how the ML model learns feature importance during training")
                    
                    try:
                        from demos.animations import create_animated_feature_importance
                        feature_names = ['Prefix Len', 'Activity', 'Value', 'Priority', 'Region', 'Unique Acts', 'Deviation']
                        anim_fig = create_animated_feature_importance(feature_names, iterations=15)
                        st.plotly_chart(anim_fig, use_container_width=True)
                    except Exception as anim_err:
                        st.warning(f"Animation not available: {anim_err}")
                    
            except Exception as e:
                progress_bar.empty()
                status_area.error(f"❌ Error: {e}")
                st.exception(e)
    else:
        st.info("👆 Click the button above to start the predictive analysis. Watch the step-by-step progress!")


def render_simulation_demo():
    """Render process simulation demo with step-by-step progress."""
    st.header("🎮 Process Simulation (Digital Twin)")
    st.caption("Simulate process changes using Discrete Event Simulation (SimPy)")
    
    st.markdown("---")
    
    if st.button("▶️ Run Simulation", type="primary", use_container_width=True):
        import time
        
        progress_bar = st.progress(0, text="Initializing simulation...")
        status_area = st.empty()
        
        try:
            from demos.simulation import SimulationConfig, ProcessSimulator, compare_scenarios
            
            # STEP 1: Setup baseline
            progress_bar.progress(10, text="Step 1/5: Setting up baseline scenario...")
            status_area.info("""
            🏭 **Setting Up Baseline Scenario**
            - 3 Clerks, 2 Credit Checkers, 4 Warehouse Staff, 2 Shippers
            - Simulating 1 week (168 hours) of operation
            - Arrival rate: 2 cases per hour
            """)
            time.sleep(0.5)
            
            base_config = SimulationConfig()
            
            # STEP 2: Run baseline simulation
            progress_bar.progress(30, text="Step 2/5: Running baseline simulation...")
            status_area.info("""
            ⏱️ **Running Baseline Simulation**
            - Processing cases through Order-to-Cash flow
            - Tracking cycle times, wait times, resource usage
            - SimPy discrete event simulation in progress...
            """)
            
            baseline_sim = ProcessSimulator(base_config)
            baseline_result = baseline_sim.run()
            status_area.success(f"✅ Baseline: {baseline_result.total_cases} cases processed, avg {baseline_result.avg_cycle_time/24:.1f} days")
            time.sleep(0.3)
            
            # STEP 3: Run alternative scenarios
            progress_bar.progress(50, text="Step 3/5: Running 'More Credit Checkers' scenario...")
            status_area.info("""
            👥 **Testing: More Credit Checkers (4 instead of 2)**
            - Hypothesis: Credit check is a bottleneck
            - Testing impact of doubling capacity...
            """)
            
            more_credit_config = SimulationConfig(num_credit_checkers=4)
            more_credit_sim = ProcessSimulator(more_credit_config)
            more_credit_result = more_credit_sim.run()
            status_area.success(f"✅ More Credit Checkers: avg {more_credit_result.avg_cycle_time/24:.1f} days")
            time.sleep(0.3)
            
            progress_bar.progress(70, text="Step 4/5: Running 'More Warehouse Staff' scenario...")
            status_area.info("""
            📦 **Testing: More Warehouse Staff (6 instead of 4)**
            - Hypothesis: Warehouse processing is slow
            - Testing impact of 50% more capacity...
            """)
            
            more_warehouse_config = SimulationConfig(num_warehouse_staff=6)
            more_warehouse_sim = ProcessSimulator(more_warehouse_config)
            more_warehouse_result = more_warehouse_sim.run()
            status_area.success(f"✅ More Warehouse Staff: avg {more_warehouse_result.avg_cycle_time/24:.1f} days")
            time.sleep(0.3)
            
            progress_bar.progress(90, text="Step 5/5: Comparing scenarios...")
            status_area.info("""
            📊 **Analyzing Results**
            - Comparing cycle times across scenarios
            - Identifying resource utilization patterns
            - Finding optimal configuration...
            """)
            time.sleep(0.5)
            
            progress_bar.progress(100, text="✅ Simulation Complete!")
            status_area.success("🎉 **All scenarios simulated!**")
            time.sleep(0.3)
            progress_bar.empty()
            status_area.empty()
            
            # Show results
            st.success("### ✅ Simulation Results")
            
            st.subheader("📊 Scenario Comparison")
            comparison_data = [
                {"Scenario": "Baseline", "Cases": baseline_result.total_cases, 
                 "Avg Cycle (days)": round(baseline_result.avg_cycle_time/24, 2),
                 "Throughput/day": round(baseline_result.throughput_per_hour*24, 1),
                 "Bottleneck": baseline_result.bottleneck},
                {"Scenario": "More Credit Checkers", "Cases": more_credit_result.total_cases,
                 "Avg Cycle (days)": round(more_credit_result.avg_cycle_time/24, 2),
                 "Throughput/day": round(more_credit_result.throughput_per_hour*24, 1),
                 "Bottleneck": more_credit_result.bottleneck},
                {"Scenario": "More Warehouse Staff", "Cases": more_warehouse_result.total_cases,
                 "Avg Cycle (days)": round(more_warehouse_result.avg_cycle_time/24, 2),
                 "Throughput/day": round(more_warehouse_result.throughput_per_hour*24, 1),
                 "Bottleneck": more_warehouse_result.bottleneck}
            ]
            
            df = pd.DataFrame(comparison_data)
            st.dataframe(df, use_container_width=True)
            
            # Best scenario recommendation
            best = min(comparison_data, key=lambda x: x["Avg Cycle (days)"])
            if best["Scenario"] != "Baseline":
                st.success(f"💡 **Recommendation:** {best['Scenario']} reduces cycle time by {comparison_data[0]['Avg Cycle (days)'] - best['Avg Cycle (days)']:.1f} days!")
            
            # Resource utilization chart
            st.subheader("📈 Resource Utilization (Baseline)")
            util_data = baseline_result.resource_utilization
            
            fig = go.Figure(go.Bar(
                x=list(util_data.keys()),
                y=[v*100 for v in util_data.values()],
                marker_color=['#4CAF50' if v < 0.8 else '#FF5722' for v in util_data.values()]
            ))
            fig.update_layout(title="Resource Utilization (%)", yaxis_range=[0, 100])
            st.plotly_chart(fig, use_container_width=True)
            st.caption("🔴 Red = Over 80% utilization (potential bottleneck)")
            
            # Animated Simulation Flow
            st.markdown("---")
            st.subheader("🎥 Algorithm Visualization")
            st.caption("Watch cases flow through the process activities in the simulation")
            
            try:
                from demos.animations import create_animated_simulation_flow
                activities = ["Order", "Credit", "Warehouse", "Ship", "Invoice", "Pay"]
                anim_fig = create_animated_simulation_flow(n_cases=15, activities=activities)
                st.plotly_chart(anim_fig, use_container_width=True)
            except Exception as anim_err:
                st.warning(f"Animation not available: {anim_err}")
            
        except Exception as e:
            progress_bar.empty()
            status_area.error(f"❌ Error: {e}")
            st.exception(e)
    else:
        st.info("👆 Click to simulate 1 week of process operations with different resource configurations")


def render_conformance_demo(event_log):
    """Render conformance checking demo with step-by-step progress."""
    st.header("✅ Conformance Checking")
    st.caption("Check process conformance against business rules and expected flows")
    
    st.markdown("---")
    
    if st.button("▶️ Check Conformance", type="primary", use_container_width=True):
        import time
        
        progress_bar = st.progress(0, text="Starting conformance check...")
        status_area = st.empty()
        
        try:
            from demos.conformance import create_o2c_conformance_checker, ConformanceChecker
            
            # STEP 1: Setup rules
            progress_bar.progress(15, text="Step 1/4: Defining business rules...")
            status_area.info("""
            📋 **Defining Business Rules**
            - Precedence: Credit Check must occur before Release Order
            - Precedence: Ship Goods must occur before Create Invoice
            - Response: Every Order must eventually receive Payment
            - Cardinality: Credit Check should occur 1-2 times only
            - Time SLA: Order to Credit Check within 24 hours
            """)
            time.sleep(0.5)
            
            checker = create_o2c_conformance_checker()
            status_area.success(f"✅ Defined {len(checker.rules)} business rules")
            time.sleep(0.3)
            
            # STEP 2: Check each case
            progress_bar.progress(40, text="Step 2/4: Checking cases against rules...")
            status_area.info(f"""
            🔍 **Checking {event_log['case_id'].nunique():,} Cases**
            - Analyzing each case's activity sequence
            - Checking precedence constraints
            - Validating response requirements
            - Checking time constraints...
            """)
            time.sleep(0.5)
            
            result = checker.check_conformance(event_log)
            status_area.success(f"✅ Found {result.non_conformant_cases} non-conformant cases")
            time.sleep(0.3)
            
            # STEP 3: Analyze deviations
            progress_bar.progress(70, text="Step 3/4: Analyzing deviations...")
            status_area.info("""
            ⚠️ **Analyzing Deviations**
            - Categorizing violation types
            - Counting occurrences per rule
            - Identifying severity levels...
            """)
            time.sleep(0.5)
            
            # STEP 4: Generate report
            progress_bar.progress(90, text="Step 4/4: Generating report...")
            deviation_df = checker.get_deviation_report(result)
            
            progress_bar.progress(100, text="✅ Conformance Check Complete!")
            status_area.success("🎉 **Analysis complete!**")
            time.sleep(0.3)
            progress_bar.empty()
            status_area.empty()
            
            # Show results
            st.success("### ✅ Conformance Results")
            
            col1, col2, col3, col4 = st.columns(4)
            with col1:
                fitness = result.fitness * 100
                st.metric("Fitness Score", f"{fitness:.1f}%",
                         delta="Good" if fitness > 80 else "Needs attention")
            with col2:
                precision = result.precision * 100
                st.metric("Precision Score", f"{precision:.1f}%")
            with col3:
                st.metric("Conformant Cases", result.conformant_cases)
            with col4:
                st.metric("Non-Conformant", result.non_conformant_cases)
            
            st.markdown("---")
            
            # Rules checked
            st.subheader("📋 Rules Checked")
            rules_data = [{"name": r.name, "description": r.description, "type": r.rule_type} for r in checker.rules]
            st.dataframe(pd.DataFrame(rules_data), use_container_width=True)
            
            # Deviations
            if result.deviation_types:
                st.subheader("⚠️ Deviations Found")
                fig = px.bar(x=list(result.deviation_types.keys()), y=list(result.deviation_types.values()))
                st.plotly_chart(fig, use_container_width=True)
                
                with st.expander("View Sample Violations"):
                    st.dataframe(deviation_df.head(20))
            else:
                st.success("✅ No deviations found!")
                
        except Exception as e:
            progress_bar.empty()
            status_area.error(f"❌ Error: {e}")
            st.exception(e)
    else:
        st.info("👆 Click to check if your process follows the expected business rules")


def render_optimization_demo():
    """Render optimization demo with step-by-step progress."""
    st.header("📊 Process Optimization")
    st.caption("Optimize resource allocation using Linear Programming (PuLP)")
    
    st.markdown("---")
    
    if st.button("▶️ Run Optimization", type="primary", use_container_width=True):
        import time
        
        progress_bar = st.progress(0, text="Setting up optimization...")
        status_area = st.empty()
        
        try:
            from demos.optimization import StaffingOptimizer, StaffingProblem, SLAOptimizer
            
            # STEP 1: Define staffing problem
            progress_bar.progress(15, text="Step 1/4: Defining staffing problem...")
            status_area.info("""
            📝 **Defining Optimization Problem**
            - Shifts: Morning, Afternoon, Evening, Night
            - Demand: 8, 12, 6, 3 staff per shift
            - Cost: $25-35/hour depending on shift
            - Objective: Minimize total labor cost
            """)
            time.sleep(0.5)
            
            problem = StaffingProblem(
                shifts=["Morning", "Afternoon", "Evening", "Night"],
                demand={"Morning": 8, "Afternoon": 12, "Evening": 6, "Night": 3},
                cost_per_hour={"Morning": 25, "Afternoon": 25, "Evening": 30, "Night": 35}
            )
            
            # STEP 2: Solve staffing optimization
            progress_bar.progress(40, text="Step 2/4: Solving staffing optimization...")
            status_area.info("""
            🧮 **Solving Linear Program**
            - Using PuLP CBC solver
            - Decision: How many staff per shift?
            - Constraints: Meet minimum demand
            - Finding minimum cost solution...
            """)
            time.sleep(0.5)
            
            optimizer = StaffingOptimizer(problem)
            staffing_result = optimizer.solve()
            status_area.success(f"✅ Found optimal solution: {staffing_result.total_staff} staff, ${staffing_result.total_cost:,.0f}/day")
            time.sleep(0.3)
            
            # STEP 3: SLA Optimization
            progress_bar.progress(70, text="Step 3/4: Running SLA optimization...")
            status_area.info("""
            ⏱️ **SLA Optimization Problem**
            - Backlog: 100 cases waiting
            - SLA Target: Complete within 8 hours
            - Staff productivity: 3 cases/hour
            - Breach penalty: $500 per case
            """)
            time.sleep(0.5)
            
            sla_optimizer = SLAOptimizer()
            sla_result = sla_optimizer.optimize_for_sla(
                current_backlog=100, sla_hours=8,
                productivity_per_staff=3, staff_cost=30, sla_breach_penalty=500
            )
            status_area.success(f"✅ SLA optimal: {sla_result['optimal_staff']} staff needed")
            time.sleep(0.3)
            
            progress_bar.progress(100, text="✅ Optimization Complete!")
            status_area.success("🎉 **All optimizations solved!**")
            time.sleep(0.3)
            progress_bar.empty()
            status_area.empty()
            
            # Show results
            st.success("### ✅ Optimization Results")
            
            st.subheader("1️⃣ Staffing Optimization")
            col1, col2 = st.columns(2)
            with col1:
                st.metric("Total Daily Cost", f"${staffing_result.total_cost:,.2f}")
                st.metric("Total Staff Needed", staffing_result.total_staff)
                st.caption(f"Status: {staffing_result.status}")
            with col2:
                fig = px.pie(values=list(staffing_result.optimal_staffing.values()),
                            names=list(staffing_result.optimal_staffing.keys()),
                            title="Staff by Shift")
                st.plotly_chart(fig, use_container_width=True)
            
            st.markdown("---")
            st.subheader("2️⃣ SLA Optimization")
            col1, col2, col3 = st.columns(3)
            with col1:
                st.metric("Optimal Staff", sla_result['optimal_staff'])
            with col2:
                breaches = int(sla_result['expected_breaches'])
                st.metric("Expected Breaches", breaches, delta="Good" if breaches == 0 else None)
            with col3:
                st.metric("Total Cost", f"${sla_result['total_cost']:,.2f}")
            st.caption(f"Capacity: {sla_result['processing_capacity']:.0f} cases in 8 hours")
            
        except Exception as e:
            progress_bar.empty()
            status_area.error(f"❌ Error: {e}")
            st.exception(e)
    else:
        st.info("👆 Click to find the optimal resource allocation that minimizes cost while meeting demand")


def render_document_demo():
    """Render IDP demo with step-by-step progress."""
    st.header("📄 Intelligent Document Processing")
    st.caption("Extract structured data using NLP (spaCy) and regex patterns")
    
    st.markdown("---")
    
    sample_invoice = st.text_area(
        "📝 Invoice Text (edit to test extraction)",
        value="""INVOICE
Invoice Number: INV-2024-00789
Date: December 28, 2024
Bill To: Acme Corporation

Description                     Qty    Unit Price    Amount
Professional Services           10     $150.00       $1,500.00
Software License               1      $2,500.00     $2,500.00

Subtotal: $4,000.00 | Tax (8%): $320.00 | TOTAL: $4,320.00
Payment Terms: Net 30""",
        height=200
    )
    
    if st.button("🔍 Process Document", type="primary", use_container_width=True):
        import time
        
        progress_bar = st.progress(0, text="Starting document processing...")
        status_area = st.empty()
        
        try:
            from demos.document import DocumentProcessor, InvoiceProcessor
            
            # STEP 1: Document Classification
            progress_bar.progress(20, text="Step 1/4: Classifying document type...")
            status_area.info("""
            📑 **Document Classification**
            - Scanning for keywords: invoice, purchase order, contract, receipt
            - Using keyword-based classification
            - Determining document type...
            """)
            time.sleep(0.4)
            
            processor = InvoiceProcessor()
            doc_type = processor.classify_document(sample_invoice)
            status_area.success(f"✅ Document type: {doc_type}")
            time.sleep(0.3)
            
            # STEP 2: Key-Value Extraction
            progress_bar.progress(45, text="Step 2/4: Extracting key fields with regex...")
            status_area.info("""
            🔤 **Key-Value Extraction (Regex)**
            - Searching for invoice number pattern
            - Extracting dates (Date, Due Date)
            - Finding amounts (Subtotal, Tax, Total)
            - Identifying payment terms...
            """)
            time.sleep(0.4)
            
            key_values = processor.extract_key_values(sample_invoice)
            status_area.success(f"✅ Extracted {len(key_values)} key fields")
            time.sleep(0.3)
            
            # STEP 3: NLP Entity Extraction
            progress_bar.progress(70, text="Step 3/4: Running NLP entity extraction...")
            status_area.info("""
            🧠 **NLP Entity Extraction (spaCy)**
            - Loading en_core_web_sm model
            - Running Named Entity Recognition (NER)
            - Finding: ORG, PERSON, DATE, MONEY entities...
            """)
            time.sleep(0.4)
            
            entities = processor.extract_entities_spacy(sample_invoice)
            status_area.success(f"✅ Found {len(entities)} entities")
            time.sleep(0.3)
            
            # STEP 4: Line Item Extraction
            progress_bar.progress(90, text="Step 4/4: Extracting line items...")
            status_area.info("""
            📋 **Line Item Extraction**
            - Parsing tabular data
            - Finding: Description, Quantity, Unit Price, Amount
            - Building structured rows...
            """)
            time.sleep(0.4)
            
            line_items = processor.extract_line_items(sample_invoice)
            
            progress_bar.progress(100, text="✅ Document Processed!")
            status_area.success("🎉 **Extraction complete!**")
            time.sleep(0.3)
            progress_bar.empty()
            status_area.empty()
            
            # Show results
            st.success("### ✅ Extraction Results")
            
            col1, col2 = st.columns(2)
            with col1:
                st.subheader("📋 Document Info")
                st.json({
                    "type": doc_type,
                    "invoice_number": key_values.get("invoice_number"),
                    "date": key_values.get("date"),
                    "payment_terms": key_values.get("payment_terms")
                })
                
                st.subheader("💰 Financial Data")
                st.json({
                    "subtotal": key_values.get("subtotal"),
                    "tax": key_values.get("tax"),
                    "total": key_values.get("total")
                })
            
            with col2:
                st.subheader("📦 Line Items")
                if line_items:
                    st.dataframe(pd.DataFrame(line_items), use_container_width=True)
                else:
                    st.info("No line items detected")
                
                st.subheader("🏷️ Entities Found")
                if entities:
                    entity_data = [{"text": e.text, "type": e.label} for e in entities[:10]]
                    st.dataframe(pd.DataFrame(entity_data), use_container_width=True)
                else:
                    st.info("Install spaCy model for entity extraction: python -m spacy download en_core_web_sm")
            
        except Exception as e:
            progress_bar.empty()
            status_area.error(f"❌ Error: {e}")
            st.exception(e)
    else:
        st.info("👆 Edit the text above and click to extract structured data from the document")


def render_graph_demo(event_log):
    """Render process graph demo with step-by-step progress."""
    st.header("🕸️ Process Graph Analysis")
    st.caption("Analyze process flows using NetworkX graph algorithms")
    
    st.markdown("---")
    
    if st.button("▶️ Build Process Graph", type="primary", use_container_width=True):
        import time
        
        progress_bar = st.progress(0, text="Initializing graph builder...")
        status_area = st.empty()
        
        try:
            from demos.graph import ProcessGraph, build_graph_from_dataframe
            
            # STEP 1: Build DFG
            progress_bar.progress(20, text="Step 1/4: Building Directly-Follows Graph...")
            status_area.info(f"""
            🔗 **Building Directly-Follows Graph (DFG)**
            - Analyzing {len(event_log):,} events
            - Extracting activity sequences per case
            - Creating nodes for each activity
            - Adding edges for transitions...
            """)
            time.sleep(0.5)
            
            graph = build_graph_from_dataframe(event_log)
            status_area.success(f"✅ Graph built: {graph.graph.number_of_nodes()} nodes, {graph.graph.number_of_edges()} edges")
            time.sleep(0.3)
            
            # STEP 2: Calculate metrics
            progress_bar.progress(50, text="Step 2/4: Calculating graph metrics...")
            status_area.info("""
            📏 **Calculating Metrics**
            - Finding start/end activities
            - Computing average path length
            - Counting process variants
            - Detecting loops...
            """)
            time.sleep(0.5)
            
            metrics = graph.calculate_metrics()
            status_area.success(f"✅ Found {metrics.variants_count} unique process variants")
            time.sleep(0.3)
            
            # STEP 3: Detect bottleneck
            progress_bar.progress(75, text="Step 3/4: Detecting bottleneck...")
            status_area.info("""
            🔍 **Bottleneck Detection**
            - Computing average duration per activity
            - Finding activity with highest wait time
            - Analyzing in-degree/out-degree...
            """)
            time.sleep(0.5)
            
            bottleneck = graph.detect_bottleneck()
            status_area.success(f"✅ Bottleneck: {bottleneck}")
            time.sleep(0.3)
            
            # STEP 4: Analyze variants
            progress_bar.progress(100, text="✅ Analysis Complete!")
            status_area.success("🎉 **Graph analysis complete!**")
            time.sleep(0.3)
            progress_bar.empty()
            status_area.empty()
            
            # Show results
            st.success("### ✅ Graph Analysis Results")
            
            col1, col2, col3, col4 = st.columns(4)
            with col1:
                st.metric("Activities", metrics.num_activities)
            with col2:
                st.metric("Transitions", metrics.num_transitions)
            with col3:
                st.metric("Variants", metrics.variants_count)
            with col4:
                st.metric("Avg Path Length", f"{metrics.avg_path_length:.1f}")
            
            st.warning(f"🚨 **Bottleneck Activity:** {bottleneck}")
            
            st.markdown("---")
            
            # Activity stats
            st.subheader("📊 Activity Statistics")
            activity_stats = []
            for node in graph.graph.nodes():
                node_data = graph.graph.nodes[node]
                activity_stats.append({
                    'activity': node,
                    'frequency': node_data.get('count', 0),
                    'avg_duration_hours': round(node_data.get('avg_duration', 0), 2)
                })
            activity_stats.sort(key=lambda x: x['frequency'], reverse=True)
            
            fig = px.bar(pd.DataFrame(activity_stats[:10]), x='activity', y='frequency',
                        color='avg_duration_hours', title="Top Activities by Frequency")
            st.plotly_chart(fig, use_container_width=True)
            
            # Top variants
            st.subheader("🔀 Top Process Variants")
            variants = []
            for path, count in sorted(graph.variants.items(), key=lambda x: -x[1])[:5]:
                variants.append({'path': ' → '.join(path), 'frequency': count, 'steps': len(path)})
            st.dataframe(pd.DataFrame(variants), use_container_width=True)
            
            # Animated DFG Discovery
            st.markdown("---")
            st.subheader("🎥 Algorithm Visualization")
            st.caption("Watch how the Directly-Follows Graph is discovered by analyzing event sequences")
            
            try:
                from demos.animations import create_animated_dfg
                anim_fig = create_animated_dfg(event_log, duration_ms=150)
                st.plotly_chart(anim_fig, use_container_width=True)
            except Exception as anim_err:
                st.warning(f"Animation not available: {anim_err}")
            
        except Exception as e:
            progress_bar.empty()
            status_area.error(f"❌ Error: {e}")
            st.exception(e)
    else:
        st.info("👆 Click to analyze the process flow, discover variants, and identify bottlenecks")


def main():
    """Main application."""
    
    # Sidebar
    st.sidebar.image("https://img.icons8.com/fluency/96/process.png", width=80)
    st.sidebar.title("Process Mining Demo")
    st.sidebar.markdown("---")
    
    # Dataset selector
    try:
        selected_dataset, n_cases = render_dataset_selector()
        event_log = load_dataset(selected_dataset, n_cases)
    except Exception:
        # Fallback to generators if datasets module has issues
        from utils.generators import generate_event_log
        event_log = generate_event_log(n_cases=300)
        selected_dataset = "order_to_cash"
    
    st.sidebar.markdown("---")
    
    demo_options = {
        "🏠 Overview": "overview",
        "🔮 Predictive Analytics": "predictive",
        "✅ Conformance Checking": "conformance",
        "🎮 Process Simulation": "simulation",
        "📊 Optimization": "optimization",
        "📄 Document Processing": "document",
        "🕸️ Process Graph": "graph"
    }
    
    selected = st.sidebar.radio("Select Demo", list(demo_options.keys()))
    demo = demo_options[selected]
    
    st.sidebar.markdown("---")
    st.sidebar.markdown("""
    ### 🛠️ Technologies
    - **scikit-learn** - ML
    - **SimPy** - Simulation
    - **PuLP** - Optimization
    - **spaCy** - NLP
    - **NetworkX** - Graphs
    """)
    
    # Main content
    if demo == "overview":
        st.markdown('<p class="main-header">Process Mining Platform</p>', unsafe_allow_html=True)
        st.markdown('<p class="sub-header">Technology Demonstration</p>', unsafe_allow_html=True)
        
        # Dataset info
        stats = get_dataset_stats(event_log)
        
        st.subheader(f"📊 Current Dataset: {selected_dataset.replace('_', ' ').title()}")
        col1, col2, col3, col4 = st.columns(4)
        with col1:
            st.metric("Cases", stats['total_cases'])
        with col2:
            st.metric("Events", stats['total_events'])
        with col3:
            st.metric("Activities", stats['total_activities'])
        with col4:
            st.metric("Avg Duration", f"{stats['avg_duration_hours']:.1f}h")
        
        st.markdown("### 🎯 Available Demos")
        
        col1, col2 = st.columns(2)
        with col1:
            st.markdown("""
            - **Predictive Analytics** - ML prediction
            - **Conformance Checking** - Rule validation
            - **Process Simulation** - Digital twin
            """)
        with col2:
            st.markdown("""
            - **Optimization** - Resource planning
            - **Document Processing** - IDP/NER
            - **Process Graph** - Flow analysis
            """)
        
        st.info("👈 Select a demo from the sidebar!")
    
    elif demo == "predictive":
        render_predictive_demo(event_log)
    elif demo == "conformance":
        render_conformance_demo(event_log)
    elif demo == "simulation":
        render_simulation_demo()
    elif demo == "optimization":
        render_optimization_demo()
    elif demo == "document":
        render_document_demo()
    elif demo == "graph":
        render_graph_demo(event_log)


if __name__ == "__main__":
    main()
