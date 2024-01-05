import streamlit as st
import plotly.express as px
import pandas as pd
import os
import warnings
warnings.filterwarnings("ignore")


#Some basic page configs
st.set_page_config(page_title="Sales Analysis",page_icon="favicon.png",layout="wide")
st.title(" :chart_with_upwards_trend: Exploratory Data Analysis (EDA) of Sales")
st.markdown("<style>div.block-container{padding-top:2rem;}</style>",unsafe_allow_html=True)
# Downloading sample data
st.subheader(":point_right: Sample data")
csv = pd.read_excel("Superstore.xls").to_csv(index = False).encode('utf-8')
st.download_button('Download Data', data = csv, file_name = "Data.csv",mime = "text/csv")

#file uploading
fl = st.file_uploader(":file_folder: Please upload a file", type=["csv", "txt", "xlsx", "xls"])

#file checking
desired_columns = ['Order Date', 'Segment', 'City','State','Region','Category','Sub-Category','Sales','Profit']
if fl is not None:
    file_name, file_extension = os.path.splitext(fl.name)
    file_extension = file_extension[1:].lower()
    if file_extension == "csv" or file_extension == "txt" :
        df = pd.read_csv(fl)
        if all(column in df.columns for column in desired_columns):
           st.success("All desired columns are present in the uploaded file.")
        else:
            missing_columns = [column for column in desired_columns if column not in df.columns]
            st.error(f"The following columns are missing in the uploaded file: {missing_columns}. Please check the sample data")
            st.stop()
    elif file_extension == "xls" or file_extension == "xlsx":
        df = pd.read_excel(fl)
        if all(column in df.columns for column in desired_columns):
           st.success("All desired columns are present in the uploaded file.")
        else:
            missing_columns = [column for column in desired_columns if column not in df.columns]
            st.error(f"The following columns are missing in the uploaded file: {missing_columns}. Please check the sample data")
            st.stop()
    else:
        st.error("Unsupported file extension. Please upload a file with CSV, TXT, XLSX, or XLS extension.")
        st.stop()
else:
    df = pd.read_excel("Superstore.xls")

