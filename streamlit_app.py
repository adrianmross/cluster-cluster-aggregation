import streamlit as st
from cca import CCA

L = st.sidebar.number_input("Lattice Size", min_value=10, max_value=100, value=50)
N = st.sidebar.number_input("Number of Particles", min_value=100, max_value=1000, value=500)

@st.cache_resource
def init_model(L, N):
    model = CCA(L=L, numberOfParticles=N)
    model.initialize()
    return model

model = init_model(L, N)

st.header("Cluster-Cluster Aggregation Simulation")

# Create a placeholder for the plot
lattice = st.empty()

# Create a placeholder for text output
num_clusters = st.empty()

def plot_lattice():
    image = model.draw()  # Get the numpy image array
    lattice.image(image, use_column_width=True)  # Use the placeholder to update the plot


def doStep():
    if model.numberOfClusters > 1:
        model.step()
        plot_lattice()
    num_clusters.write(f"Number of clusters: {model.numberOfClusters}")  # Update the text using the placeholder
    

if st.sidebar.button("Step"):
    doStep()

if "running" not in st.session_state:
    st.session_state.running = False

start_button = st.sidebar.button("Run")
stop_button = st.sidebar.button("Stop")

if start_button:
    st.session_state.running = True

if stop_button:
    st.session_state.running = False

if st.session_state.running:
    while model.numberOfClusters > 1:
        doStep()
        if not st.session_state.running:
            break
