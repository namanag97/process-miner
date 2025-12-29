PM4Py Complete Reference Guide
A condensed, developer-focused reference for the pm4py process mining library.

Quick Start
import pm4py
import pandas as pd

# Read event log

log = pm4py.read_xes("log.xes")

# or from CSV

df = pd.read_csv("log.csv")
df = pm4py.format_dataframe(df, case_id="case_id", activity_key="activity", timestamp_key="timestamp")

# Discover process model

net, im, fm = pm4py.discover_petri_net_inductive(log)

# Visualize

pm4py.view_petri_net(net, im, fm)

# Check conformance

fitness = pm4py.fitness_alignments(log, net, im, fm)
📥 Input/Output (pm4py.read / pm4py.write)
Traditional Event Logs
Format Read Write
XES read_xes(file_path) write_xes(log, file_path)
BPMN read_bpmn(file_path) write_bpmn(model, file_path)
DFG read_dfg(file_path) write_dfg(dfg, start, end, file_path)
Petri Net read_pnml(file_path) write_pnml(net, im, fm, file_path)
Process Tree read_ptml(file_path) write_ptml(tree, file_path)
Object-Centric Event Logs (OCEL 1.0)
Format Read Write
CSV read_ocel_csv(file_path) write_ocel_csv(ocel, file_path, objects_path)
SQLite read_ocel_sqlite(file_path) write_ocel_sqlite(ocel, file_path)
Object-Centric Event Logs (OCEL 2.0)
Format Read Write
XML read_ocel2_xml(file_path) write_ocel2_xml(ocel, file_path)
SQLite read_ocel2_sqlite(file_path) write_ocel2_sqlite(ocel, file_path)
JSON read_ocel2_json(file_path) write_ocel2_json(ocel, file_path)
🔄 Conversion (pm4py.convert)

# Log conversions

event_log = pm4py.convert_to_event_log(df)
event_stream = pm4py.convert_to_event_stream(log)
dataframe = pm4py.convert_to_dataframe(log)

# Model conversions

bpmn = pm4py.convert_to_bpmn(net, im, fm)
net, im, fm = pm4py.convert_to_petri_net(tree)
tree = pm4py.convert_to_process_tree(net, im, fm)
powl = pm4py.convert_to_powl(tree)
rg = pm4py.convert_to_reachability_graph(net, im, fm)

# Special conversions

ocel = pm4py.convert_log_to_ocel(log, object_types=["order", "item"])
nx_graph = pm4py.convert_log_to_networkx(log)
nx_graph = pm4py.convert_ocel_to_networkx(ocel)
nx_graph = pm4py.convert_petri_net_to_networkx(net, im, fm)
net = pm4py.convert_petri_net_type(net, im, fm) # Change internal type
🔍 Process Discovery (pm4py.discovery)
Directly-Follows Graphs (DFG)
dfg, start, end = pm4py.discover_dfg(log) # Frequency-annotated
dfg, start, end = pm4py.discover_performance_dfg(log) # Performance-annotated
efg = pm4py.discover_eventually_follows_graph(log) # Eventually-follows
Procedural Models
Algorithm Output Function
Alpha Miner Petri Net discover_petri_net_alpha(log)
Inductive Miner Petri Net discover_petri_net_inductive(log, noise_threshold=0.0)
Heuristics Miner Petri Net discover_petri_net_heuristics(log)
ILP Miner Petri Net discover_petri_net_ilp(log)
Inductive Miner Process Tree discover_process_tree_inductive(log)
Inductive Miner BPMN discover_bpmn_inductive(log)
Heuristics Miner Heuristics Net discover_heuristics_net(log)
POWL POWL Model discover_powl(log)
Declarative Models
declare_model = pm4py.discover_declare(log)
log_skeleton = pm4py.discover_log_skeleton(log)
temporal_profile = pm4py.discover_temporal_profile(log)
Other Discovery
footprints = pm4py.discover_footprints(log) # or from model
ts = pm4py.discover_transition_system(log)
prefix_tree = pm4py.discover_prefix_tree(log)
batches = pm4py.discover_batches(log)
msd = pm4py.derive_minimum_self_distance(log)
✅ Conformance Checking (pm4py.conformance)
Token-Based Replay

