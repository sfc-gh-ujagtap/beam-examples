"""
Deploy Streamlit TPC-H Dashboard to Beam.cloud
==============================================

Prerequisites:
1. Create Beam secrets for Snowflake credentials:
   beam secret create SNOWFLAKE_ACCOUNT "your-account"
   beam secret create SNOWFLAKE_USER "your-user"
   beam secret create SNOWFLAKE_PAT "your-pat-token"
   beam secret create SNOWFLAKE_WAREHOUSE "COMPUTE_WH"

2. Run this script:
   python deploy_streamlit.py
"""

from beam import Pod, Image


def deploy():
    print("🚀 Deploying Streamlit TPC-H Dashboard to Beam.cloud...")
    
    pod = Pod(
        name="tpch-dashboard",
        image=Image(python_version="python3.11").add_python_packages([
            "streamlit",
            "pandas",
            "plotly",
            "snowflake-connector-python",
        ]),
        cpu=2,
        memory=2048,
        ports=[8501],
        entrypoint=[
            "streamlit", "run", "streamlit_app.py",
            "--server.port=8501",
            "--server.address=0.0.0.0",
            "--server.headless=true",
        ],
        secrets=[
            "SNOWFLAKE_ACCOUNT",
            "SNOWFLAKE_USER", 
            "SNOWFLAKE_PAT",
            "SNOWFLAKE_WAREHOUSE",
        ],
    )
    
    result = pod.create()
    print(f"✅ Streamlit app deployed!")
    print(f"🌐 URL: {result.url}")
    return result


if __name__ == "__main__":
    deploy()
