import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go

# 设置页面标题和布局
st.set_page_config(
    page_title="上市公司数字化转型指数查询系统",
    page_icon="📊",
    layout="wide"
)

# 读取数据
@st.cache_data

def load_data():
    df = pd.read_excel('合并后的数据.xlsx')
    # 处理行业代码列名的空格
    df.rename(columns={' 行业代码': '行业代码'}, inplace=True)
    
    # 填充缺失的行业信息
    df['行业代码'] = df['行业代码'].fillna('未知')
    df['行业名称'] = df['行业名称'].fillna('未知')
    
    # 将股票代码补全到6位数
    df['股票代码'] = df['股票代码'].astype(str).str.zfill(6)
    
    return df

df = load_data()

# 页面标题
st.title("📊 上市公司数字化转型指数查询系统")
st.markdown("### 查询1999-2023年上市公司的数字化转型指数数据")

# 统计信息卡片
col1, col2, col3 = st.columns(3)
with col1:
    st.metric("📈 数据总量", f"{len(df):,}")
with col2:
    st.metric("🏢 企业数量", f"{df['企业名称'].nunique():,}")
with col3:
    st.metric("📅 年份跨度", f"{df['年份'].min()}-{df['年份'].max()}")

# 查询条件
st.sidebar.header("查询条件")

# 查询方式选择
query_method = st.sidebar.radio(
    "搜索方式",
    ("股票代码", "企业名称")
)

# 企业选择
if query_method == "股票代码":
    stock_codes = df['股票代码'].unique().tolist()
    selected_stock = st.sidebar.selectbox(
        "选择股票代码:",
        stock_codes
    )
    # 根据选择的股票代码获取企业名称
    selected_company = df[df['股票代码'] == selected_stock]['企业名称'].iloc[0]
else:
    companies = df['企业名称'].unique().tolist()
    selected_company = st.sidebar.selectbox(
        "选择企业名称:",
        companies
    )
    # 根据选择的企业名称获取股票代码
    selected_stock = df[df['企业名称'] == selected_company]['股票代码'].iloc[0]

# 年份选择
selected_year = st.sidebar.selectbox(
    "选择年份:",
    sorted(df['年份'].unique().tolist())
)

# 执行查询按钮
if st.sidebar.button("🔍 执行查询"):
    # 显示企业基本信息
    st.subheader(f"🏢 {selected_company} (股票代码: {selected_stock})")
    
    # 筛选该企业的数据
    company_data = df[df['股票代码'] == selected_stock]
    
    # 绘制趋势图
    st.markdown(f"### {selected_company}历年数字化转型指数趋势({df['年份'].min()}-{df['年份'].max()})")
    
    fig = go.Figure()
    
    # 绘制趋势线
    fig.add_trace(go.Scatter(
        x=company_data['年份'],
        y=company_data['数字化转型指数'],
        mode='lines+markers',
        name='数字化转型指数',
        line=dict(color='blue', width=2),
        marker=dict(size=8)
    ))
    
    # 标记选中年份的数据点
    selected_year_data = company_data[company_data['年份'] == selected_year]
    if not selected_year_data.empty:
        fig.add_trace(go.Scatter(
            x=[selected_year],
            y=[selected_year_data['数字化转型指数'].iloc[0]],
            mode='markers',
            name=f'{selected_year}年',
            marker=dict(size=12, color='orange', symbol='star')
        ))
    
    # 设置图表布局
    fig.update_layout(
        xaxis_title='年份',
        yaxis_title='数字化转型指数',
        hovermode='x unified',
        legend=dict(x=0.02, y=0.98),
        height=500,
        # 设置x轴显示完整的年份范围
        xaxis=dict(
            range=[1999, 2023],
            tickmode='linear',
            dtick=1
        )
    )
    
    st.plotly_chart(fig, use_container_width=True)
    
    # 显示选中年份的详细数据
    if not selected_year_data.empty:
        st.markdown(f"#### {selected_year}年详细数据")
        detail_data = selected_year_data[['企业名称', '股票代码', '年份', '数字化转型指数', '行业代码', '行业名称']].iloc[0]
        st.write(f"- **企业名称**: {detail_data['企业名称']}")
        st.write(f"- **股票代码**: {detail_data['股票代码']}")
        st.write(f"- **年份**: {detail_data['年份']}")
        st.write(f"- **数字化转型指数**: {detail_data['数字化转型指数']}")
        st.write(f"- **行业代码**: {detail_data['行业代码']}")
        st.write(f"- **行业名称**: {detail_data['行业名称']}")
    
    # 显示企业统计信息
    st.markdown("#### 企业统计信息")
    col1, col2, col3 = st.columns(3)
    with col1:
        st.metric("📊 平均指数", round(company_data['数字化转型指数'].mean(), 2))
    with col2:
        st.metric("📈 最高指数", round(company_data['数字化转型指数'].max(), 2))
    with col3:
        st.metric("📉 最低指数", round(company_data['数字化转型指数'].min(), 2))

# 数据概览
with st.expander("📋 数据概览"):
    st.dataframe(df.sample(10))

# 行业分布
with st.expander("🏭 行业分布"):
    industry_dist = df['行业名称'].value_counts().head(20)
    fig_industry = px.bar(
        x=industry_dist.values,
        y=industry_dist.index,
        orientation='h',
        title='企业数量最多的20个行业'
    )
    fig_industry.update_layout(xaxis_title='企业数量', yaxis_title='行业名称')
    st.plotly_chart(fig_industry, use_container_width=True)

# 页脚信息
st.markdown("---")
st.markdown("© 2025 上市公司数字化转型指数查询系统 | 数据范围: 1999-2023年")