# ------------------------------
                    # Links
                    # ------------------------------

                    if game.get("spreadsheet_url"):

                        btn_col, copy_col = st.columns([5, 1])

                        with btn_col:
                            st.link_button(
                                "📊 Spreadsheet",
                                game["spreadsheet_url"],
                                use_container_width=True
                            )

                        with copy_col:
                            direct_url = f"https://solo-tracker.streamlit.app/?record_play={game['id']}"
                            
                            st.components.v1.html(f"""
                                <div style="display: flex; align-items: center; justify-content: center; margin: 0; padding: 0;">
                                    <button onclick="navigator.clipboard.writeText('{direct_url}'); this.innerText='✅';" title="Copy Direct Record Play Link" style="
                                        width: 100%;
                                        height: 38px;
                                        background-color: rgb(255, 255, 255);
                                        border: 1px solid rgba(49, 51, 63, 0.2);
                                        border-radius: 4px;
                                        cursor: pointer;
                                        font-size: 1rem;
                                        display: flex;
                                        align-items: center;
                                        justify-content: center;
                                        transition: background-color 0.2s;
                                    ">📋</button>
                                </div>
                            """, height=38)

                    if game.get("bgg_url"):

                        st.link_button(
                            "🎲 BoardGameGeek",
                            game["bgg_url"],
                            use_container_width=True
                        )
