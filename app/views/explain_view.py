"""
EXPLAIN ANALYZE View - Query Performance Analysis
"""
import streamlit as st
from sqlalchemy.engine import Engine
import pandas as pd
import json
from queries.explain_queries import explain_query, get_test_queries, get_index_recommendations


def show_explain_view(engine: Engine):
    """Display EXPLAIN ANALYZE interface for query performance testing"""
    
    st.header("🔍 Query Performance Analysis (EXPLAIN ANALYZE)")
    
    st.markdown("""
    This page helps you analyze query performance using database EXPLAIN plans.
    Use this to:
    - 🎯 Identify slow queries and bottlenecks
    - 📊 See execution plans and cost estimates
    - 🔧 Test the impact of indexes
    - ⚡ Compare optimized vs unoptimized queries
    """)
    
    if engine is None:
        st.error("❌ Database connection not available")
        return
    
    # Create tabs
    tab1, tab2, tab3 = st.tabs(["📈 Test Queries", "🛠️ Custom Query", "💡 Index Recommendations"])
    
    with tab1:
        show_test_queries_tab(engine)
    
    with tab2:
        show_custom_query_tab(engine)
    
    with tab3:
        show_index_recommendations_tab(engine)


def show_test_queries_tab(engine: Engine):
    """Tab for pre-defined test queries"""
    st.subheader("Pre-defined Test Queries")
    st.caption("Select a query to analyze its execution plan")
    
    queries = get_test_queries()
    
    # Query selector
    query_names = list(queries.keys())
    selected_query_name = st.selectbox(
        "Select Query to Analyze",
        query_names,
        help="Choose from common OLAP queries to analyze performance"
    )
    
    selected_query = queries[selected_query_name]
    
    # Display query info
    col1, col2 = st.columns([2, 1])
    
    with col1:
        st.markdown(f"**Description:** {selected_query['description']}")
    
    with col2:
        analyze_mode = st.checkbox(
            "Use ANALYZE (actual execution)",
            value=False,
            help="ANALYZE actually runs the query. Uncheck for EXPLAIN only (plan without execution)"
        )
    
    # Show the query
    with st.expander("📝 View SQL Query", expanded=False):
        st.code(selected_query['query'], language="sql")
        if selected_query['params']:
            st.markdown("**Parameters:**")
            st.json(selected_query['params'])
    
    # Run EXPLAIN button
    if st.button("▶️ Run EXPLAIN ANALYZE", type="primary", use_container_width=True):
        with st.spinner("Analyzing query execution plan..."):
            result, duration = explain_query(
                engine,
                selected_query['query'],
                selected_query['params'],
                use_analyze=analyze_mode
            )
            
            display_explain_results(result, duration, analyze_mode)


def show_custom_query_tab(engine: Engine):
    """Tab for custom query input"""
    st.subheader("Custom Query Analysis")
    st.caption("Enter your own SQL query to analyze")
    
    # Query input
    custom_query = st.text_area(
        "SQL Query",
        height=200,
        placeholder="Enter your SELECT query here...",
        help="Write a SELECT query to analyze. Use :param_name for parameters."
    )
    
    # Parameters input
    st.markdown("**Query Parameters** (optional)")
    params_json = st.text_area(
        "Parameters (JSON format)",
        height=80,
        placeholder='{"param_name": "value", "year": 2024}',
        help="Enter parameters as JSON object"
    )
    
    col1, col2 = st.columns([1, 1])
    with col1:
        analyze_mode = st.checkbox(
            "Use ANALYZE (actual execution)",
            value=False,
            key="custom_analyze",
            help="ANALYZE actually runs the query"
        )
    
    # Run button
    if st.button("▶️ Run Custom EXPLAIN", type="primary", use_container_width=True):
        if not custom_query.strip():
            st.warning("⚠️ Please enter a SQL query")
            return
        
        # Parse parameters
        params = {}
        if params_json.strip():
            try:
                params = json.loads(params_json)
            except json.JSONDecodeError as e:
                st.error(f"❌ Invalid JSON in parameters: {e}")
                return
        
        with st.spinner("Analyzing custom query..."):
            result, duration = explain_query(
                engine,
                custom_query,
                params if params else None,
                use_analyze=analyze_mode
            )
            
            display_explain_results(result, duration, analyze_mode)


def show_index_recommendations_tab(engine: Engine):
    """Tab for index recommendations"""
    st.subheader("Index Recommendations")
    st.caption("Suggested indexes to improve query performance")
    
    st.markdown("""
    ### 📚 Understanding Indexes
    
    **Indexes** are database structures that improve query performance by creating fast lookup paths.
    
    **When to use indexes:**
    - ✅ Columns frequently used in WHERE clauses
    - ✅ Columns used in JOIN conditions (foreign keys)
    - ✅ Columns used in GROUP BY or ORDER BY
    - ✅ Columns with high selectivity (many unique values)
    
    **Trade-offs:**
    - ⚡ **Faster reads** - queries execute faster
    - 🐌 **Slower writes** - inserts/updates take longer
    - 💾 **More storage** - indexes consume disk space
    """)
    
    recommendations = get_index_recommendations()
    
    st.markdown("---")
    st.subheader("Recommended Indexes")
    
    # Group by table
    tables = {}
    for rec in recommendations:
        table = rec['table']
        if table not in tables:
            tables[table] = []
        tables[table].append(rec)
    
    for table, indexes in tables.items():
        with st.expander(f"📊 **{table}** ({len(indexes)} indexes)", expanded=True):
            for idx in indexes:
                col1, col2 = st.columns([3, 1])
                
                with col1:
                    st.markdown(f"**`{idx['index_name']}`** on `{', '.join(idx['columns'])}`")
                    st.caption(f"💡 {idx['reason']}")
                
                with col2:
                    if st.button("📋 Copy SQL", key=f"copy_{idx['index_name']}", use_container_width=True):
                        st.code(idx['sql'], language="sql")
                
                st.code(idx['sql'], language="sql")
                st.markdown("")
    
    st.markdown("---")
    st.info("""
    ### 🚀 Next Steps:
    1. **Analyze queries** using the "Test Queries" tab to see current performance
    2. **Create indexes** by running the SQL commands in your database
    3. **Re-analyze queries** to compare before/after performance
    4. **Monitor** the impact on both read and write operations
    """)
    
    # Add index creation helper
    st.markdown("---")
    st.subheader("Create Indexes")
    
    if st.checkbox("Show all index creation SQL"):
        all_sql = "\n\n".join([rec['sql'] for rec in recommendations])
        st.code(all_sql, language="sql")
        
        st.warning("""
        ⚠️ **Before creating indexes:**
        - Backup your database
        - Test on a development environment first
        - Monitor disk space usage
        - Consider creating indexes during off-peak hours
        - Run `ANALYZE TABLE` after creating indexes
        """)


