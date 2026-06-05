import streamlit as st

st.set_page_config(
    page_title="Mahindra University | School of Management",
    page_icon="🎓",
    layout="wide"
)

# ---------- HERO SECTION ----------
st.title("🎓 Hello, Mahindra University School of Management!")
st.subheader("Building future-ready leaders for a changing world.")

st.write(
    """
    Welcome to the **School of Management at Mahindra University**, Hyderabad.
    The School of Management focuses on developing students who can understand
    business, technology, analytics, strategy, and leadership in an increasingly
    digital and interdisciplinary world.
    """
)

st.divider()

# ---------- ABOUT SECTION ----------
col1, col2 = st.columns([2, 1])

with col1:
    st.header("About the School")
    st.write(
        """
        The School of Management at Mahindra University offers management education
        designed for the modern economy. The learning experience combines business
        fundamentals with analytical thinking, digital technologies, problem-solving,
        and responsible leadership.
        """
    )

    st.write(
        """
        Students are encouraged to think critically, work collaboratively, and apply
        classroom learning to real-world business and societal challenges.
        """
    )

with col2:
    st.info(
        """
        **Location**  
        Mahindra University  
        Hyderabad, Telangana, India
        """
    )

# ---------- PROGRAMS SECTION ----------
st.header("Programs and Learning Areas")

col1, col2, col3 = st.columns(3)

with col1:
    st.metric("Undergraduate", "BBA / BA")
    st.write("Business, economics, finance, analytics, and digital technology foundations.")

with col2:
    st.metric("Postgraduate", "MBA")
    st.write("Management education for leadership, strategy, innovation, and execution.")

with col3:
    st.metric("Research", "Ph.D.")
    st.write("Research-oriented programs in management and allied disciplines.")

st.divider()

# ---------- FEATURE CARDS ----------
st.header("What Makes the School Future-Ready?")

feature1, feature2, feature3, feature4 = st.columns(4)

with feature1:
    st.success("📊 Analytics")
    st.write("Using data to understand business problems and make better decisions.")

with feature2:
    st.success("💡 Innovation")
    st.write("Encouraging creative thinking, entrepreneurship, and new business models.")

with feature3:
    st.success("🌐 Digital Business")
    st.write("Preparing students for technology-enabled organizations and markets.")

with feature4:
    st.success("🤝 Leadership")
    st.write("Developing ethical, collaborative, and responsible managers.")

# ---------- CALL TO ACTION ----------
st.divider()

st.header("Hello World, Hello Future!")

st.write(
    """
    This simple Streamlit app is a first step toward building interactive digital
    experiences for education, admissions, student engagement, and management learning.
    """
)

if st.button("Explore the School of Management"):
    st.balloons()
    st.success("Welcome to Mahindra University School of Management!")

# ---------- FOOTER ----------
st.divider()
st.caption("Demo Streamlit landing page for Mahindra University School of Management.")