# Diagnostics (detailed per-trace)

replayed = pm4py.conformance_diagnostics_token_based_replay(log, net, im, fm)

# Fitness (aggregate score)

fitness = pm4py.fitness_token_based_replay(log, net, im, fm)

# Returns: {"average_trace_fitness": 0.95, "log_fitness": 0.92, ...}

# Precision

precision = pm4py.precision_token_based_replay(log, net, im, fm)

# Prefix replay

result = pm4py.replay_prefix_tbr(["A", "B", "C"], net, im, fm)
Alignments (Optimal)

# Diagnostics (detailed per-trace)

aligned = pm4py.conformance_diagnostics_alignments(log, net, im, fm)

# Fitness

fitness = pm4py.fitness_alignments(log, net, im, fm)

# Precision

precision = pm4py.precision_alignments(log, net, im, fm)
Footprints-Based
diagnostics = pm4py.conformance_diagnostics_footprints(log, net, im, fm)
fitness = pm4py.fitness_footprints(log, net, im, fm)
precision = pm4py.precision_footprints(log, net, im, fm)
Declarative Conformance

# Temporal profile deviations

deviations = pm4py.conformance_temporal_profile(log, temporal_profile, zeta=2.0)

# DECLARE conformance

conformance = pm4py.conformance_declare(log, declare_model)

# Log skeleton conformance

