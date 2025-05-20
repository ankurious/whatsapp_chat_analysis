import streamlit as st
import preprocessor,helper
import matplotlib.pyplot as plt
import seaborn as sns
import plotly.express as px
import pandas as pd
import os
import sys
import subprocess


from helper import most_common_words, daily_timeline
st.set_page_config(layout="wide")
st.sidebar.title("WhatsApp Chat Analyzer")

uploaded_file = st.sidebar.file_uploader("Upload your WhatsApp chat file (.txt)", type=["txt"])

if uploaded_file is not None:
    # Read the uploaded file
    bytes_data = uploaded_file.read()
    data = bytes_data.decode("utf-8")

    # Display raw text (optional)
    #st.subheader("Chat Preview")
    #st.text(data[:1000])  # preview first 1000 characters

    df=preprocessor.preprocess(data)

    #st.dataframe(df)

    #fetch unique users

    user_list=df['user'].unique().tolist()

    user_list.remove('group_notification')
    user_list.sort()
    user_list.insert(0,'Overall')

    #selected user value stored to send in helper.py
    selected_user=st.sidebar.selectbox("Show Analysis wrt", user_list)

    if st.sidebar.button("Analyze"): #if analyze os clicked
        num_messages,words,num_media,num_links=helper.fetch_stats(selected_user,df) #values of fetch_stats of helper.py sent in these two values
        st.title("Top Statistics ")
        col1, col2, col3, col4 = st.columns(4)

        with col1:
            st.header("Total Messages")
            st.title(num_messages)
        with col2:
            st.header("Total Words")
            st.title(words)
        with col3:
            st.header("Media Shared")
            st.title(num_media)
        with col4:
            st.header("Links Shared")
            st.title(num_links)

     #Monthly timeline

        st.title("Monthly Timeline")
        timeline=helper.monthly_timeline(selected_user, df)
        #plot

        # Apply improved layout
        fig = px.line(
            timeline,
            x='time',
            y='message',
            markers=True,
            title=f'Monthly Messages Timeline for {selected_user}',
            labels={'time': 'Time (Month-Year)', 'message': 'Number of Messages'},
            line_shape='spline',
        )

        fig.update_layout(
            title_font=dict(size=20, color='#223355', family='Segoe UI'),
            font=dict(size=14, color='#223355', family='Segoe UI'),

            xaxis=dict(
                title='Time (Month-Year)',
                tickangle=45,
                title_font=dict(size=16, color='#223355', family='Segoe UI'),
                tickfont=dict(size=12, color='#223355', family='Segoe UI'),
                linecolor='#223355',
                showgrid=False,
            ),
            yaxis=dict(
                title='Number of Messages',
                title_font=dict(size=16, color='#223355', family='Segoe UI'),
                tickfont=dict(size=12, color='#223355', family='Segoe UI'),
                linecolor='#223355',
                showgrid=True,
                gridcolor='#e0e0e0',
            ),
            plot_bgcolor='#ffffff',
            paper_bgcolor='#ffffff',
            hovermode='x unified',
            width=1000,
            height=500,
            margin=dict(l=40, r=40, t=60, b=120),
        )

        # Line and marker colors separated
        fig.update_traces(
            line=dict(color='#6A5ACD', width=3),  # Line in slate blue
            marker=dict(size=8, color='#FF6347')  # Markers in tomato orange
        )

        st.plotly_chart(fig, use_container_width=False)

    #Daily Timeline
        st.title("Daily Timeline")
        daily_timeline = helper.daily_timeline(selected_user, df)
        # plot

        # Apply improved layout
        fig = px.line(
            daily_timeline,
            x='only_date',
            y='message',
            markers=True,
            title=f'Daily Messages Timeline for {selected_user}',
            labels={'only_date': 'Time ', 'message': 'Number of Messages'},
            line_shape='spline',
        )

        fig.update_layout(
            title_font=dict(size=20, color='#223355', family='Segoe UI'),
            font=dict(size=14, color='#223355', family='Segoe UI'),

            xaxis=dict(
                title='Time ',
                tickangle=45,
                title_font=dict(size=16, color='#223355', family='Segoe UI'),
                tickfont=dict(size=12, color='#223355', family='Segoe UI'),
                linecolor='#223355',
                showgrid=False,
            ),
            yaxis=dict(
                title='Number of Messages',
                title_font=dict(size=16, color='#223355', family='Segoe UI'),
                tickfont=dict(size=12, color='#223355', family='Segoe UI'),
                linecolor='#223355',
                showgrid=True,
                gridcolor='#e0e0e0',
            ),
            plot_bgcolor='#ffffff',
            paper_bgcolor='#ffffff',
            hovermode='x unified',
            width=1000,
            height=500,
            margin=dict(l=40, r=40, t=60, b=120),
        )

        # Line and marker colors separated
        fig.update_traces(
            line=dict(color='#6A5ACD', width=3),  # Line in slate blue
            marker=dict(size=8, color='#FF6347')  # Markers in tomato orange
        )

        st.plotly_chart(fig, use_container_width=False)

    #-------------------------------------------------------------------
        #Week Activity Map

        st.title('Activity Map')
        col1, col2 = st.columns(2)

        #With Daily
        with col1:
            st.header('Most Busy Day')
            busy_day = helper.week_activity(selected_user, df)
            days_order = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday']
            # Reindex to maintain order, fill missing with 0
            busy_day = busy_day.reindex(days_order, fill_value=0)

            # Plotly chart
            fig = px.bar(
                x=busy_day.index,
                y=busy_day.values,
                labels={'x': 'Day of Week', 'y': 'Activity Count'},
                title=f'Weekly Activity Map for {selected_user}',
                color=busy_day.values,
                color_continuous_scale='Viridis'
            )
            st.plotly_chart(fig)

        #With Weekly
        with col2:
            st.header('Most Busy Month')
            busy_month = helper.month_activity(selected_user, df)
            month_order = ['January', 'February', 'March', 'April', 'May', 'June',
                           'July', 'August', 'September', 'October', 'November', 'December']
            # Reindex to maintain order, fill missing with 0
            busy_month = busy_month.reindex(month_order, fill_value=0)

            # Plotly chart
            fig = px.bar(
                x=busy_month.index,
                y=busy_month.values,
                labels={'x': 'Month', 'y': 'Activity Count'},
                title=f'Weekly Activity Map for {selected_user}',
                color=busy_month.values,
                color_continuous_scale='Viridis'
            )
            st.plotly_chart(fig)

        #-----------------------------------------------------

    #Hourly Chat Activity
        st.header('Hourly Chat Activity')
        heatmap_data = helper.activity_heatmap_period(selected_user, df)
        fig, ax = plt.subplots(figsize=(16, 6))
        # heatmap
        sns.heatmap(
            heatmap_data,
            cmap='magma',
            linewidths=0.3,
            linecolor='black',
            cbar=True,
            square=False,
            xticklabels=True,
            yticklabels=True,
            ax=ax
        )

        ax.set_title(f'Heatmap of Chat Activity – {selected_user}', fontsize=16, pad=20)
        ax.set_xlabel('Hour of Day ', fontsize=12)
        ax.set_ylabel('Day of Week', fontsize=12)

        ax.set_xticklabels(ax.get_xticklabels(), rotation=45, ha='right', fontsize=10)
        ax.set_yticklabels(ax.get_yticklabels(), rotation=0, fontsize=10)

        plt.tight_layout() #adjusts the spacing between subplots and plot elements like labels etc. to make sure nothing overlaps or gets cut off.


        st.pyplot(fig)
    # -------------------------------------
        # Most busy users
        if selected_user=='Overall':
            st.title("Most Busy Users")
            x,new_df=helper.most_busy_users(df)

            col1, col2 = st.columns(2)

            with col1:
                # df = x.reset_index()
                # df.columns = ['User', 'Messages']
                #
                # fig = px.bar(
                #     df,
                #     x='User',
                #     y='Messages',
                #     color='Messages',
                #     color_continuous_scale='Blues',
                #     labels={'User': 'User', 'Messages': 'Messages'},
                #     title="Top 10 Most Active Users"
                # )
                # st.plotly_chart(fig)

                df_top_users = pd.DataFrame({'User': x.index, 'Messages': x.values})

                # Improved Plotly Bar Chart
                fig = px.bar(
                    df_top_users,
                    x='User',
                    y='Messages',
                    color='Messages',
                    color_continuous_scale='Agsunset',  # Other good ones: 'Plasma', 'Viridis', 'Cividis', 'Agsunset'
                    title='🌟 Top 10 Most Active Users',
                    text='Messages'  # Display message counts on bars
                )
                # Show chart in Streamlit
                st.plotly_chart(fig)

            with col2:
                # Display the DataFrame of user % contribution
                st.dataframe(new_df)


        #WordCloud Image
        st.header("WordCloud")
        wc_img=helper.create_wordcloud(selected_user, df)

        if wc_img is None:
            st.warning("No words found for the selected user to generate a word cloud.")
        else:
            fig, ax = plt.subplots(figsize=(10, 5))
            ax.imshow(wc_img, interpolation='bilinear')
            ax.axis("off")
            st.pyplot(fig)

        #Count most common words
        st.title("Word Analysis")
        col1, col2 = st.columns(2)
        most_common_df=helper.most_common_words(selected_user, df)
        with col1:
            st.dataframe(most_common_df)
        with col2:
            # Plotly horizontal bar chart
            most_common_df.columns = ['Word', 'Count']  # Rename columns for clarity

            fig = px.bar(
                most_common_df,
                x='Count',
                y='Word',
                orientation='h',
                title=f"Most Common Words Used by {'All Users' if selected_user == 'Overall' else selected_user}",
                color='Count',
                color_continuous_scale='Blues'
            )

            fig.update_layout(
                yaxis=dict(autorange="reversed"),  # So most frequent word is at top
                xaxis_title="Frequency",
                yaxis_title="Words",
                title_x=0.5,
                plot_bgcolor='rgba(0,0,0,0)',
                paper_bgcolor='rgba(0,0,0,0)'
            )

            st.plotly_chart(fig, use_container_width=True)

    #----------------------------------------------------

        emoji_df=helper.emoji_count(selected_user, df)
        st.title("Emoji Analysis")
        col1, col2 = st.columns(2)
        with col1:
            st.subheader("Emoji Data")
            st.dataframe(emoji_df)

        with col2:
            st.subheader("Emoji Distribution")

            if not emoji_df.empty:
                emoji_df.columns = ['Emoji', 'Count']  # Rename for clarity

                fig = px.pie(
                    emoji_df.head(15),
                    values='Count',
                    names='Emoji',
                    title=f"Top Emoji Usage by {'All Users' if selected_user == 'Overall' else selected_user}",
                    color_discrete_sequence=px.colors.sequential.RdBu
                )

                fig.update_traces(textposition='inside', textinfo='percent+label')
                fig.update_layout(
                    showlegend=True,
                    title_x=0.5,
                    margin=dict(t=40, b=0, l=0, r=0),
                )

                st.plotly_chart(fig, use_container_width=True)
            else:
                st.info("No emojis found to display.")

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 8501))
    args = [
        "streamlit",
        "run",
        sys.argv[0],
        f"--server.port={port}",
        "--server.enableCORS=false",
        "--server.enableXsrfProtection=false"
    ]
    # This replaces the current process with Streamlit, avoiding warnings
    os.execvp("streamlit", args)



