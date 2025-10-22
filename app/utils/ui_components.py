"""
UI Components and Helper Functions for Better Styling
"""
import streamlit as st


def show_metric_cards(metrics_data):
    """
    Display metrics in styled cards
    
    Args:
        metrics_data: List of dicts with keys: 'label', 'value', 'icon' (optional)
    """
    cols = st.columns(len(metrics_data))
    
    for col, metric in zip(cols, metrics_data):
        with col:
            icon = metric.get('icon', '📊')
            st.markdown(f"""
            <div style='background: linear-gradient(135deg, #FFFFFF 0%, #F8F9FA 100%);
                        padding: 1.5rem;
                        border-radius: 12px;
                        border: 2px solid #FF6B35;
                        box-shadow: 0 2px 8px rgba(255, 107, 53, 0.1);
                        text-align: center;
                        transition: transform 0.3s ease;'>
                <div style='font-size: 2rem; margin-bottom: 0.5rem;'>{icon}</div>
                <div style='color: #666; font-size: 0.9rem; font-weight: 600; margin-bottom: 0.5rem;'>
                    {metric['label']}
                </div>
                <div style='color: #FF6B35; font-size: 1.8rem; font-weight: bold;'>
                    {metric['value']}
                </div>
            </div>
            """, unsafe_allow_html=True)


def show_performance_badge(duration, label="Query Time"):
    """
    Display a performance badge with color coding
    
    Args:
        duration: Query execution time in seconds
        label: Label for the badge
    """
    if duration < 0.5:
        color = "#28a745"
        perf_text = "Excellent"
    elif duration < 1.0:
        color = "#17a2b8"
        perf_text = "Good"
    elif duration < 2.0:
        color = "#ffc107"
        perf_text = "Fair"
    else:
        color = "#dc3545"
        perf_text = "Slow"
    
    st.markdown(f"""
    <div style='display: inline-flex; align-items: center; background-color: {color}; 
                color: white; padding: 0.4rem 1.2rem; border-radius: 25px; 
                font-size: 0.9rem; margin: 1rem 0; box-shadow: 0 2px 4px rgba(0,0,0,0.2);'>
        <span style='margin-right: 0.5rem;'>⚡</span>
        <span><strong>{label}:</strong> {duration:.4f}s ({perf_text})</span>
    </div>
    """, unsafe_allow_html=True)


def show_section_header(title, icon, description=None, color="#FF6B35"):
    """
    Display a styled section header
    
    Args:
        title: Section title
        icon: Emoji icon
        description: Optional description text
        color: Header color
    """
    desc_html = f"<p style='color: #666; margin-top: 0.5rem;'>{description}</p>" if description else ""
    
    st.markdown(f"""
    <div style='background: linear-gradient(135deg, {color}15 0%, {color}05 100%);
                padding: 1.5rem;
                border-radius: 12px;
                border-left: 4px solid {color};
                margin: 1.5rem 0;'>
        <h3 style='color: {color}; margin: 0;'>{icon} {title}</h3>
        {desc_html}
    </div>
    """, unsafe_allow_html=True)


def show_info_box(content, box_type="info"):
    """
    Display a styled information box
    
    Args:
        content: HTML or text content
        box_type: 'info', 'success', 'warning', 'error'
    """
    colors = {
        'info': {'bg': '#E3F2FD', 'border': '#2196F3', 'icon': 'ℹ️'},
        'success': {'bg': '#E8F5E9', 'border': '#4CAF50', 'icon': '✅'},
        'warning': {'bg': '#FFF3E0', 'border': '#FF9800', 'icon': '⚠️'},
        'error': {'bg': '#FFEBEE', 'border': '#F44336', 'icon': '❌'}
    }
    
    style = colors.get(box_type, colors['info'])
    
    st.markdown(f"""
    <div style='background: {style["bg"]};
                padding: 1rem 1.5rem;
                border-radius: 10px;
                border-left: 4px solid {style["border"]};
                margin: 1rem 0;'>
        <span style='font-size: 1.2rem; margin-right: 0.5rem;'>{style["icon"]}</span>
        {content}
    </div>
    """, unsafe_allow_html=True)


def create_download_button(df, filename, button_text="Download Data"):
    """
    Create a styled download button for dataframes
    
    Args:
        df: DataFrame to download
        filename: Name of the file
        button_text: Button label
    """
    csv = df.to_csv(index=False)
    st.download_button(
        label=f"📥 {button_text}",
        data=csv,
        file_name=filename,
        mime="text/csv",
        help=f"Download {filename} as CSV"
    )


def show_data_summary(df, title="Data Summary"):
    """
    Display a summary of the dataframe
    
    Args:
        df: DataFrame to summarize
        title: Summary title
    """
    st.markdown(f"""
    <div style='background: #F8F9FA; padding: 1rem; border-radius: 10px; margin: 1rem 0;'>
        <h4 style='margin: 0 0 0.5rem 0; color: #333;'>{title}</h4>
        <div style='display: grid; grid-template-columns: repeat(auto-fit, minmax(150px, 1fr)); gap: 1rem;'>
            <div>
                <span style='color: #666; font-size: 0.9rem;'>Rows:</span>
                <strong style='color: #FF6B35; font-size: 1.2rem; display: block;'>{len(df):,}</strong>
            </div>
            <div>
                <span style='color: #666; font-size: 0.9rem;'>Columns:</span>
                <strong style='color: #FF6B35; font-size: 1.2rem; display: block;'>{len(df.columns)}</strong>
            </div>
            <div>
                <span style='color: #666; font-size: 0.9rem;'>Memory:</span>
                <strong style='color: #FF6B35; font-size: 1.2rem; display: block;'>
                    {df.memory_usage(deep=True).sum() / 1024:.1f} KB
                </strong>
            </div>
        </div>
    </div>
    """, unsafe_allow_html=True)