conformance = pm4py.conformance_log_skeleton(log, log_skeleton)
📊 Visualization (pm4py.vis)
View (On-Screen) vs Save (To File)
Model Type View Save
Petri Net view_petri_net(net, im, fm) save_vis_petri_net(net, im, fm, path)
DFG view_dfg(dfg, start, end) save_vis_dfg(dfg, start, end, path)
Performance DFG view_performance_dfg(dfg, start, end) save_vis_performance_dfg(dfg, start, end, path)
Process Tree view_process_tree(tree) save_vis_process_tree(tree, path)
BPMN view_bpmn(bpmn) save_vis_bpmn(bpmn, path)
Heuristics Net view_heuristics_net(hnet) save_vis_heuristics_net(hnet, path)
POWL view_powl(powl) save_vis_powl(powl, path)
Transition System view_transition_system(ts) save_vis_transition_system(ts, path)
Prefix Tree view_prefix_tree(trie) save_vis_prefix_tree(trie, path)
Footprints view_footprints(fp) save_vis_footprints(fp, path)
Alignments view_alignments(log, aligned) save_vis_alignments(log, aligned, path)
Charts & Analytics
Chart View Save
Dotted Chart view_dotted_chart(log) save_vis_dotted_chart(log, path)
SNA Network view_sna(sna_metric) save_vis_sna(sna_metric, path)
Case Duration view_case_duration_graph(log) save_vis_case_duration_graph(log, path)
Events/Time view_events_per_time_graph(log) save_vis_events_per_time_graph(log, path)
Performance Spectrum view_performance_spectrum(log, acts) save_vis_performance_spectrum(log, acts, path)
Events Distribution view_events_distribution_graph(log) save_vis_events_distribution_graph(log, path)
Network Analysis view_network_analysis(na) save_vis_network_analysis(na, path)
Object-Centric Visualization
Type View Save
OC-DFG view_ocdfg(ocdfg) save_vis_ocdfg(ocdfg, path)
OC Petri Net view_ocpn(ocpn) save_vis_ocpn(ocpn, path)
Object Graph view_object_graph(ocel, graph) save_vis_object_graph(ocel, graph, path)
📈 Statistics (pm4py.stats)
Activity & Attribute Statistics
start_acts = pm4py.get_start_activities(log) # {"A": 100, "B": 50}
end_acts = pm4py.get_end_activities(log) # {"Z": 120, "Y": 30}
event_attrs = pm4py.get_event_attributes(log) # ["concept:name", "time:timestamp", ...]
trace_attrs = pm4py.get_trace_attributes(log) # ["case:concept:name", ...]
event_vals = pm4py.get_event_attribute_values(log, "resource") # {"John": 50, ...}
trace_vals = pm4py.get_trace_attribute_values(log, "customer") # {"VIP": 20, ...}
Variants
variants = pm4py.get_variants(log) # {"A,B,C": [trace1, trace2], ...}
variants_tuples = pm4py.get_variants_as_tuples(log) # {("A","B","C"): [...], ...}
sub_logs = pm4py.split_by_process_variant(log) # Split log by variant
paths_duration = pm4py.get_variants_paths_duration(log) # Variant positions with durations
Performance Metrics
case_durations = pm4py.get_all_case_durations(log) # [1000.0, 2000.0, ...]
case_duration = pm4py.get_case_duration(log, "case1") # Single case duration
arrival_avg = pm4py.get_case_arrival_average(log) # Average inter-arrival time
cycle_time = pm4py.get_cycle_time(log) # Process cycle time
service_time = pm4py.get_service_time(log) # {"A": 10.5, "B": 20.3, ...}
Other Statistics
msd = pm4py.get_minimum_self_distances(log)
msd_witnesses = pm4py.get_minimum_self_distance_witnesses(log)
rework = pm4py.get_rework_cases_per_activity(log) # {"A": ["case1", "case2"], ...}
segments = pm4py.get_frequent_trace_segments(log, k=5)
positions = pm4py.get_activity_position_summary(log, "A")
stochastic_lang = pm4py.get_stochastic_language(log) # or from model
🔧 Filtering (pm4py.filtering)
Activity Filtering
filtered = pm4py.filter_start_activities(log, ["A", "B"])
filtered = pm4py.filter_end_activities(log, ["X", "Y"])
filtered = pm4py.filter_event_attribute_values(log, "concept:name", ["A", "B", "C"])
filtered = pm4py.filter_trace_attribute_values(log, "customer", ["VIP"])
Variant Filtering
filtered = pm4py.filter_variants(log, [("A", "B", "C"), ("A", "C", "B")])
filtered = pm4py.filter_variants_top_k(log, k=10)
filtered = pm4py.filter_variants_by_coverage_percentage(log, percentage=0.8)
Relation Filtering
filtered = pm4py.filter_directly_follows_relation(log, [("A", "B"), ("B", "C")])
filtered = pm4py.filter_eventually_follows_relation(log, [("A", "Z")])
filtered = pm4py.filter_between(log, "A", "Z") # Sub-cases between activities
Time & Performance Filtering
from datetime import datetime
filtered = pm4py.filter_time_range(log, datetime(2023,1,1), datetime(2023,12,31))
filtered = pm4py.filter_case_performance(log, min_performance=0, max_performance=86400)
filtered = pm4py.filter_paths_performance(log, [("A","B")], min_perf=0, max_perf=3600)
Case Filtering
filtered = pm4py.filter_case_size(log, min_size=3, max_size=20)
filtered = pm4py.filter_activities_rework(log, "A", min_occurrences=2)
filtered = pm4py.filter_prefixes(log, "A") # Prefixes up to activity A
filtered = pm4py.filter_suffixes(log, "A") # Suffixes starting from A
filtered = pm4py.filter_trace_segments(log, [["A", "B"], ["B", "C"]])
filtered = pm4py.filter_log_relative_occurrence_event_attribute(log, "resource", 0.1)
Resource Filtering (LTL)
filtered = pm4py.filter_four_eyes_principle(log, "A", "B")
filtered = pm4py.filter_activity_done_different_resources(log, "A")
OCEL Filtering

# Event/Object attribute filtering