try:
    col1, col2 = st.columns((2))
    df["Order Date"] = pd.to_datetime(df["Order Date"])
    
    # getting min and max date
    startDate = pd.to_datetime(df["Order Date"]).min()
    endDate = pd.to_datetime(df["Order Date"]).max()

    
    date1 = pd.to_datetime(st.date_input("Start date", startDate))
    date2 = pd.to_datetime(st.date_input("End date", endDate))

    # Check if the entered dates are within the calculated range
    if startDate <= date1 <= endDate and startDate <= date2 <= endDate:
        df = df[(df["Order Date"] > date1) & (df["Order Date"] < date2)].copy()
    else:
        st.warning(f"Warning: Please adjust your date range. The date range must be between {startDate} and {endDate}, and start date must be less than end date")

    # Sidebar section
    st.sidebar.header("Choose the filter to analyze data:")

    # Region filter
    region = st.sidebar.multiselect("Please pick the region", options=df['Region'].unique())
    if not region:
        df = df.copy()
    else:
        df = df[df['Region'].isin(region)]

    # State filter
    state = st.sidebar.multiselect("Please pick the state", options=df['State'].unique())
    if not state:
        df = df.copy()
    else:
        df = df[df['State'].isin(state)]

    # City filter
    city = st.sidebar.multiselect("Please pick the City", options=df['City'].unique())
    if not city:
        df = df.copy()
    else:
        df = df[df['City'].isin(city)]

    category_df = df.groupby(by=['Category'], as_index=False)["Sales"].sum()

    with col1:
        st.subheader("Sales by category")
        fig = px.bar(category_df, x="Category", y="Sales", text=['${:,.2f}'.format(x) for x in category_df["Sales"]],
                     template="seaborn")
        st.plotly_chart(fig, use_container_width=True, height=200)

    with col2:
        st.subheader("Sales by Region")
        fig = px.pie(df, values="Sales", names="Region", hole=0.5, template="ggplot2")
        fig.update_traces(text=df["Region"], textposition="outside")
        st.plotly_chart(fig, use_container_width=True, height=200)

    # Downloading interface the data based on the defined filters
    col3, col4 = st.columns((2))

    with col3:
        with st.expander("View the category data"):
            st.write(category_df.style.background_gradient(cmap="Blues"))
            csv = category_df.to_csv(index=False).encode("utf-8")
            st.download_button("Download data", data=csv, file_name="Category.csv", mime="text/csv",
                               help="Click the button to download category aggregated data as csv file")

    with col4:
        with st.expander("View the region data"):
            region = df.groupby(by="Region", as_index=False)["Sales"].sum()
            st.write(region.style.background_gradient(cmap="Reds"))
            csv = region.to_csv(index=False).encode("utf-8")
            st.download_button("Download data", data=csv, file_name="Region.csv", mime="text/csv",
                               help="Click the button to download region aggregated data as csv file")

    # Time series analysis of the data
    st.subheader("Time series analysis")
    df["month_year"] = df["Order Date"].dt.to_period("M")
    linechartdf = pd.DataFrame(df.groupby(df["month_year"].dt.strftime("%Y : %b"))["Sales"].sum().reset_index())
    fig2 = px.line(linechartdf, x="month_year", y="Sales", labels={"Sales": "Amount"}, height=500, width=1000,
                   template="plotly_dark")
    st.plotly_chart(fig2, use_container_width=True)

    # Download time series data
    with st.expander("View the time series data: "):
        st.write(linechartdf.T.style.background_gradient(cmap="Greens"))
        csv = linechartdf.to_csv(index=False).encode("utf-8")
        st.download_button("Download data", data=csv, file_name="Timeseries.csv", mime="text/csv",
                           help="Click the button to download time series data as csv file")

    # Treemap visualization of the data based on Region, category and sub-category
    st.subheader("Hierarchical view of Sales via Treemap")
    fig3 = px.treemap(df, path=["Region", "Category", "Sub-Category"], values="Sales", hover_data="Sales",
                      color="Sub-Category")
    fig3.update_layout(width=800, height=650)
    st.plotly_chart(fig3, use_container_width=True)

    # Category and segment visualization data
    chart1, chart2 = st.columns((2))
    with chart1:
        st.subheader("Sales by segment")
        fig = px.pie(df, values="Sales", names="Segment", template="none")
        fig.update_traces(text=df["Segment"], textposition="inside")
        st.plotly_chart(fig, use_container_width=True)

    with chart2:
        st.subheader("Sales by category")
        fig = px.pie(df, values="Sales", names="Category", template="plotly_dark")
        fig.update_traces(text=df["Segment"], textposition="inside")
        st.plotly_chart(fig, use_container_width=True)

    import plotly.figure_factory as ff
    st.subheader(":point_right: Click to see the summary table of sub-categories")
    with st.expander("Summary Table for sub-categories"):
        st.markdown("Heatmap for subcategories")
        df["month"] = df["Order Date"].dt.month_name()
        sub_category_Year = pd.pivot_table(data=df, values="Sales", index=["Sub-Category"], columns="month")
        st.write(sub_category_Year.style.background_gradient(cmap="Blues"))

    # Create a scatter plot
    data1 = px.scatter(df, x="Sales", y="Profit", size="Quantity")
    data1['layout'].update(title="Relationship between Sales and Profits",
                           titlefont=dict(size=20), xaxis=dict(title="Sales", titlefont=dict(size=19)),
                           yaxis=dict(title="Profit", titlefont=dict(size=19)))
    st.plotly_chart(data1, use_container_width=True)

except Exception as e:
    st.error(f"There is an inconsistency in the data you have uploaded. Please match the data you upload to the sample format. Error code is: {e}")


st.markdown("---")
st.markdown("### Data collection:")
st.markdown("<div> The uploaded data is not stored anywhere, and we don't reuse the data you have uploaded. </div>",
                unsafe_allow_html=True)