def display_explain_results(result: dict, duration: float, analyze_mode: bool):
    """Display EXPLAIN results in a formatted way"""
    
    st.markdown("---")
    st.subheader("📊 Execution Plan Results")
    
    # Show execution time
    col1, col2, col3 = st.columns(3)
    with col1:
        st.metric("⏱️ Analysis Time", f"{duration*1000:.2f} ms")
    with col2:
        st.metric("🔍 Mode", "EXPLAIN ANALYZE" if analyze_mode else "EXPLAIN")
    with col3:
        if analyze_mode:
            st.metric("⚡ Status", "Actual Execution")
        else:
            st.metric("📋 Status", "Plan Only")
    
    st.markdown("---")
    
    # Display based on result type
    result_type = result.get('type', 'error')
    output = result.get('output', '')
    
    if result_type == 'error':
        st.error(f"❌ Error: {output}")
        
    elif result_type == 'analyze_text':
        # MySQL EXPLAIN ANALYZE text output
        st.subheader("Execution Plan (MySQL)")
        st.text(output)
        
        # Try to parse key metrics
        st.markdown("---")
        st.subheader("Key Observations")
        parse_mysql_explain_text(output)
        
    elif result_type == 'json':
        # JSON format (MySQL or PostgreSQL)
        st.subheader("Execution Plan (JSON)")
        
        with st.expander("📄 View Raw JSON", expanded=False):
            st.json(output)
        
        # Parse and display key information
        st.markdown("---")
        st.subheader("Key Observations")
        parse_json_explain(output)
        
    elif result_type == 'dataframe':
        # SQLite QUERY PLAN
        st.subheader("Execution Plan (SQLite)")
        st.dataframe(output, use_container_width=True)
        
        st.markdown("---")
        st.subheader("Key Observations")
        parse_sqlite_explain(output)


def parse_mysql_explain_text(text: str):
    """Parse MySQL EXPLAIN ANALYZE text output and highlight key points"""
    
    observations = []
    
    if "full scan" in text.lower() or "table scan" in text.lower():
        observations.append("⚠️ **Full table scan detected** - Consider adding an index")
    
    if "using temporary" in text.lower():
        observations.append("⚠️ **Using temporary table** - May indicate need for index on GROUP BY columns")
    
    if "using filesort" in text.lower():
        observations.append("⚠️ **Using filesort** - Consider adding index on ORDER BY columns")
    
    if "using index" in text.lower():
        observations.append("✅ **Using index** - Query is using an index efficiently")
    
    if "using where" in text.lower():
        observations.append("ℹ️ **Using WHERE clause** - Filter applied after reading rows")
    
    # Try to extract actual time
    import re
    time_match = re.search(r'actual time=([\d.]+)\.\.([\d.]+)', text)
    if time_match:
        start_time = float(time_match.group(1))
        end_time = float(time_match.group(2))
        observations.append(f"⏱️ **Actual execution time:** {start_time:.2f}..{end_time:.2f} ms")
    
    # Extract rows
    rows_match = re.search(r'rows=(\d+)', text)
    if rows_match:
        rows = int(rows_match.group(1))
        observations.append(f"📊 **Rows processed:** {rows:,}")
    
    if observations:
        for obs in observations:
            st.markdown(f"- {obs}")
    else:
        st.info("No specific observations extracted. Review the plan above.")


def parse_json_explain(json_data: dict):
    """Parse JSON EXPLAIN output"""
    
    st.info("💡 Review the JSON output above for detailed execution plan information")
    
    # Try to extract useful information from MySQL JSON format
    if 'query_block' in json_data:
        query_block = json_data['query_block']
        
        if 'cost_info' in query_block:
            cost = query_block['cost_info']
            st.metric("Estimated Query Cost", f"{cost.get('query_cost', 'N/A')}")


def parse_sqlite_explain(df: pd.DataFrame):
    """Parse SQLite EXPLAIN QUERY PLAN output"""
    
    observations = []
    
    # Check for scans in the plan
    for _, row in df.iterrows():
        detail = str(row.get('detail', ''))
        
        if 'SCAN' in detail:
            observations.append(f"⚠️ **Table scan:** {detail}")
        elif 'SEARCH' in detail and 'USING INDEX' in detail:
            observations.append(f"✅ **Using index:** {detail}")
        elif 'SEARCH' in detail:
            observations.append(f"ℹ️ **Search operation:** {detail}")
        elif 'USE TEMP' in detail:
            observations.append(f"⚠️ **Temporary table:** {detail}")
    
    if observations:
        for obs in observations:
            st.markdown(f"- {obs}")
    else:
        st.info("Review the query plan above for details")