filtered = pm4py.filter_ocel_event_attribute(ocel, "activity", ["A", "B"])
filtered = pm4py.filter_ocel_object_attribute(ocel, "color", ["red", "blue"])

# Object type filtering

filtered = pm4py.filter_ocel_object_types(ocel, ["order", "item"])
filtered = pm4py.filter_ocel_object_types_allowed_activities(ocel, {"order": ["Create", "Ship"]})
filtered = pm4py.filter_ocel_object_per_type_count(ocel, {"order": 1, "item": 2})

# Lifecycle filtering

filtered = pm4py.filter_ocel_start_events_per_object_type(ocel, "order")
filtered = pm4py.filter_ocel_end_events_per_object_type(ocel, "order")
filtered = pm4py.filter_ocel_events_timestamp(ocel, start_ts, end_ts)

# ID-based filtering

filtered = pm4py.filter_ocel_events(ocel, ["e1", "e2", "e3"])
filtered = pm4py.filter_ocel_objects(ocel, ["o1", "o2"])

# Connected component filtering

filtered = pm4py.filter_ocel_cc_object(ocel, "order_123")
filtered = pm4py.filter_ocel_cc_length(ocel, min_length=5, max_length=50)
filtered = pm4py.filter_ocel_cc_otype(ocel, "order")
filtered = pm4py.filter_ocel_cc_activity(ocel, "Create Order")
🤖 Machine Learning (pm4py.ml)

# Train/test split

train_log, test_log = pm4py.split_train_test(log, train_percentage=0.8)

# Prefix extraction

prefixes = pm4py.get_prefixes_from_log(log, length=5)

# Feature extraction

features_df = pm4py.extract_features_dataframe(log)
temporal_df = pm4py.extract_temporal_features_dataframe(log)

# Target extraction

targets = pm4py.extract_target_vector(log, variant="next_activity")

# Variants: "next_activity", "remaining_time", "case_outcome"

# Outcome enrichment

enriched_df = pm4py.extract_outcome_enriched_dataframe(log)

# OCEL features

ocel_features = pm4py.extract_ocel_features(ocel, "order")
🎮 Simulation (pm4py.sim)

# Play out from model

simulated_log = pm4py.play_out(net, im, fm)

# or from process tree

simulated_log = pm4py.play_out(tree)

# Generate random process tree

random_tree = pm4py.generate_process_tree(
min_leaves=5,
max_leaves=15,
operators=["->", "X", "+", "*"] # sequence, xor, parallel, loop
)
🎯 Object-Centric Process Mining (pm4py.ocel)
Basic Operations
object_types = pm4py.ocel_get_object_types(ocel) # ["order", "item", ...]
attr_names = pm4py.ocel_get_attribute_names(ocel) # ["cost", "quantity", ...]

# Flatten to traditional log

flat_log = pm4py.ocel_flattening(ocel, "order")

# Activity-object type mapping

activities = pm4py.ocel_object_type_activities(ocel) # {"order": ["Create", ...]}
ot_counts = pm4py.ocel_objects_ot_count(ocel) # Per-event object counts
Discovery
ocdfg = pm4py.discover_ocdfg(ocel)
ocpn = pm4py.discover_oc_petri_net(ocel)
Summaries
temporal = pm4py.ocel_temporal_summary(ocel)
objects = pm4py.ocel_objects_summary(ocel)
interactions = pm4py.ocel_objects_interactions_summary(ocel)
Sampling & Transformation
sampled = pm4py.sample_ocel_objects(ocel, num_objects=100)
sampled = pm4py.sample_ocel_connected_components(ocel, num_cc=50)
cleaned = pm4py.ocel_drop_duplicates(ocel)
merged = pm4py.ocel_merge_duplicates(ocel)
Enrichment
enriched = pm4py.ocel_o2o_enrichment(ocel) # Object-to-object relations
enriched = pm4py.ocel_e2o_lifecycle_enrichment(ocel) # Lifecycle info
clustered = pm4py.cluster_equivalent_ocel(ocel, "order")
🧠 LLM Integration (pm4py.llm)
Abstractions for LLM Prompts

