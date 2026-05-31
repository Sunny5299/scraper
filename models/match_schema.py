from datetime import datetime

def match_schema():
    return {
        "match_id": None,
        "match_url": "",
        "match_date": None,
        "status": "",  # UPCOMING, LIVE, COMPLETED

        # Match Info Tab
        "match_info": {
            "series": "",
            "match_type": "",
            "venue": "",
            "team1": "",
            "team2": "",
            "toss": "",
            "umpires": [],
            "third_umpire": "",
            "match_referee": "",
            "weather": "",

            "last_five_matches": {
                "team1": [],
                "team2": []
            },

            "team1_vs_team2_Hd2Hd": {
                "team1_win": "",
                "team2_win": "",
                "team1_score": [
                    {
                        "score": "",
                        "over": ""
                    }
                ],
                "team2_score": [
                    {
                        "score": "",
                        "over": ""
                    }
                ],
                "win_record": []
            },

            "comparison_VS_allteam": {
                "team1": {
                    "match_played": "",
                    "win_percentage": "",
                    "avg_score": "",
                    "highest_score": "",
                    "lowest_score": ""
                },
                "team2": {
                    "match_played": "",
                    "win_percentage": "",
                    "avg_score": "",
                    "highest_score": "",
                    "lowest_score": ""
                }
            }
        },

        # Squads Tab
        "squads": {
            "team1_players": [],
            "team2_players": []
        },

        # Live Tab
        "live": {
            "current_score": "",
            "overs": "",
            "current_batsmen": [],
            "current_bowlers": [],
            "commentary": []
        },

        # Scorecard Tab
        "scorecard": {
            "innings": [
                {
                    "team_name": "",

                    "batting": [
                        {
                            "batsman_name": "",
                            "run": "",
                            "ball": "",
                            "fours": "",
                            "sixes": "",
                            "strike_rate": "",
                            "ball_by": "",
                            "out_by": "",
                            "extras": []
                        }
                    ],

                    "bowling": [
                        {
                            "bowler_name": "",
                            "over": "",
                            "maiden": "",
                            "run": "",
                            "wkt": "",
                            "economy": ""
                        }
                    ],

                    "fall_of_wkt": [
                        {
                            "batsman": "",
                            "score": "",
                            "overs": ""
                        }
                    ],

                    "partnership": [
                        {
                            "wkt": "",
                            "batter_1": "",
                            "batter_1_run": "",
                            "batter_1_ball": "",
                            "batter_2": "",
                            "batter_2_run": "",
                            "batter_2_ball": "",
                            "total_run_partner": "",
                            "total_ball_play_partner": ""
                        }
                    ]
                }
            ]
        },

        "created_at": datetime.utcnow(),
        "updated_at": datetime.utcnow()
    }