# Log abstractions

dfg_text = pm4py.abstract_dfg(log)
variants_text = pm4py.abstract_variants(log)
attrs_text = pm4py.abstract_log_attributes(log)
features_text = pm4py.abstract_log_features(log)
stream_text = pm4py.abstract_event_stream(log)
case_text = pm4py.abstract_case(case)

# Model abstractions

petri_text = pm4py.abstract_petri_net(net, im, fm)
declare_text = pm4py.abstract_declare(declare_model)
skeleton_text = pm4py.abstract_log_skeleton(log_skeleton)
temporal_text = pm4py.abstract_temporal_profile(temporal_profile)

# OCEL abstractions

ocel_text = pm4py.abstract_ocel(ocel)
ocdfg_text = pm4py.abstract_ocel_ocdfg(ocel)
ocel_features_text = pm4py.abstract_ocel_features(ocel, "order")
LLM Queries

# OpenAI integration

response = pm4py.openai_query(prompt, api_key="sk-...")

# Explain visualizations

explanation = pm4py.explain*visualization(pm4py.save_vis_petri_net, net, im, fm)
🔌 Connectors (pm4py.connectors)
Traditional Logs
Source Function
Outlook Mails extract_log_outlook_mails()
Outlook Calendar extract_log_outlook_calendar()
Windows Events extract_log_windows_events()
Chrome History extract_log_chrome_history()
Firefox History extract_log_firefox_history()
GitHub Issues extract_log_github(owner, repo, token)
Camunda extract_log_camunda_workflow(connection)
SAP O2C extract_log_sap_o2c(connection)
SAP Accounting extract_log_sap_accounting(connection)
OCEL Variants
All above have extract_ocel*\* equivalents for object-centric logs.

👥 Organizational Mining (pm4py.org)

# Social network analysis

handover = pm4py.discover_handover_of_work_network(log)
working_together = pm4py.discover_working_together_network(log)
subcontracting = pm4py.discover_subcontracting_network(log)
similarity = pm4py.discover_activity_based_resource_similarity(log)

# Role mining

roles = pm4py.discover_organizational_roles(log)

# Network analysis

network = pm4py.discover_network_analysis(log, out_column="source", in_column="target")
🔬 Analysis (pm4py.analysis)
Log Analysis

# Clustering

clustered_logs = pm4py.cluster_log(log, sklearn_clusterer)

# Time enrichment

enriched = pm4py.insert_case_service_waiting_time(log)
enriched = pm4py.insert_case_arrival_finish_rate(log)

# Artificial activities

enriched = pm4py.insert_artificial_start_end(log)
Petri Net Analysis

# Soundness & Workflow checks

is_sound = pm4py.check_soundness(net, im, fm)
is_wf_net = pm4py.check_is_workflow_net(net)

# Marking operations

marking = pm4py.generate_marking(net, {"p1": 1, "p2": 0})
enabled = pm4py.get_enabled_transitions(net, marking)
solution = pm4py.solve_marking_equation(net, im, fm)

# Reduction

reduced = pm4py.reduce_petri_net_invisibles(net)
reduced_net, im, fm = pm4py.reduce_petri_net_implicit_places(net, im, fm)

# Decomposition

components = pm4py.maximal_decomposition(net, im, fm)

# Metrics

simplicity = pm4py.simplicity_petri_net(net, im, fm)
Model Comparison
emd = pm4py.compute_emd(lang1, lang2) # Earth Mover Distance
behavioral = pm4py.behavioral_similarity(model1, model2)
structural = pm4py.structural_similarity(model1, model2)
embeddings = pm4py.embeddings_similarity(model1, model2)
label_sets = pm4py.label_sets_similarity(model1, model2)
Label Operations
labels = pm4py.get_activity_labels(log) # or from model
new_model = pm4py.replace_activity_labels(model, {"old": "new"})
mapped = pm4py.map_labels_from_second_model(model1, model2)
🛠️ Utilities (pm4py.utils)
DataFrame Formatting
df = pm4py.format_dataframe(df,
case_id="case_id",
activity_key="activity",
timestamp_key="timestamp"
)
Parsing

# Parse process tree from string

tree = pm4py.parse_process_tree("->( 'A', X( 'B', 'C' ), 'D' )")

# Parse POWL from string

powl = pm4py.parse_powl_model_string("PO=({'A','B'},{'A'->'B'})")

# Parse log from string

log = pm4py.parse_event_log_string(["A,B,C,D", "A,C,B,D", "A,D"])
Projection & Sampling

# Project on attribute

projected = pm4py.project_on_event_attribute(log) # List of activity sequences

# Sampling

sampled = pm4py.sample_cases(log, num_cases=100)
sampled = pm4py.sample_events(log, num_events=1000)
Serialization
serialized = pm4py.serialize(net, im, fm) # bytes
net, im, fm = pm4py.deserialize(serialized)
Rebasing
rebased = pm4py.rebase(log,
case_id="new_case_id",
activity_key="new_activity",
timestamp_key="new_timestamp"
)
📋 Common Patterns
Full Discovery Pipeline
import pm4py

# 1. Load data

log = pm4py.read_xes("event_log.xes")

# 2. Get statistics

print(f"Start activities: {pm4py.get_start_activities(log)}")
print(f"End activities: {pm4py.get_end_activities(log)}")
print(f"Variants: {len(pm4py.get_variants(log))}")

# 3. Filter if needed

filtered = pm4py.filter_variants_top_k(log, k=20)

# 4. Discover model

net, im, fm = pm4py.discover_petri_net_inductive(filtered, noise_threshold=0.2)

# 5. Evaluate

fitness = pm4py.fitness_alignments(log, net, im, fm)
precision = pm4py.precision_alignments(log, net, im, fm)
print(f"Fitness: {fitness['averageFitness']:.2f}")
print(f"Precision: {precision:.2f}")

# 6. Visualize

pm4py.save_vis_petri_net(net, im, fm, "process_model.png")
OCEL Analysis Pipeline
import pm4py

# 1. Load OCEL

ocel = pm4py.read_ocel2_sqlite("ocel.sqlite")

# 2. Explore

print(f"Object types: {pm4py.ocel_get_object_types(ocel)}")
print(f"Activities per type: {pm4py.ocel_object_type_activities(ocel)}")

# 3. Discover

ocdfg = pm4py.discover_ocdfg(ocel)
ocpn = pm4py.discover_oc_petri_net(ocel)

# 4. Flatten for traditional analysis

flat_log = pm4py.ocel_flattening(ocel, "order")
net, im, fm = pm4py.discover_petri_net_inductive(flat_log)

# 5. Visualize

pm4py.save_vis_ocdfg(ocdfg, "ocdfg.png")
pm4py.save_vis_ocpn(ocpn, "ocpn.png")
ML Feature Extraction
import pm4py
from sklearn.ensemble import RandomForestClassifier

# 1. Load and prepare

log = pm4py.read_xes("log.xes")
train, test = pm4py.split_train_test(log, train_percentage=0.8)

# 2. Extract features

X_train = pm4py.extract_features_dataframe(train)
X_test = pm4py.extract_features_dataframe(test)

# 3. Extract targets (next activity prediction)

y_train = pm4py.extract_target_vector(train, "next_activity")
y_test = pm4py.extract_target_vector(test, "next_activity")

# 4. Train model

clf = RandomForestClassifier()
clf.fit(X_train, y_train)
accuracy = clf.score(X_test, y_test)
🔗 Quick Reference Links
Documentation: https://pm4py.fit.fraunhofer.de/documentation
GitHub: https://github.com/pm4py/pm4py-core
XES Standard: https://xes-standard.org/
OCEL Standard: http://www.ocel-standard.org/
Version: pm4py 2.x
Last Updated: December 2024
